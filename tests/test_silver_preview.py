from __future__ import annotations

from pathlib import Path

from estafette.checks.build import preview_silver
from estafette.harness.podman import HarnessOutcome, StageResult
from estafette.manifest import BuildSpec, TransferManifest


def _manifest(with_build: bool) -> TransferManifest:
    build = BuildSpec(containerfile="Containerfile") if with_build else None
    return TransferManifest(
        name="x", licence="MIT", owner="o", contact="c", status="poc", build=build
    )


class _FakeHarness:
    def __init__(self, outcome: HarnessOutcome):
        self._outcome = outcome

    def build_and_run(self, context, spec):
        return self._outcome


def test_no_build_recipe_is_not_assessable():
    preview = preview_silver(Path("/repo"), _manifest(with_build=False))
    assert preview.available is False
    assert "no build recipe" in preview.reason


def test_unusable_podman_degrades_gracefully():
    preview = preview_silver(
        Path("/repo"),
        _manifest(with_build=True),
        usable_probe=lambda: (False, "rootless podman is installed but not usable"),
    )
    assert preview.available is False
    assert "not usable" in preview.reason


def test_reached_running_state_would_pass():
    outcome = HarnessOutcome(True, build=StageResult(0, "", ""), run=StageResult(0, "", ""))
    preview = preview_silver(
        Path("/repo"),
        _manifest(with_build=True),
        harness=_FakeHarness(outcome),
        usable_probe=lambda: (True, ""),
    )
    assert preview.available is True
    assert preview.would_pass is True
    assert preview.gaps == []


def test_failure_is_classified_with_gap():
    run = StageResult(1, "", "ModuleNotFoundError: No module named 'click'")
    outcome = HarnessOutcome(False, build=StageResult(0, "", ""), run=run)
    preview = preview_silver(
        Path("/repo"),
        _manifest(with_build=True),
        harness=_FakeHarness(outcome),
        usable_probe=lambda: (True, ""),
    )
    assert preview.would_pass is False
    assert preview.classification == "missing-declared-dep"
    assert preview.gaps
    # deterministic evidence only: no timing keys (I5)
    assert "caps" in preview.evidence
    assert not any("second" in k or "duration" in k for k in preview.evidence)
