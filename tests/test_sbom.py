from __future__ import annotations

from conftest import requires

from estafette.checks.protocol import CheckStatus
from estafette.checks.sbom import SbomCheck, missing_from_sbom, normalise
from estafette.manifest import TransferManifest


def _manifest(deps: list[str]) -> TransferManifest:
    return TransferManifest(
        name="x", licence="MIT", owner="o", contact="c", status="poc", deps=deps
    )


def test_normalise():
    assert normalise("PyYAML") == "pyyaml"
    assert normalise("some_pkg") == "some-pkg"


def test_missing_from_sbom_is_normalised():
    assert missing_from_sbom(["Click", "PyYAML"], ["click", "pyyaml"]) == []
    assert missing_from_sbom(["click", "ghost"], ["click"]) == ["ghost"]


@requires("syft")
def test_sbom_matches_declared(repo):
    target = repo({"requirements.txt": "click==8.1.7\n"})
    result = SbomCheck(_manifest(["click"])).run(target)
    assert result.status is CheckStatus.passed
    assert result.evidence["sbom_component_count"] >= 1


@requires("syft")
def test_sbom_missing_declared_dep_fails(repo):
    target = repo({"requirements.txt": "click==8.1.7\n"})
    result = SbomCheck(_manifest(["click", "totally-absent-pkg"])).run(target)
    assert result.status is CheckStatus.failed
    assert any("totally-absent-pkg" in g.message for g in result.gaps)
