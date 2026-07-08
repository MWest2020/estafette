from __future__ import annotations

from estafette.checks.deps_reality import DepsRealityCheck, diff_deps, find_imports
from estafette.checks.protocol import CheckStatus
from estafette.manifest import TransferManifest


def _manifest(deps: list[str]) -> TransferManifest:
    return TransferManifest(
        name="x", licence="MIT", owner="o", contact="c", status="poc", deps=deps
    )


def test_diff_deps_undeclared_and_stdlib():
    undeclared, unused = diff_deps(["click"], {"click", "os", "requests"}, {"myapp"})
    assert undeclared == ["requests"]  # os is stdlib, click is declared, myapp is local
    assert unused == []


def test_diff_deps_unused_declared():
    undeclared, unused = diff_deps(["ghost"], {"os"}, set())
    assert undeclared == []
    assert unused == ["ghost"]


def test_find_imports_recurses(repo):
    target = repo({"a.py": "import click\nfrom requests import get\n", "sub/b.py": "import os\n"})
    assert {"click", "requests", "os"} <= find_imports(target)


def test_undeclared_import_fails(repo):
    target = repo({"code.py": "import requests\n"})
    result = DepsRealityCheck(_manifest([])).run(target)
    assert result.status is CheckStatus.failed
    assert any("requests" in g.message and "not declared" in g.message for g in result.gaps)


def test_clean_deps_pass(repo):
    target = repo({"code.py": "import click\n"})
    result = DepsRealityCheck(_manifest(["click"])).run(target)
    assert result.status is CheckStatus.passed


def test_alias_maps_import_to_package():
    # `import yaml` satisfies a declared `pyyaml` dependency.
    undeclared, unused = diff_deps(["pyyaml"], {"yaml"}, set())
    assert undeclared == []
    assert unused == []


def test_test_dirs_are_not_scanned(repo):
    target = repo({"src/app/__init__.py": "", "tests/test_x.py": "import pytest\n"})
    assert "pytest" not in find_imports(target)


def test_local_package_excluded(repo):
    target = repo(
        {"src/myapp/__init__.py": "", "src/myapp/main.py": "import myapp\nimport click\n"}
    )
    result = DepsRealityCheck(_manifest(["click"]), {"myapp"}).run(target)
    assert result.status is CheckStatus.passed
