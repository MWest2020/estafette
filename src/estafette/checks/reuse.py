"""REUSE compliance check — wraps `reuse lint --json` (invariant I2)."""

from __future__ import annotations

import json
from pathlib import Path

from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.checks.tooling import capture_version, run_tool


def _gaps_from_report(non_compliant: dict) -> list[Gap]:
    gaps: list[Gap] = []
    missing = sorted(
        set(non_compliant.get("missing_licensing_info", []))
        | set(non_compliant.get("missing_copyright_info", []))
    )
    if missing:
        listed = ", ".join(missing)
        gaps.append(
            Gap(
                message=f"{len(missing)} file(s) lack licence/copyright info: {listed}",
                remediation="Add SPDX headers, e.g. `reuse annotate --license <SPDX> "
                "--copyright '<holder>' <file>`.",
            )
        )
    for key, label in (
        ("missing_licenses", "licence text missing from LICENSES/"),
        ("bad_licenses", "unrecognised licence identifier"),
        ("deprecated_licenses", "deprecated licence identifier"),
    ):
        items = non_compliant.get(key)
        if items:
            gaps.append(
                Gap(
                    message=f"{label}: {', '.join(sorted(map(str, items)))}",
                    remediation="Run `reuse lint` locally and resolve the reported issue.",
                )
            )
    return gaps


class ReuseCheck:
    """Every file must carry licence and copyright information."""

    name = "reuse"

    def run(self, target: Path) -> CheckResult:
        result = run_tool(["reuse", "--root", str(target), "lint", "--json"])
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            report = {}
        version = report.get("reuse_tool_version") or capture_version("reuse")
        evidence = {"tool": "reuse", "version": version, "exit_code": result.exit_code}

        compliant = report.get("summary", {}).get("compliant")
        if compliant is True or (compliant is None and result.exit_code == 0):
            return CheckResult(CheckStatus.passed, [], evidence)

        gaps = _gaps_from_report(report.get("non_compliant", {}))
        if not gaps:
            gaps = [
                Gap(
                    message="Repository is not REUSE-compliant.",
                    remediation="Run `reuse lint` locally and add the missing licence/copyright "
                    "info.",
                )
            ]
        return CheckResult(CheckStatus.failed, gaps, evidence)
