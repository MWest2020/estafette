"""PoC entry — the unit of the catalogue (platform-first reframe).

Wraps publiccode.yml by reference rather than duplicating it (invariant I2):
publiccode.yml is software-only, has no `poc` status and no conclusion field, so
a PoC entry adds exactly what it lacks — `kind` and `conclusion` — and points at
a real publiccode.yml (for code) and an estafette assessment (for the verdict).
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from estafette.manifest import Status


class Kind(StrEnum):
    code = "code"
    findings = "findings"
    both = "both"


class PoCEntry(BaseModel):
    """A shareable proof of concept: code, findings, or both."""

    name: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    contact: str = Field(min_length=1)
    status: Status
    kind: Kind
    conclusion: str = Field(min_length=1)  # the star — the PoC's takeaway
    repo: str | None = None
    doc: str | None = None
    demo: str | None = None
    publiccode: str | None = None  # reference to a real publiccode.yml (software)
    assessment: str | None = None  # reference to an estafette report.json (verdict)


class EntryError(ValueError):
    """A catalog entry failed strict validation (naming the file + reason)."""


def load_entries(catalog_dir: Path) -> list[PoCEntry]:
    """Load PoC entries from ``*.yaml`` under ``catalog_dir``, skipping bad ones."""
    entries: list[PoCEntry] = []
    if not catalog_dir.is_dir():
        return entries
    for path in sorted(catalog_dir.glob("*.yaml")):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            entries.append(PoCEntry.model_validate(raw))
        except (yaml.YAMLError, ValueError, OSError, ValidationError):
            continue
    return sorted(entries, key=lambda e: e.name)


def validate_entries(catalog_dir: Path) -> int:
    """Strictly load ``catalog_dir/*.yaml``; raise ``EntryError`` naming the first
    invalid file + reason. Returns the count when all are valid (the CI gate)."""
    if not catalog_dir.is_dir():
        return 0
    count = 0
    for path in sorted(catalog_dir.glob("*.yaml")):
        try:
            PoCEntry.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        except (yaml.YAMLError, ValueError, OSError, ValidationError) as exc:
            raise EntryError(f"{path}: {exc}") from exc
        count += 1
    return count


def load_merged_entries(catalog_dir: Path) -> list[PoCEntry]:
    """Local ``catalog/*.yaml`` merged with harvested ``catalog/.harvested/*.yaml``.

    One deterministic set; the local entry wins on a name collision (a curated
    local entry always beats an auto-harvested one). Both sides stay lenient —
    an unparseable file on either side is skipped, never fatal (I3)."""
    merged: dict[str, PoCEntry] = {}
    for entry in load_entries(catalog_dir / ".harvested"):  # harvested first ...
        merged[entry.name] = entry
    for entry in load_entries(catalog_dir):  # ... local overwrites (wins collision)
        merged[entry.name] = entry
    return sorted(merged.values(), key=lambda e: e.name)
