from __future__ import annotations

import pytest
import yaml
from pydantic import ValidationError

from estafette.entry import Kind, PoCEntry, load_entries


def _base(**over) -> dict:
    d = {
        "name": "X", "owner": "o", "contact": "c",
        "status": "poc", "kind": "findings", "conclusion": "we learned Y",
    }
    d.update(over)
    return d


def test_findings_only_entry_is_valid():
    entry = PoCEntry.model_validate(_base())
    assert entry.kind is Kind.findings
    assert entry.repo is None and entry.assessment is None


def test_code_entry_with_refs_is_valid():
    entry = PoCEntry.model_validate(
        _base(kind="code", repo="https://x", assessment="reports/a/report.json")
    )
    assert entry.kind is Kind.code
    assert entry.assessment == "reports/a/report.json"


def test_missing_conclusion_rejected():
    d = _base()
    del d["conclusion"]
    with pytest.raises(ValidationError):
        PoCEntry.model_validate(d)


def test_empty_conclusion_rejected():
    with pytest.raises(ValidationError):
        PoCEntry.model_validate(_base(conclusion=""))


def test_invalid_kind_rejected():
    with pytest.raises(ValidationError):
        PoCEntry.model_validate(_base(kind="prototype"))


def test_load_entries_skips_unparseable_and_sorts(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    (cat / "b.yaml").write_text(yaml.safe_dump(_base(name="Beta")), encoding="utf-8")
    (cat / "a.yaml").write_text(yaml.safe_dump(_base(name="Alpha")), encoding="utf-8")
    (cat / "bad.yaml").write_text("{ not valid yaml", encoding="utf-8")
    assert [e.name for e in load_entries(cat)] == ["Alpha", "Beta"]
