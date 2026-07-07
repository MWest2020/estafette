from __future__ import annotations

from conftest import make_reuse_compliant, requires
from typer.testing import CliRunner

from estafette.cli import app

runner = CliRunner()

CLEAN_MANIFEST = """\
name: Clean PoC
licence: MIT
owner: Example Org
contact: dev@example.org
status: poc
"""


def _clean_repo(root):
    """A repo that passes all five checks: compliant, no secrets, no deps."""
    make_reuse_compliant(root)
    (root / "transfer.yaml").write_text(CLEAN_MANIFEST, encoding="utf-8")
    (root / "code.py").write_text("import os\n\nprint(os.getcwd())\n", encoding="utf-8")
    return root


# --- command-level behaviour (no external tools needed) -------------------


def test_assess_invalid_manifest_exits_nonzero(tmp_path, valid_manifest_text, write_manifest):
    text = valid_manifest_text.replace("status: poc", "status: prototype")
    write_manifest(tmp_path, text)
    result = runner.invoke(app, ["assess", str(tmp_path)])
    assert result.exit_code == 1


def test_assess_missing_manifest_exits_nonzero(tmp_path):
    result = runner.invoke(app, ["assess", str(tmp_path)])
    assert result.exit_code == 1


def test_assess_missing_tool_exits_nonzero(
    tmp_path, valid_manifest_text, write_manifest, monkeypatch
):
    write_manifest(tmp_path, valid_manifest_text)
    monkeypatch.setenv("PATH", "")  # no external tool is resolvable
    result = runner.invoke(app, ["assess", str(tmp_path)])
    assert result.exit_code == 1


# --- full pipeline (needs reuse + gitleaks + syft) ------------------------


@requires("reuse")
@requires("gitleaks")
@requires("syft")
def test_assess_clean_repo_all_pass(tmp_path):
    root = tmp_path / "clean"
    root.mkdir()
    _clean_repo(root)
    out_dir = tmp_path / "out"
    result = runner.invoke(app, ["assess", str(root), "--reports-dir", str(out_dir)])
    assert result.exit_code == 0
    out = result.output
    assert "[FAIL]" not in out
    assert out.count("[PASS]") == 5
    assert "Tool versions:" in out
    assert "Bronze verdict: PASS" in out  # all five checks pass → bronze
    assert "Report written:" in out
    lower = out.lower()
    assert "gold" not in lower  # gold is never presented in v1
    # "silver" appears only inside the informational "Silver preview" label.
    assert "silver preview" in lower
    assert "not assessable" in lower  # clean fixture declares no build recipe
    # a report was actually written
    assert (out_dir).exists() and any(out_dir.rglob("report.md"))


@requires("reuse")
@requires("gitleaks")
@requires("syft")
def test_assess_reports_gaps_but_command_succeeds(tmp_path):
    root = tmp_path / "gappy"
    root.mkdir()
    (root / "transfer.yaml").write_text(CLEAN_MANIFEST, encoding="utf-8")
    (root / "code.py").write_text("print(1)\n", encoding="utf-8")  # not REUSE-compliant
    result = runner.invoke(app, ["assess", str(root), "--reports-dir", str(tmp_path / "out")])
    assert result.exit_code == 0  # command ran; verdict is not the exit code
    assert "[FAIL] reuse" in result.output
    assert "Bronze verdict: FAIL" in result.output
