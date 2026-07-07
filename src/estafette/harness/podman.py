"""Rootless-podman two-stage runner (invariant I4).

Build stage may fetch dependencies over the network; the run stage executes
with no network, resource caps, no host environment, and read-only mounts. The
I4-critical argv is built by pure functions (`build_argv`, `run_argv`) so the
guarantees are unit-testable without a live podman. Execution is injectable.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field

from estafette.manifest import BuildSpec, Readiness

_IMAGE_TAG = "estafette-assess:latest"
_CONTAINER_NAME = "estafette-assess-run"


@dataclass(frozen=True)
class StageResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


@dataclass
class HarnessOutcome:
    reached_running_state: bool
    build: StageResult | None = None
    run: StageResult | None = None
    caps: dict = field(default_factory=dict)


Executor = Callable[[list[str], int | None], StageResult]


def podman_usable() -> tuple[bool, str]:
    """Return (usable, reason). Rootless podman must actually work, not just exist."""
    if shutil.which("podman") is None:
        return False, "podman not installed"
    try:
        proc = subprocess.run(
            ["podman", "info", "--format", "{{.Host.Security.Rootless}}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"podman not usable: {exc}"
    if proc.returncode != 0:
        return False, "rootless podman is installed but not usable in this environment"
    return True, ""


def build_argv(context: str, containerfile: str | None, tag: str = _IMAGE_TAG) -> list[str]:
    """`podman build` — the build stage (network permitted for dependency fetch)."""
    argv = ["podman", "build", "-t", tag]
    if containerfile:
        argv += ["-f", containerfile]
    argv.append(context)
    return argv


def run_argv(spec: BuildSpec, tag: str = _IMAGE_TAG, name: str = _CONTAINER_NAME) -> list[str]:
    """`podman run` — the run stage. Enforces the I4 isolation properties."""
    argv = [
        "podman", "run", "--rm",
        "--name", name,
        "--network=none",          # untrusted code never reaches the network
        "--read-only",             # read-only root filesystem
        "--env-host=false",        # no host environment leaks in
    ]
    if spec.memory:
        argv += ["--memory", spec.memory]
    if spec.cpus:
        argv += ["--cpus", str(spec.cpus)]
    argv.append(tag)
    return argv


def _subprocess_exec(argv: list[str], timeout: int | None) -> StageResult:
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        return StageResult(124, exc.stdout or "", exc.stderr or "", timed_out=True)
    return StageResult(proc.returncode, proc.stdout, proc.stderr)


def reached_running_state(readiness: Readiness, run: StageResult) -> bool:
    """Evaluate the declared readiness mode against the run result."""
    if readiness is Readiness.exits_zero:
        return not run.timed_out and run.exit_code == 0
    # stays-up: still running when the window elapsed (timed out) counts as reached.
    return run.timed_out or run.exit_code == 0


class PodmanHarness:
    """Builds then runs the target with I4 isolation."""

    def __init__(self, execute: Executor = _subprocess_exec) -> None:
        self._execute = execute

    def build_and_run(self, context: str, spec: BuildSpec) -> HarnessOutcome:
        caps = {
            "network_run": "none",
            "memory": spec.memory,
            "cpus": spec.cpus,
            "readiness": spec.readiness.value,
            "timeout_seconds": spec.timeout_seconds,
        }
        build = self._execute(build_argv(context, spec.containerfile), None)
        if build.exit_code != 0:
            return HarnessOutcome(False, build=build, run=None, caps=caps)
        run = self._execute(run_argv(spec), spec.timeout_seconds)
        self._execute(["podman", "rm", "-f", _CONTAINER_NAME], 30)  # best-effort cleanup
        return HarnessOutcome(reached_running_state(spec.readiness, run), build, run, caps)
