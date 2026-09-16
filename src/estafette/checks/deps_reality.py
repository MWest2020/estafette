"""Dependency reality check — estafette-owned diff of declared deps vs reality.

Compares the manifest's declared dependencies against the modules actually
imported in the code, in both directions. Import-name vs package-name mapping
is heuristic in v1 (Python-focused); see the change's design.md.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.manifest import TransferManifest

# Test directories hold dev-only imports (pytest, local conftest), not runtime
# dependencies, so they are excluded from the declared-runtime-deps comparison.
_SKIP_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist", ".ruff_cache",
    "tests", "test",
}
_STDLIB = set(sys.stdlib_module_names)

# Common cases where the import name differs from the distribution/package name.
_IMPORT_ALIASES = {
    "yaml": "pyyaml",
    "PIL": "pillow",
    "cv2": "opencv-python",
    "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
}


def _normalise(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def _canonical(name: str) -> str:
    """Normalise an import name to its distribution name where known."""
    return _normalise(_IMPORT_ALIASES.get(name, name))


def find_imports(target: Path) -> set[str]:
    """Top-level modules imported by the Python files under ``target``.

    Via de syntaxboom, niet via een regex over de rauwe tekst. Een regex die op
    ``^\s*(?:import|from)\s+(\w+)`` matcht leest ook proza: een docstring-regel
    als "from the public site" levert dan een dependency ``the``.

    Gemeten op 2026-09-16 op MWest2020/internetnl-cli: zeven meldingen, waarvan
    drie geen pakket waren (``a``, ``here``, ``the``). Dat is niet alleen ruis —
    het advies erbij luidde letterlijk "Add 'the' to the manifest", en een gate
    die je dat aanraadt, leert je hem te negeren.

    Een bestand dat niet parseert wordt overgeslagen. Dat is bewust: het gaat om
    een repo die je nog niet vertrouwt, en een half bestand is geen reden om de
    hele beoordeling te laten omvallen.
    """
    found: set[str] = set()
    for path in target.rglob("*.py"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        try:
            boom = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except (SyntaxError, ValueError):
            continue
        for node in ast.walk(boom):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                # level > 0 is een relatieve import: eigen code, geen dependency.
                if node.level == 0 and node.module:
                    found.add(node.module.split(".")[0])
    return found


def diff_deps(
    declared: list[str], imports: set[str], local: set[str]
) -> tuple[list[str], list[str]]:
    """Return (undeclared imports, unused declared deps), both normalised-compared."""
    declared_norm = {_normalise(d) for d in declared}
    local_norm = {_normalise(name) for name in local}
    external = {i for i in imports if i not in _STDLIB and _canonical(i) not in local_norm}
    undeclared = sorted(i for i in external if _canonical(i) not in declared_norm)
    imported_canon = {_canonical(i) for i in imports}
    unused = sorted(d for d in declared if _normalise(d) not in imported_canon)
    return undeclared, unused


class DepsRealityCheck:
    """Declared dependencies must match what the code actually uses."""

    name = "deps_reality"

    def __init__(self, manifest: TransferManifest, local_packages: set[str] | None = None) -> None:
        self._manifest = manifest
        self._local = local_packages or set()

    def run(self, target: Path) -> CheckResult:
        imports = find_imports(target)
        undeclared, unused = diff_deps(self._manifest.deps, imports, self._local)
        evidence = {
            "declared": sorted(self._manifest.deps),
            "imported": sorted(imports),
            "local_packages": sorted(self._local),
        }
        gaps: list[Gap] = []
        for dep in undeclared:
            gaps.append(
                Gap(
                    message=f"dependency '{dep}' is used in code but not declared",
                    remediation=f"Add '{dep}' to the manifest's `deps` (and the project metadata).",
                )
            )
        for dep in unused:
            gaps.append(
                Gap(
                    message=f"dependency '{dep}' is declared but never imported",
                    remediation=f"Remove '{dep}' from the manifest if it is genuinely unused.",
                )
            )
        status = CheckStatus.passed if not gaps else CheckStatus.failed
        return CheckResult(status, gaps, evidence)
