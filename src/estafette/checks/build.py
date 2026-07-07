"""Silver preview — clean-environment build+run via the harness (invariant I4).

INFORMATIONAL in v1: this never gates the bronze verdict (invariant I1). When
podman is absent/unusable or the manifest declares no build recipe, the preview
is reported as unavailable rather than failing.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from estafette.checks.protocol import Gap
from estafette.harness.classify import Category, classify, log_tail
from estafette.harness.podman import HarnessOutcome, PodmanHarness, podman_usable
from estafette.manifest import TransferManifest

_REMEDIATION = {
    Category.missing_declared_dep: (
        "Declare the missing dependency and pin it so a clean build resolves it."
    ),
    Category.undeclared_system_dep: (
        "Install the system package/library in the Containerfile (it is assumed, not declared)."
    ),
    Category.unreachable_internal_service: (
        "Make the target start without an external service, or document/provide it."
    ),
    Category.requires_unavailable_data: (
        "Ship synthetic/seed data or document how to provide the required data."
    ),
    Category.other: "Inspect the captured log tail and reproduce the build locally.",
}


@dataclass
class SilverPreview:
    available: bool
    would_pass: bool | None = None
    classification: str | None = None
    gaps: list[Gap] = field(default_factory=list)
    reason: str | None = None
    evidence: dict = field(default_factory=dict)  # deterministic parts only (no timing, I5)


def _gap_for(category: Category, tail: str) -> Gap:
    message = f"Clean build/run failed: {category.value}"
    if category is Category.other:
        message = f"Clean build/run failed (unclassified). Log tail:\n{tail}"
    return Gap(message=message, remediation=_REMEDIATION[category])


def _from_outcome(outcome: HarnessOutcome) -> SilverPreview:
    evidence = {"caps": outcome.caps}
    if outcome.reached_running_state:
        return SilverPreview(available=True, would_pass=True, evidence=evidence)
    build_log = f"{outcome.build.stdout}{outcome.build.stderr}" if outcome.build else ""
    run_log = f"{outcome.run.stdout}{outcome.run.stderr}" if outcome.run else ""
    category = classify(build_log, run_log)
    tail = log_tail(f"{build_log}\n{run_log}")
    return SilverPreview(
        available=True,
        would_pass=False,
        classification=category.value,
        gaps=[_gap_for(category, tail)],
        evidence=evidence,
    )


def preview_silver(
    target: Path,
    manifest: TransferManifest,
    harness: PodmanHarness | None = None,
    usable_probe: Callable[[], tuple[bool, str]] = podman_usable,
) -> SilverPreview:
    """Produce an informational silver preview for ``target``."""
    if manifest.build is None:
        return SilverPreview(available=False, reason="no build recipe declared in the manifest")
    usable, reason = usable_probe()
    if not usable:
        return SilverPreview(available=False, reason=reason)
    outcome = (harness or PodmanHarness()).build_and_run(str(target), manifest.build)
    return _from_outcome(outcome)
