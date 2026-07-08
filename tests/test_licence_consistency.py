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
    # REUSE-IgnoreStart
    target = repo({"code.py": "# SPDX-License-Identifier: MIT\nprint(1)\n"})
    # REUSE-IgnoreEnd
    result = LicenceConsistencyCheck(_manifest("EUPL-1.2")).run(target)
    assert result.status is CheckStatus.failed


def test_deep_spdx_string_is_not_a_header(repo):
    # An SPDX identifier deep in a file (e.g. a test fixture or regex literal)
    # must not be mistaken for the file's licence header.
    # REUSE-IgnoreStart
    body = "\n" * 30 + "value = 'SPDX-License-Identifier: MIT'\n"
    # REUSE-IgnoreEnd
    target = repo({"code.py": body})
    result = LicenceConsistencyCheck(_manifest("EUPL-1.2")).run(target)
    assert result.status is CheckStatus.passed


def test_collect_sources_reads_package_json(repo):
    target = repo({"package.json": '{"license": "Apache-2.0"}'})
    sources = collect_sources(target, _manifest("EUPL-1.2"))
    assert sources["manifest"] == "EUPL-1.2"
    assert sources["package.json"] == "Apache-2.0"
