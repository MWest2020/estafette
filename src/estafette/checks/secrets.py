"""Secret detection check — wraps `gitleaks` (invariant I2).

Findings report location only; the secret value is never echoed (keeps reports
safe to commit, invariant I5).
"""

from __future__ import annotations

import json
from pathlib import Path

from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.checks.tooling import capture_version, run_tool


def _parse_findings(stdout: str) -> list[dict]:
    stdout = stdout.strip()
    if not stdout:
        return []
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _gap_for(finding: dict) -> Gap:
    path = finding.get("File", "?")
    line = finding.get("StartLine", "?")
    rule = finding.get("RuleID") or finding.get("Description") or "secret"
    return Gap(
        message=f"Potential secret ({rule}) at {path}:{line}",
        remediation="Remove the secret, rotate it, and load it from the environment "
        "or a secret store instead of committing it.",
    )


class SecretsCheck:
    """No secrets may be present in the target."""

    name = "secrets"

    def run(self, target: Path) -> CheckResult:
        result = run_tool(
            [
                "gitleaks",
                "dir",
                str(target),
                "--report-format",
                "json",
                "--report-path",
                "-",
                "--redact",
                "--no-banner",
                "--exit-code",
                "1",
            ]
        )
        findings = _parse_findings(result.stdout)
        evidence = {
            "tool": "gitleaks",
            "version": capture_version("gitleaks"),
            "exit_code": result.exit_code,
            "finding_count": len(findings),
        }
        if not findings and result.exit_code == 0:
            return CheckResult(CheckStatus.passed, [], evidence)
        gaps = [_gap_for(f) for f in findings]
        if not gaps:
            gaps = [
                Gap(
                    message="gitleaks reported a problem but no findings could be parsed.",
                    remediation="Run `gitleaks dir <path>` locally to inspect the output.",
                )
            ]
        return CheckResult(CheckStatus.failed, gaps, evidence)
