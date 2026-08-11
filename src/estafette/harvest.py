"""Harvest PoC entries from remote repos — the crawl on-ramp.

Reads a ``sources.yaml`` repo list, fetches each repo's well-known ``poc.yaml``
(``publiccode.yml`` fallback, wrapped as ``kind=code``), and writes normalised
``PoCEntry`` YAML into the harvested dir the loader reads. Network fetch lives
ONLY here (a CLI/CI step), never on the verdict path (I6). Deterministic (I5):
sorted order, failures skipped with a reason, no timestamps/abs paths in output.
"""

from __future__ import annotations

import hashlib
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from estafette.entry import Kind, PoCEntry
from estafette.manifest import Status

_MAX_BYTES = 512 * 1024  # per-fetch size cap (a few hundred KB is plenty)
_TIMEOUT = 10  # seconds per fetch
_POC_FILE = "poc.yaml"
_PUBLICCODE_FILE = "publiccode.yml"
# publiccode developmentStatus -> our Status (publiccode has no "poc").
_PUBLICCODE_STATUS = {"concept": "concept", "development": "poc", "beta": "beta",
                      "stable": "stable", "obsolete": "obsolete"}


class Source(BaseModel):
    """A repo to harvest: the raw base URL its well-known files live under, e.g.
    ``https://raw.githubusercontent.com/<org>/<repo>/HEAD``. A repo list, not a
    file list — the harvester appends ``/poc.yaml`` by convention (I2)."""

    repo: str = Field(min_length=1)


@dataclass
class HarvestResult:
    entries: list[PoCEntry] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # "repo: reason"

    @property
    def summary(self) -> str:
        total = len(self.entries) + len(self.skipped)
        line = f"harvested {len(self.entries)} of {total} sources"
        if self.skipped:
            line += f"; skipped {len(self.skipped)}: " + "; ".join(self.skipped)
        return line


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "entry"


def load_sources(path: Path) -> list[Source]:
    """Parse ``sources.yaml`` into a sorted list of repos. Accepts a bare list or
    a ``sources:`` mapping; each item is a repo URL string or ``{repo: url}``.
    Missing file → empty (non-fatal, I3); malformed → ``ValueError`` (actionable)."""
    if not path.is_file():
        return []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if raw is None:
        return []
    items = raw.get("sources", []) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError(f"{path}: expected a list of repos (or a 'sources:' list)")
    sources: list[Source] = []
    for i, item in enumerate(items, start=1):
        try:
            sources.append(Source.model_validate({"repo": item} if isinstance(item, str) else item))
        except (ValidationError, TypeError) as exc:
            raise ValueError(f"{path}: source #{i} invalid: {exc}") from exc
    return sorted(sources, key=lambda s: s.repo)


class _HTTPSOnlyRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse any redirect that leaves https — no SSRF pivot to file/ftp/http/internal."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, PLR0913
        if not newurl.lower().startswith("https://"):
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


# https-only redirect handler + scheme guard in _fetch enforce "https only"
# instead of merely asserting it (no file://, ftp://, data://, http://).
_OPENER = urllib.request.build_opener(_HTTPSOnlyRedirect)


