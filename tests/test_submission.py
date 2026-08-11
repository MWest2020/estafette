"""submission-v1: strict validation (CI gate), harvester, and local+harvested merge.

Network is never hit: the harvester's ``_fetch`` is monkeypatched with canned
bytes so every case is deterministic and offline.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from estafette import harvest as harvest_mod
from estafette.entry import EntryError, load_merged_entries, validate_entries
from estafette.harvest import Source, harvest, load_sources

_VALID_POC = {
    "name": "Alpha",
    "owner": "Org",
    "contact": "a@org",
    "status": "poc",
    "kind": "findings",
    "conclusion": "Alpha works",
}


def _write(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


# --- 1. strict validation (PR-submission CI gate) ---

def test_validate_entries_passes_and_counts(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    _write(cat / "alpha.yaml", _VALID_POC)
    _write(cat / "beta.yaml", {**_VALID_POC, "name": "Beta"})
    assert validate_entries(cat) == 2


def test_validate_entries_fails_naming_the_file(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    _write(cat / "bad.yaml", {**_VALID_POC, "conclusion": ""})  # empty conclusion
    with pytest.raises(EntryError) as exc:
        validate_entries(cat)
    assert "bad.yaml" in str(exc.value)


def test_validate_entries_missing_dir_is_zero(tmp_path):
    assert validate_entries(tmp_path / "nope") == 0


# --- 2. source list + harvester ---

def test_load_sources_accepts_strings_and_dicts_sorted(tmp_path):
    p = tmp_path / "sources.yaml"
    p.write_text(
        "sources:\n  - https://raw/b/HEAD\n  - repo: https://raw/a/HEAD\n", encoding="utf-8"
    )
    srcs = load_sources(p)
    assert [s.repo for s in srcs] == ["https://raw/a/HEAD", "https://raw/b/HEAD"]


def test_load_sources_missing_file_is_non_fatal(tmp_path):
    assert load_sources(tmp_path / "absent.yaml") == []


def test_load_sources_malformed_raises_actionable(tmp_path):
    p = tmp_path / "sources.yaml"
    p.write_text("sources:\n  - 123\n  - repo: 456\n", encoding="utf-8")
    # 123 -> {"repo": 123} but repo must be a str >=1; item #1 invalid
    with pytest.raises(ValueError) as exc:
        load_sources(p)
    assert "source #" in str(exc.value)


def _fake_fetch(mapping: dict[str, bytes]):
    def _fetch(url: str) -> bytes | None:
        return mapping.get(url)
    return _fetch


def test_harvest_poc_yaml(tmp_path, monkeypatch):
    src = Source(repo="https://raw/org/alpha/HEAD")
    mapping = {"https://raw/org/alpha/HEAD/poc.yaml": yaml.safe_dump(_VALID_POC).encode()}
    monkeypatch.setattr(harvest_mod, "_fetch", _fake_fetch(mapping))
    result = harvest([src], tmp_path / "out")
    assert [e.name for e in result.entries] == ["Alpha"]
    assert not result.skipped


def test_harvest_publiccode_fallback_wraps_as_code(tmp_path, monkeypatch):
    src = Source(repo="https://raw/org/widget/HEAD")
    pub = textwrap.dedent(
        """
        name: Widget
        url: https://github.com/org/widget
        developmentStatus: stable
        description:
          en:
            shortDescription: A widget that widgets.
        maintenance:
          contacts:
            - name: Jane
              email: jane@example.org
        """
    ).encode()
    mapping = {"https://raw/org/widget/HEAD/publiccode.yml": pub}  # no poc.yaml
    monkeypatch.setattr(harvest_mod, "_fetch", _fake_fetch(mapping))
    result = harvest([src], tmp_path / "out")
    assert len(result.entries) == 1
    e = result.entries[0]
    assert e.name == "Widget" and e.kind.value == "code" and e.status.value == "stable"
    assert e.contact == "jane@example.org"
    assert "auto-derived" in e.conclusion


def test_harvest_one_failing_source_skips_others_survive(tmp_path, monkeypatch):
    ok = Source(repo="https://raw/org/alpha/HEAD")
    bad = Source(repo="https://raw/org/ghost/HEAD")  # nothing in the mapping -> 404
    mapping = {"https://raw/org/alpha/HEAD/poc.yaml": yaml.safe_dump(_VALID_POC).encode()}
    monkeypatch.setattr(harvest_mod, "_fetch", _fake_fetch(mapping))
    result = harvest([ok, bad], tmp_path / "out")
    assert [e.name for e in result.entries] == ["Alpha"]
    assert len(result.skipped) == 1 and "ghost" in result.skipped[0]
    assert "harvested 1 of 2" in result.summary


def test_harvest_invalid_poc_is_skipped_with_reason(tmp_path, monkeypatch):
    src = Source(repo="https://raw/org/broken/HEAD")
    mapping = {"https://raw/org/broken/HEAD/poc.yaml": b"name: X\nconclusion: ''\n"}  # invalid
    monkeypatch.setattr(harvest_mod, "_fetch", _fake_fetch(mapping))
    result = harvest([src], tmp_path / "out")
    assert not result.entries and "invalid poc.yaml" in result.skipped[0]


def test_fetch_rejects_non_https_schemes(tmp_path):
    """SSRF guard: file://, http://, ftp://, data: are refused before any read."""
    probe = tmp_path / "secret.txt"
    probe.write_text("SECRET", encoding="utf-8")
    assert harvest_mod._fetch(f"file://{probe}") is None
    assert harvest_mod._fetch("http://169.254.169.254/latest/meta-data/") is None
    assert harvest_mod._fetch("ftp://example.org/x") is None


