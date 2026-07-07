from __future__ import annotations

import pytest

from estafette.manifest import ManifestError, Readiness, load_manifest

BASE = """\
name: Buildable
licence: MIT
owner: Org
contact: dev@example.org
status: poc
build:
  containerfile: Containerfile
  readiness: stays-up
  timeout_seconds: 15
  memory: 256m
  cpus: 1
"""


def test_build_section_parses(tmp_path, write_manifest):
    manifest = load_manifest(write_manifest(tmp_path, BASE))
    assert manifest.build is not None
    assert manifest.build.readiness is Readiness.stays_up
    assert manifest.build.timeout_seconds == 15
    assert manifest.build.memory == "256m"


def test_build_section_optional(tmp_path, write_manifest):
    text = BASE.split("build:")[0]
    manifest = load_manifest(write_manifest(tmp_path, text))
    assert manifest.build is None


def test_invalid_readiness_rejected(tmp_path, write_manifest):
    text = BASE.replace("readiness: stays-up", "readiness: whenever")
    with pytest.raises(ManifestError) as exc:
        load_manifest(write_manifest(tmp_path, text))
    assert "readiness" in str(exc.value)


def test_readiness_defaults_to_stays_up(tmp_path, write_manifest):
    text = (
        "name: X\nlicence: MIT\nowner: o\ncontact: c\nstatus: poc\n"
        "build:\n  containerfile: Dockerfile\n"
    )
    manifest = load_manifest(write_manifest(tmp_path, text))
    assert manifest.build.readiness is Readiness.stays_up
    assert manifest.build.timeout_seconds == 30