def _fetch(url: str) -> bytes | None:
    """https-only GET (rejects non-https schemes + non-https redirects: no file://,
    internal-host, or metadata pivot). Returns <=_MAX_BYTES+1 bytes, None on failure."""
    if not url.lower().startswith("https://"):
        return None
    req = urllib.request.Request(url, headers={"User-Agent": "estafette-harvest"})
    try:
        with _OPENER.open(req, timeout=_TIMEOUT) as resp:  # noqa: S310 (https enforced above)
            return resp.read(_MAX_BYTES + 1)
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _wrap_publiccode(raw: object, src: Source) -> PoCEntry:
    """Map a publiccode.yml mapping into a PoCEntry(kind=code), auto-derived (I2)."""
    if not isinstance(raw, dict):
        raise ValueError("publiccode.yml is not a mapping")
    name = str(raw.get("name") or src.repo)
    repo = str(raw.get("url") or src.repo)
    desc = ""
    description = raw.get("description")
    if isinstance(description, dict):
        for lang in sorted(description):
            block = description[lang]
            if isinstance(block, dict) and block.get("shortDescription"):
                desc = str(block["shortDescription"])
                break
    contact = "unknown"
    maintenance = raw.get("maintenance")
    if isinstance(maintenance, dict):
        contacts = maintenance.get("contacts")
        if isinstance(contacts, list) and contacts and isinstance(contacts[0], dict):
            contact = str(contacts[0].get("email") or contacts[0].get("name") or "unknown")
    ds = str(raw.get("developmentStatus", "")).lower()
    status = Status(_PUBLICCODE_STATUS.get(ds, "concept"))
    return PoCEntry(
        name=name,
        owner=name,
        contact=contact,
        status=status,
        kind=Kind.code,
        conclusion=f"[auto-derived from publiccode.yml] {desc or 'no description provided'}",
        repo=repo,
        publiccode=f"{src.repo.rstrip('/')}/{_PUBLICCODE_FILE}",
    )


def _entry_from_source(src: Source) -> tuple[PoCEntry | None, str | None]:
    """Fetch one repo → (entry, None) or (None, skip-reason). Never raises on a
    bad remote: poc.yaml first, publiccode.yml as fallback."""
    base = src.repo.rstrip("/")
    data = _fetch(f"{base}/{_POC_FILE}")
    if data is not None:
        if len(data) > _MAX_BYTES:
            return None, f"{src.repo}: {_POC_FILE} exceeds size cap"
        try:
            entry = PoCEntry.model_validate(yaml.safe_load(data.decode("utf-8")))
        except (yaml.YAMLError, ValueError, ValidationError, UnicodeDecodeError) as exc:
            return None, f"{src.repo}: invalid {_POC_FILE} ({exc.__class__.__name__})"
        # Drop any LOCAL assessment path: it is read repo-relative in generate_site,
        # so a remote-controlled value would drive an arbitrary local read (harvested
        # PoCs aren't locally assessable — they render "no verdict").
        return entry.model_copy(update={"assessment": None}), None
    data = _fetch(f"{base}/{_PUBLICCODE_FILE}")
    if data is None:
        return None, f"{src.repo}: no {_POC_FILE} or {_PUBLICCODE_FILE}"
    if len(data) > _MAX_BYTES:
        return None, f"{src.repo}: {_PUBLICCODE_FILE} exceeds size cap"
    try:
        return _wrap_publiccode(yaml.safe_load(data.decode("utf-8")), src), None
    except (yaml.YAMLError, ValueError, ValidationError, UnicodeDecodeError) as exc:
        return None, f"{src.repo}: invalid {_PUBLICCODE_FILE} ({exc.__class__.__name__})"


def harvest(sources: list[Source], out_dir: Path) -> HarvestResult:
    """Fetch every source, aggregate deterministically, write normalised YAML."""
    result = HarvestResult()
    for src in sorted(sources, key=lambda s: s.repo):
        entry, reason = _entry_from_source(src)
        if entry is None:
            result.skipped.append(reason or f"{src.repo}: unknown error")
        else:
            result.entries.append(entry)
    result.entries.sort(key=lambda e: e.name)
    _write_harvested(result.entries, out_dir)
    return result


def _write_harvested(entries: list[PoCEntry], out_dir: Path) -> None:
    """Write one normalised YAML per entry; clears stale files first (determinism)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*.yaml"):
        stale.unlink()
    used: set[str] = set()
    for entry in entries:
        slug = _slug(entry.name)
        if slug in used:  # distinct names, same slug -> disambiguate, never clobber
            slug = f"{slug}-{hashlib.sha1(entry.name.encode('utf-8')).hexdigest()[:8]}"
        used.add(slug)
        data = entry.model_dump(exclude_none=True, mode="json")
        (out_dir / f"{slug}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=True, allow_unicode=True), encoding="utf-8"
        )
