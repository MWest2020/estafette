from __future__ import annotations

from pathlib import Path

from estafette.catalogue import generate_site, load_reports
from estafette.report import (
    ReportCheck,
    ReportCriterion,
    ReportGap,
    ReportSilver,
    TransferabilityReport,
)


def _report(name: str, commit: str, bronze: bool = True) -> TransferabilityReport:
    return TransferabilityReport(
        estafette_version="0.1.0",
        tier_doc_version="1.0",
        commit=commit,
        manifest={"name": name, "licence": "MIT", "owner": "o", "contact": "c", "status": "poc"},
        tool_versions={"reuse": "6.2.0"},
        bronze=bronze,
        criteria=[ReportCriterion(id="B1", title="REUSE-compliant", passed=bronze)],
        checks=[
            ReportCheck(
                name="reuse",
                status="pass" if bronze else "fail",
                gaps=[] if bronze else [ReportGap(message="gap", remediation="fix")],
            )
        ],
        silver_preview=ReportSilver(available=False, reason="no build recipe"),
    )


def _write(reports: Path, name: str, commit: str, bronze: bool = True) -> None:
    d = reports / commit
    d.mkdir(parents=True)
    body = _report(name, commit, bronze).model_dump_json()
    (d / "report.json").write_text(body, encoding="utf-8")


def test_index_lists_pocs_and_detail_pages(tmp_path):
    reports = tmp_path / "reports"
    _write(reports, "Alpha", "aaaaaaaaaaaa", bronze=True)
    _write(reports, "Beta", "bbbbbbbbbbbb", bronze=False)
    count, index = generate_site(reports, tmp_path / "site")
    assert count == 2
    html = index.read_text(encoding="utf-8")
    assert "Alpha" in html and "Beta" in html
    assert "bronze" in html and "not bronze" in html
    # a detail page exists per report
    assert (tmp_path / "site" / "alpha-aaaaaaaaaaaa.html").exists()
    assert (tmp_path / "site" / "beta-bbbbbbbbbbbb.html").exists()


def test_site_is_deterministic(tmp_path):
    reports = tmp_path / "reports"
    _write(reports, "Alpha", "aaaaaaaaaaaa")
    _write(reports, "Beta", "bbbbbbbbbbbb")
    first = generate_site(reports, tmp_path / "s1")[1].read_text(encoding="utf-8")
    second = generate_site(reports, tmp_path / "s2")[1].read_text(encoding="utf-8")
    assert first == second


def test_empty_reports_dir(tmp_path):
    count, index = generate_site(tmp_path / "nope", tmp_path / "site")
    assert count == 0
    assert "No reports yet" in index.read_text(encoding="utf-8")


def test_names_are_html_escaped(tmp_path):
    reports = tmp_path / "reports"
    _write(reports, "<b>x</b>", "cccccccccccc")
    _, index = generate_site(reports, tmp_path / "site")
    html = index.read_text(encoding="utf-8")
    assert "<b>x</b>" not in html
    assert "&lt;b&gt;" in html


def test_load_reports_skips_unparseable(tmp_path):
    reports = tmp_path / "reports"
    _write(reports, "Good", "dddddddddddd")
    bad = reports / "bad"
    bad.mkdir(parents=True)
    (bad / "report.json").write_text("{ not valid json", encoding="utf-8")
    loaded = load_reports(reports)
    assert [r.manifest["name"] for r in loaded] == ["Good"]
