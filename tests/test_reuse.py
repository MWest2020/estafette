from __future__ import annotations

from conftest import requires

from estafette.checks.protocol import CheckStatus
from estafette.checks.reuse import ReuseCheck


@requires("reuse")
def test_compliant_repo_passes(repo):
    target = repo({"code.py": "import os\n"}, compliant=True)
    result = ReuseCheck().run(target)
    assert result.status is CheckStatus.passed
    assert result.evidence["tool"] == "reuse"
    assert result.gaps == []


@requires("reuse")
def test_noncompliant_repo_fails_with_file_gap(repo):
    target = repo({"code.py": "print(1)\n"})  # no REUSE.toml, no header
    result = ReuseCheck().run(target)
    assert result.status is CheckStatus.failed
    assert result.gaps
    assert "code.py" in result.gaps[0].message
    assert "reuse annotate" in result.gaps[0].remediation
