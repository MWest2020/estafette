"""Assemble and run the static checks against a target.

No tier verdict is produced here (that is tier-report-v1); this returns the raw
per-check results for the CLI to render.
"""

from __future__ import annotations

from pathlib import Path

from estafette.checks.deps_reality import DepsRealityCheck
from estafette.checks.licence_consistency import LicenceConsistencyCheck
from estafette.checks.protocol import Check, CheckResult
from estafette.checks.reuse import ReuseCheck
from estafette.checks.sbom import SbomCheck
from estafette.checks.secrets import SecretsCheck
from estafette.manifest import TransferManifest


def discover_local_packages(target: Path) -> set[str]:
    """Top-level Python package names owned by the target (src/ or root layout)."""
    roots = [target / "src", target]
    local: set[str] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                local.add(child.name)
    return local


def build_checks(manifest: TransferManifest, target: Path) -> list[Check]:
    """The five static checks, in report order."""
    local = discover_local_packages(target)
    return [
        ReuseCheck(),
        LicenceConsistencyCheck(manifest),
        SecretsCheck(),
        SbomCheck(manifest),
        DepsRealityCheck(manifest, local),
    ]


def run_checks(checks: list[Check], target: Path) -> list[tuple[str, CheckResult]]:
    """Run each check against ``target``; ToolNotFound propagates to the caller."""
    return [(check.name, check.run(target)) for check in checks]
