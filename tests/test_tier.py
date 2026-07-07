from __future__ import annotations

from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.manifest import TransferManifest
from estafette.tier import TIER_DOC_VERSION, compute_bronze


def _manifest() -> TransferManifest:
    return TransferManifest(name="x", licence="MIT", owner="o", contact="c", status="poc")


def _ok() -> CheckResult:
    return CheckResult(CheckStatus.passed, [], {})


def _fail(msg: str) -> CheckResult:
    return CheckResult(CheckStatus.failed, [Gap(message=msg, remediation="fix it")], {})


def _all_pass() -> list[tuple[str, CheckResult]]:
    return [(n, _ok()) for n in ("reuse", "licence_consistency", "secrets", "sbom", "deps_reality")]


def test_all_pass_is_bronze():
    verdict = compute_bronze(_all_pass(), _manifest())
    assert verdict.passed is True
    assert verdict.tier_doc_version == TIER_DOC_VERSION
    assert len(verdict.criteria) == 6


def test_single_failing_check_withholds_bronze():
    results = dict(_all_pass())
    results["secrets"] = _fail("planted secret at x.py:1")
    verdict = compute_bronze(list(results.items()), _manifest())
    assert verdict.passed is False
    b3 = next(c for c in verdict.criteria if c.id == "B3")
    assert b3.passed is False
    assert b3.gaps and "planted secret" in b3.gaps[0].message


def test_b4_requires_both_sbom_and_deps():
    results = dict(_all_pass())
    results["deps_reality"] = _fail("requests used but not declared")
    verdict = compute_bronze(list(results.items()), _manifest())
    b4 = next(c for c in verdict.criteria if c.id == "B4")
    assert b4.passed is False
    assert any("requests" in g.message for g in b4.gaps)
