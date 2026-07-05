from __future__ import annotations

from typer.testing import CliRunner

from estafette.cli import app

runner = CliRunner()


def test_assess_valid_manifest_exits_zero(tmp_path, valid_manifest_text, write_manifest):
    write_manifest(tmp_path, valid_manifest_text)
    result = runner.invoke(app, ["assess", str(tmp_path)])
    assert result.exit_code == 0
    assert "Example PoC" in result.output
    assert "not yet implemented" in result.output.lower()


def test_assess_output_is_honest_no_verdict(tmp_path, valid_manifest_text, write_manifest):
    write_manifest(tmp_path, valid_manifest_text)
    result = runner.invoke(app, ["assess", str(tmp_path)])
    lower = result.output.lower()
    for tier in ("bronze", "silver", "gold"):
        assert tier not in lower
    assert "verdict" not in lower or "no verdict is produced" in lower


def test_assess_invalid_manifest_exits_nonzero(tmp_path, valid_manifest_text, write_manifest):
    text = valid_manifest_text.replace("status: poc", "status: prototype")
    write_manifest(tmp_path, text)
    result = runner.invoke(app, ["assess", str(tmp_path)])
    assert result.exit_code == 1


def test_assess_missing_manifest_exits_nonzero(tmp_path):
    result = runner.invoke(app, ["assess", str(tmp_path)])
    assert result.exit_code == 1
