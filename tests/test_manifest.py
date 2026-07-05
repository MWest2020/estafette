from __future__ import annotations

from pathlib import Path

import pytest

from estafette.manifest import (
    DEFAULT_MANIFEST_NAME,
    ManifestError,
    Status,
    load_manifest,
    resolve_manifest_path,
)


def test_valid_manifest_parses(tmp_path, valid_manifest_text, write_manifest):
    manifest = load_manifest(write_manifest(tmp_path, valid_manifest_text))
    assert manifest.name == "Example PoC"
    assert manifest.status is Status.poc
    assert manifest.deps == ["fastapi", "pydantic"]
    assert manifest.data is not None
    assert manifest.data.schema_ == "OpenAPI 3 person record"
    assert manifest.data.synthetic_data is True


def test_missing_required_field_rejected(tmp_path, valid_manifest_text, write_manifest):
    text = valid_manifest_text.replace("contact: dev@example.gov\n", "")
    with pytest.raises(ManifestError) as exc:
        load_manifest(write_manifest(tmp_path, text))
    assert "contact" in str(exc.value)


def test_invalid_status_rejected(tmp_path, valid_manifest_text, write_manifest):
    text = valid_manifest_text.replace("status: poc", "status: prototype")
    with pytest.raises(ManifestError) as exc:
        load_manifest(write_manifest(tmp_path, text))
    assert "status" in str(exc.value)


def test_empty_contact_rejected(tmp_path, valid_manifest_text, write_manifest):
    text = valid_manifest_text.replace("contact: dev@example.gov", 'contact: ""')
    with pytest.raises(ManifestError):
        load_manifest(write_manifest(tmp_path, text))


def test_non_mapping_manifest_rejected(tmp_path, write_manifest):
    with pytest.raises(ManifestError) as exc:
        load_manifest(write_manifest(tmp_path, "- just\n- a\n- list\n"))
    assert "mapping" in str(exc.value)


def test_missing_file_is_actionable(tmp_path):
    with pytest.raises(ManifestError) as exc:
        load_manifest(tmp_path / "nope.yaml")
    assert "not found" in str(exc.value).lower()


def test_default_manifest_path(tmp_path):
    assert resolve_manifest_path(str(tmp_path)) == tmp_path / DEFAULT_MANIFEST_NAME


def test_manifest_override_path():
    assert resolve_manifest_path("some/repo", "other/spot.yaml") == Path("other/spot.yaml")
