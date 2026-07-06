"""Shared runner for the external tools estafette orchestrates (invariant I2).

A missing tool is an estafette-environment error, never a silent pass and never
the target's fault (invariant I1). Tool versions are captured for the report
(invariant I5).
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

_VERSION_RE = re.compile(r"\d+\.\d+\.\d+")

# How to ask each tool for its version.
_VERSION_CMD: dict[str, list[str]] = {
    "reuse": ["reuse", "--version"],
    "gitleaks": ["gitleaks", "version"],
    "syft": ["syft", "version"],
}


class ToolNotFound(Exception):
    """Raised when a required external tool is not installed or not on PATH."""


@dataclass(frozen=True)
class ToolResult:
    exit_code: int
    stdout: str
    stderr: str


def _resolve(tool: str) -> str:
    exe = shutil.which(tool)
    if exe is None:
        raise ToolNotFound(
            f"Required tool '{tool}' is not installed or not on PATH. "
            f"Install it and re-run (see the README prerequisites)."
        )
    return exe


def run_tool(argv: list[str], cwd: str | Path | None = None) -> ToolResult:
    """Run ``argv`` as a subprocess, returning exit code and captured output.

    Raises ToolNotFound if ``argv[0]`` is not on PATH.
    """
    exe = _resolve(argv[0])
    proc = subprocess.run(
        [exe, *argv[1:]],
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    return ToolResult(proc.returncode, proc.stdout, proc.stderr)


def capture_version(tool: str) -> str:
    """Return a version string for ``tool`` (e.g. '1.46.0'), or 'unknown'."""
    argv = _VERSION_CMD.get(tool, [tool, "--version"])
    res = run_tool(argv)
    text = (res.stdout or res.stderr).strip()
    match = _VERSION_RE.search(text)
    if match:
        return match.group(0)
    return text.splitlines()[0] if text else "unknown"
