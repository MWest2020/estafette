"""SBOM check — wraps `syft` (invariant I2).

Verifies the SBOM generates cleanly and that every declared dependency actually
appears in it. Extra (transitive) components are expected and are not gaps.
"""

from __future__ import annotations

import json
from pathlib import Path

from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.checks.tooling import capture_version, run_tool
from estafette.manifest import TransferManifest


def normalise(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def missing_from_sbom(declared: list[str], sbom_names: list[str]) -> list[str]:
    """Declared dependencies that do not appear in the SBOM (normalised)."""
    present = {normalise(n) for n in sbom_names}
    return [dep for dep in declared if normalise(dep) not in present]


def _sbom_names(stdout: str) -> list[str] | None:
    try:
        artifacts = json.loads(stdout).get("artifacts", [])
    except (json.JSONDecodeError, AttributeError):
        return None
    return [a.get("name", "") for a in artifacts]


class SbomCheck:
    """The SBOM must generate cleanly and cover the declared dependencies."""

    name = "sbom"

    def __init__(self, manifest: TransferManifest) -> None:
        self._manifest = manifest

    def run(self, target: Path) -> CheckResult:
        result = run_tool(["syft", "scan", f"dir:{target}", "-o", "syft-json", "-q"])
        version = capture_version("syft")
        names = _sbom_names(result.stdout) if result.exit_code == 0 else None
        if names is None:
            evidence = {"tool": "syft", "version": version, "exit_code": result.exit_code}
            return CheckResult(
                CheckStatus.failed,
                [
                    Gap(
                        message="SBOM did not generate cleanly.",
                        remediation="Run `syft scan dir:<path>` locally and resolve the error.",
                    )
                ],
                evidence,
            )

        missing = missing_from_sbom(self._manifest.deps, names)
        evidence = {
            "tool": "syft",
            "version": version,
            "exit_code": result.exit_code,
            "sbom_component_count": len(names),
            "declared_count": len(self._manifest.deps),
        }
        if not missing:
            return CheckResult(CheckStatus.passed, [], evidence)
        gaps = [
            Gap(
                message=f"Declared dependency '{dep}' is absent from the generated SBOM.",
                remediation="Ensure the dependency is actually installed/locked, or remove it "
                "from the manifest if it is not really used.",
            )
            for dep in missing
        ]
        return CheckResult(CheckStatus.failed, gaps, evidence)
