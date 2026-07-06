from __future__ import annotations

import re

import pytest
from conftest import requires

from estafette.checks.tooling import ToolNotFound, capture_version, run_tool


def test_missing_tool_raises():
    with pytest.raises(ToolNotFound):
        run_tool(["definitely-not-a-real-tool-xyz-123"])


@requires("reuse")
def test_run_tool_captures_output():
    result = run_tool(["reuse", "--version"])
    assert result.exit_code == 0
    assert "reuse" in (result.stdout + result.stderr).lower()


@requires("reuse")
def test_capture_version_is_semver():
    assert re.match(r"\d+\.\d+\.\d+", capture_version("reuse"))
