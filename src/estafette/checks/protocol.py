"""The Check protocol every mechanical check implements.

A check never bare-fails: on failure it emits actionable gaps (invariant I3).
No concrete checks live here — they arrive in checks-static-v1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


class CheckStatus(StrEnum):
    passed = "pass"
    failed = "fail"


@dataclass(frozen=True)
class Gap:
    """A single actionable problem, with a concrete remediation."""

    message: str
    remediation: str


@dataclass(frozen=True)
class CheckResult:
    """The result of running one check against a target."""

    status: CheckStatus
    gaps: list[Gap] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Check(Protocol):
    """A named, mechanical assessment of a target repository."""

    name: str

    def run(self, target: Path) -> CheckResult:
        """Assess ``target`` and return a CheckResult."""
        ...
