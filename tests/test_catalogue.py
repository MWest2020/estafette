from __future__ import annotations

import yaml

from estafette.catalogue import generate_site
from estafette.report import (
    ReportCheck,
    ReportCriterion,
    ReportSilver,
    TransferabilityReport,
)


def _entry(cat, name, kind="findings", conclusion="learned X", assessment=None):
    d = {"name": name, "owner": "o", "contact": "c", "status": "poc",
         "kind": kind, "conclusion": conclusion}
    if assessment:
        d["assessment"] = assessment
    (cat / f"{name}.yaml").write_text(yaml.safe_dump(d), encoding="utf-8")


def _write_report(base, rel, bronze=True):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    report = TransferabilityReport(
        estafette_version="0.1.0", tier_doc_version="1.0", commit="abc123",
        manifest={"name": "x", "licence": "MIT", "owner": "o", "contact": "c", "status": "poc"},
        tool_versions={}, bronze=bronze,
        criteria=[ReportCriterion(id="B1", title="REUSE-compliant", passed=bronze)],
        checks=[ReportCheck(name="reuse", status="pass" if bronze else "fail", gaps=[])],
        silver_preview=ReportSilver(available=False, reason="no build recipe"),
    )
    p.write_text(report.model_dump_json(), encoding="utf-8")


def test_index_lists_all_entries_with_conclusions(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    _entry(cat, "Alpha", kind="findings", conclusion="alpha conclusion")
    _entry(cat, "Beta", kind="code", assessment="reports/beta/report.json")
    _write_report(tmp_path, "reports/beta/report.json", bronze=True)
    count, index = generate_site(cat, tmp_path / "site", base=tmp_path)
    assert count == 2
    html = index.read_text("utf-8")
    assert "Alpha" in html and "Beta" in html
    assert "alpha conclusion" in html
    assert "bronze" in html  # Beta carries an assessment


def test_findings_only_has_no_verdict_badge(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    _entry(cat, "Findy", kind="findings", conclusion="just findings, no code")
    _, index = generate_site(cat, tmp_path / "site", base=tmp_path)
    html = index.read_text("utf-8")
    assert "just findings, no code" in html
    assert "bronze" not in html


def test_site_is_deterministic(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    _entry(cat, "Alpha", conclusion="c1")
    _entry(cat, "Beta", conclusion="c2")
    a = generate_site(cat, tmp_path / "s1", base=tmp_path)[1].read_text("utf-8")
    b = generate_site(cat, tmp_path / "s2", base=tmp_path)[1].read_text("utf-8")
    assert a == b


def test_empty_catalog(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    count, index = generate_site(cat, tmp_path / "site", base=tmp_path)
    assert count == 0
    assert "No entries yet" in index.read_text("utf-8")


def test_detail_page_shows_full_conclusion(tmp_path):
    cat = tmp_path / "catalog"
    cat.mkdir()
    _entry(cat, "Alpha", conclusion="the full conclusion text")
    generate_site(cat, tmp_path / "site", base=tmp_path)
    detail = (tmp_path / "site" / "alpha.html").read_text("utf-8")
    assert "the full conclusion text" in detail
