"""Licence consistency check — estafette-owned.

Compares the declared licence across the manifest, `pyproject.toml`,
`package.json`, and SPDX headers, and reports any disagreement.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.manifest import TransferManifest

# Match a real SPDX header: a valid licence token, not arbitrary text. Only the
# head of a file is scanned so SPDX strings that appear deep in source (test
# fixtures, a regex literal like this one) are not mistaken for a file's header.
# REUSE-IgnoreStart
_SPDX_RE = re.compile(r"SPDX-License-Identifier:\s*([\w.+-]+)")
# REUSE-IgnoreEnd
_HEAD_LINES = 20
_SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist", "LICENSES"}
_HEADER_EXT = {".py", ".js", ".ts", ".go", ".java", ".rs", ".sh"}


def _pyproject_licence(target: Path) -> str | None:
    path = target / "pyproject.toml"
    if not path.exists():
        return None
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    lic = data.get("project", {}).get("license")
    if isinstance(lic, str):
        return lic
    if isinstance(lic, dict):
        return lic.get("text")
    return None


def _package_json_licence(target: Path) -> str | None:
    path = target / "package.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("license")
    except json.JSONDecodeError:
        return None


def _header_licences(target: Path) -> set[str]:
    found: set[str] = set()
    for path in target.rglob("*"):
        if path.suffix not in _HEADER_EXT or any(p in _SKIP_DIRS for p in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = _SPDX_RE.search("\n".join(text.splitlines()[:_HEAD_LINES]))
        if match:
            found.add(match.group(1))
    return found


def collect_sources(target: Path, manifest: TransferManifest) -> dict[str, str]:
    """Map each source that declares a licence to the value it declares."""
    sources: dict[str, str] = {"manifest": manifest.licence}
    pyproject = _pyproject_licence(target)
    if pyproject:
        sources["pyproject.toml"] = pyproject
    package = _package_json_licence(target)
    if package:
        sources["package.json"] = package
    headers = _header_licences(target)
    if len(headers) == 1:
        sources["headers"] = next(iter(headers))
    elif len(headers) > 1:
        sources["headers"] = "/".join(sorted(headers))
    return sources


class LicenceConsistencyCheck:
    """The declared licence must agree everywhere it appears."""

    name = "licence_consistency"

    def __init__(self, manifest: TransferManifest) -> None:
        self._manifest = manifest

    def run(self, target: Path) -> CheckResult:
        sources = collect_sources(target, self._manifest)
        distinct = set(sources.values())
        evidence = {"sources": sources}
        if len(distinct) <= 1:
            return CheckResult(CheckStatus.passed, [], evidence)
        listed = "; ".join(f"{k}={v}" for k, v in sorted(sources.items()))
        gaps = [
            Gap(
                message=f"Declared licence disagrees across sources: {listed}",
                remediation="Make the licence identical in the manifest, project metadata, "
                "and file headers.",
            )
        ]
        return CheckResult(CheckStatus.failed, gaps, evidence)
