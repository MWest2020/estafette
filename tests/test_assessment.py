from __future__ import annotations

from estafette.assessment import build_checks, discover_local_packages
from estafette.manifest import TransferManifest


def _manifest() -> TransferManifest:
    return TransferManifest(name="x", licence="MIT", owner="o", contact="c", status="poc")


def test_discover_local_packages_src_layout(repo):
    target = repo({"src/pkg/__init__.py": "", "src/pkg/m.py": ""})
    assert discover_local_packages(target) == {"pkg"}


def test_discover_local_packages_root_layout(repo):
    target = repo({"pkg/__init__.py": ""})
    assert discover_local_packages(target) == {"pkg"}


def test_build_checks_names_and_order(repo):
    target = repo({"code.py": ""})
    names = [c.name for c in build_checks(_manifest(), target)]
    assert names == ["reuse", "licence_consistency", "secrets", "sbom", "deps_reality"]
