from __future__ import annotations

from estafette.checks.licence_consistency import LicenceConsistencyCheck, collect_sources
from estafette.checks.protocol import CheckStatus
from estafette.manifest import TransferManifest


def _manifest(licence: str = "EUPL-1.2") -> TransferManifest:
    return TransferManifest(name="x", licence=licence, owner="o", contact="c", status="poc")


def test_consistent_licence_passes(repo):
    target = repo({"pyproject.toml": '[project]\nname = "x"\nlicense = "EUPL-1.2"\n'})
    result = LicenceConsistencyCheck(_manifest()).run(target)
    assert result.status is CheckStatus.passed


def test_mismatched_pyproject_licence_fails(repo):
    target = repo({"pyproject.toml": '[project]\nname = "x"\nlicense = "MIT"\n'})
    result = LicenceConsistencyCheck(_manifest("EUPL-1.2")).run(target)
    assert result.status is CheckStatus.failed
    assert "pyproject.toml" in result.gaps[0].message
    assert "MIT" in result.gaps[0].message


def test_header_mismatch_detected(repo):
    target = repo({"code.py": "# SPDX-License-Identifier: MIT\nprint(1)\n"})
    result = LicenceConsistencyCheck(_manifest("EUPL-1.2")).run(target)
    assert result.status is CheckStatus.failed


def test_collect_sources_reads_package_json(repo):
    target = repo({"package.json": '{"license": "Apache-2.0"}'})
    sources = collect_sources(target, _manifest("EUPL-1.2"))
    assert sources["manifest"] == "EUPL-1.2"
    assert sources["package.json"] == "Apache-2.0"
