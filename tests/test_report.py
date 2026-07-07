from __future__ import annotations

import json
from pathlib import Path

from estafette.checks.build import SilverPreview
from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.manifest import TransferManifest
from estafette.report import (
    COMMIT_UNAVAILABLE,
    build_report,
    capture_commit,
    render_json,
    render_markdown,
    write_report,
)
from estafette.tier import compute_bronze


def _manifest() -> TransferManifest:
    return TransferManifest(name="Demo", licence="MIT", owner="o", contact="c", status="poc")


def _results(target: Path) -> list[tuple[str, CheckResult]]:
    # a reuse gap carrying an absolute path, to exercise relativisation
    reuse = CheckResult(
        CheckStatus.failed,
        [Gap(message=f"{target}/code.py lacks info", remediation="add header")],
        {"tool": "reuse", "version": "6.2.0"},
    )
    ok = CheckResult(CheckStatus.passed, [], {"tool": "syft", "version": "1.46.0"})
    return [("reuse", reuse), ("licence_consistency", ok)]


def _build(target: Path):
    manifest = _manifest()
    results = _results(target)
    verdict = compute_bronze(results, manifest)
    silver = SilverPreview(available=False, reason="no build recipe declared in the manifest")
    return build_report(target, manifest, results, verdict, silver, "0.1.0", "abc123def456")


def test_absolute_paths_are_relativised(tmp_path):
    report = _build(tmp_path)
    blob = render_json(report)
    assert str(tmp_path) not in blob  # target prefix stripped
    assert "./code.py lacks info" in blob


def test_body_is_deterministic(tmp_path):
    a = render_json(_build(tmp_path))
    b = render_json(_build(tmp_path))
    assert a == b
    # markdown too
    assert render_markdown(_build(tmp_path)) == render_markdown(_build(tmp_path))


def test_json_has_verdict_and_provenance(tmp_path):
    data = json.loads(render_json(_build(tmp_path)))
    assert data["commit"] == "abc123def456"
    assert data["tool_versions"]["reuse"] == "6.2.0"
    assert data["bronze"] is False
    assert data["estafette_version"] == "0.1.0"


def test_capture_commit_non_git(tmp_path):
    assert capture_commit(tmp_path) == COMMIT_UNAVAILABLE


def test_write_is_append_only(tmp_path):
    report = _build(tmp_path)
    reports = tmp_path / "reports"
    first = write_report(reports, report)
    again = write_report(reports, report)  # identical → idempotent
    assert first == again
    assert (first / "report.md").exists()
    # a differing report for the same commit lands in a sibling, not overwritten
    report.manifest["name"] = "Changed"
    third = write_report(reports, report)
    assert third != first
