"""Bronze tier semantics — versioned and mechanical (invariants I1, I5).

The bronze verdict is a pure function of the check results plus manifest
presence. No self-declared or human-judged input participates. See
docs/tiers.md v1.0, which this module implements.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from estafette.checks.protocol import CheckResult, CheckStatus, Gap
from estafette.manifest import TransferManifest

TIER_DOC_VERSION = "1.0"


@dataclass(frozen=True)
class Criterion:
    id: str
    title: str
    passed: bool
    gaps: list[Gap] = field(default_factory=list)


@dataclass(frozen=True)
class BronzeVerdict:
    passed: bool
    criteria: list[Criterion]
    tier_doc_version: str = TIER_DOC_VERSION


def _passed(result: CheckResult | None) -> bool:
    return result is not None and result.status is CheckStatus.passed


def _gaps(*results: CheckResult | None) -> list[Gap]:
    collected: list[Gap] = []
    for result in results:
        if result is not None:
            collected.extend(result.gaps)
    return collected


def compute_bronze(
    results: list[tuple[str, CheckResult]], manifest: TransferManifest
) -> BronzeVerdict:
    """Map check results + manifest onto the six bronze criteria (B1–B6)."""
    by_name = dict(results)
    reuse = by_name.get("reuse")
    licence = by_name.get("licence_consistency")
    secrets = by_name.get("secrets")
    sbom = by_name.get("sbom")
    deps = by_name.get("deps_reality")

    criteria = [
        Criterion("B1", "REUSE-compliant", _passed(reuse), _gaps(reuse)),
        Criterion("B2", "Licence consistent", _passed(licence), _gaps(licence)),
        Criterion("B3", "No secrets", _passed(secrets), _gaps(secrets)),
        Criterion(
            "B4",
            "SBOM generates and matches declared deps",
            _passed(sbom) and _passed(deps),
            _gaps(sbom, deps),
        ),
        # B5/B6 are structurally satisfied: assess only reaches here with a
        # valid manifest, and contact is validated non-empty (min_length=1).
        Criterion("B5", "Transfer manifest present and valid", True, []),
        Criterion("B6", "Contact/owner non-empty", bool(manifest.contact.strip()), []),
    ]
    return BronzeVerdict(passed=all(c.passed for c in criteria), criteria=criteria)