def test_harvest_strips_assessment_from_remote_entry(tmp_path, monkeypatch):
    """A harvested poc.yaml must not carry a local `assessment` path (arbitrary
    file-read guard in generate_site)."""
    src = Source(repo="https://raw/org/alpha/HEAD")
    poc = {**_VALID_POC, "assessment": "../../../../etc/passwd"}
    mapping = {"https://raw/org/alpha/HEAD/poc.yaml": yaml.safe_dump(poc).encode()}
    monkeypatch.setattr(harvest_mod, "_fetch", _fake_fetch(mapping))
    result = harvest([src], tmp_path / "out")
    assert result.entries and result.entries[0].assessment is None


def test_harvest_slug_collision_does_not_clobber(tmp_path, monkeypatch):
    """Distinct names that slugify identically get distinct files (no data loss)."""
    a = Source(repo="https://raw/org/a/HEAD")
    b = Source(repo="https://raw/org/b/HEAD")

    def _poc(name: str) -> bytes:
        return yaml.safe_dump({**_VALID_POC, "name": name}).encode()

    mapping = {
        "https://raw/org/a/HEAD/poc.yaml": _poc("My PoC"),  # both slugify to "my-poc"
        "https://raw/org/b/HEAD/poc.yaml": _poc("my-poc"),
    }
    monkeypatch.setattr(harvest_mod, "_fetch", _fake_fetch(mapping))
    out = tmp_path / "out"
    result = harvest([a, b], out)
    assert len(result.entries) == 2
    assert len(list(out.glob("*.yaml"))) == 2  # both persisted, neither overwritten


def test_harvest_is_byte_identical_across_runs(tmp_path, monkeypatch):
    src = Source(repo="https://raw/org/alpha/HEAD")
    mapping = {"https://raw/org/alpha/HEAD/poc.yaml": yaml.safe_dump(_VALID_POC).encode()}
    monkeypatch.setattr(harvest_mod, "_fetch", _fake_fetch(mapping))
    harvest([src], tmp_path / "a")
    harvest([src], tmp_path / "b")
    a = (tmp_path / "a" / "alpha.yaml").read_bytes()
    b = (tmp_path / "b" / "alpha.yaml").read_bytes()
    assert a == b


# --- 3. merge into the loader ---

def test_merge_local_and_harvested(tmp_path):
    cat = tmp_path / "catalog"
    (cat / ".harvested").mkdir(parents=True)
    _write(cat / "alpha.yaml", _VALID_POC)
    _write(cat / ".harvested" / "beta.yaml", {**_VALID_POC, "name": "Beta"})
    names = [e.name for e in load_merged_entries(cat)]
    assert names == ["Alpha", "Beta"]


def test_merge_local_wins_name_collision(tmp_path):
    cat = tmp_path / "catalog"
    (cat / ".harvested").mkdir(parents=True)
    _write(cat / "alpha.yaml", {**_VALID_POC, "conclusion": "LOCAL wins"})
    _write(cat / ".harvested" / "alpha.yaml", {**_VALID_POC, "conclusion": "harvested loses"})
    entries = load_merged_entries(cat)
    assert len(entries) == 1
    assert entries[0].conclusion == "LOCAL wins"


def test_merge_skips_unparseable_on_either_side(tmp_path):
    cat = tmp_path / "catalog"
    (cat / ".harvested").mkdir(parents=True)
    _write(cat / "good.yaml", _VALID_POC)
    (cat / ".harvested" / "junk.yaml").write_text("{ not: valid: yaml ]", encoding="utf-8")
    names = [e.name for e in load_merged_entries(cat)]
    assert names == ["Alpha"]
