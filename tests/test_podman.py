from __future__ import annotations

import pytest

from estafette.harness.podman import (
    HarnessOutcome,
    PodmanHarness,
    StageResult,
    build_argv,
    podman_usable,
    reached_running_state,
    run_argv,
)
from estafette.manifest import BuildSpec, Readiness


def test_run_argv_enforces_i4_isolation():
    argv = run_argv(BuildSpec(memory="256m", cpus=1))
    assert "--network=none" in argv  # run stage has no network
    assert "--read-only" in argv
    assert "--env-host=false" in argv
    assert "--memory" in argv and "256m" in argv
    assert "--cpus" in argv and "1.0" in argv  # cpus is a float field
    # no host env passthrough
    assert "--env" not in argv


def test_build_argv_shape():
    argv = build_argv("/repo", "Containerfile")
    assert argv[:2] == ["podman", "build"]
    assert "-f" in argv and "Containerfile" in argv
    assert argv[-1] == "/repo"


def test_reached_running_state_exits_zero():
    ok = StageResult(0, "", "")
    bad = StageResult(1, "", "")
    assert reached_running_state(Readiness.exits_zero, ok) is True
    assert reached_running_state(Readiness.exits_zero, bad) is False


def test_reached_running_state_stays_up():
    timed_out = StageResult(124, "", "", timed_out=True)
    crashed = StageResult(1, "", "")
    assert reached_running_state(Readiness.stays_up, timed_out) is True
    assert reached_running_state(Readiness.stays_up, crashed) is False


class _FakeExec:
    """Executor stub returning canned results keyed by podman subcommand."""

    def __init__(self, build: StageResult, run: StageResult | None):
        self.build, self.run = build, run
        self.calls: list[list[str]] = []

    def __call__(self, argv, timeout):
        self.calls.append(argv)
        if argv[1] == "build":
            return self.build
        if argv[1] == "run":
            return self.run
        return StageResult(0, "", "")  # rm cleanup


def test_build_failure_short_circuits_run():
    fake = _FakeExec(build=StageResult(1, "", "boom"), run=None)
    outcome = PodmanHarness(fake).build_and_run("/repo", BuildSpec())
    assert isinstance(outcome, HarnessOutcome)
    assert outcome.reached_running_state is False
    assert outcome.run is None
    assert not any(c[1] == "run" for c in fake.calls)


def test_successful_stays_up_run():
    fake = _FakeExec(build=StageResult(0, "ok", ""), run=StageResult(124, "", "", timed_out=True))
    outcome = PodmanHarness(fake).build_and_run("/repo", BuildSpec(readiness=Readiness.stays_up))
    assert outcome.reached_running_state is True
    assert outcome.caps["network_run"] == "none"


def test_podman_usable_false_without_binary(monkeypatch):
    monkeypatch.setenv("PATH", "")
    usable, reason = podman_usable()
    assert usable is False
    assert "not installed" in reason


# Live integration — runs only where rootless podman actually works (skips in
# CI and in nested/LXC sandboxes). Exercises real build + network-free run.
@pytest.mark.skipif(not podman_usable()[0], reason="rootless podman not usable here")
def test_live_build_and_run_reaches_state(tmp_path):
    (tmp_path / "Containerfile").write_text("FROM alpine:3.20\nCMD [\"true\"]\n", encoding="utf-8")
    spec = BuildSpec(
        containerfile="Containerfile", readiness=Readiness.exits_zero, timeout_seconds=60
    )
    outcome = PodmanHarness().build_and_run(str(tmp_path), spec)
    assert outcome.reached_running_state is True
