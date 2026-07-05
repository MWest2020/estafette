"""Shared test fixtures: tiny synthetic manifests."""

from __future__ import annotations

from pathlib import Path

import pytest

VALID_MANIFEST = """\
name: Example PoC
licence: EUPL-1.2
owner: Example Municipality
contact: dev@example.gov
status: poc
deps:
  - fastapi
  - pydantic
deployment_target: docker-compose
data:
  schema: "OpenAPI 3 person record"
  volume: "<1GB"
  sensitivity: personal
  synthetic_data: true
"""


def _write_manifest(directory: Path, text: str, name: str = "transfer.yaml") -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def valid_manifest_text() -> str:
    return VALID_MANIFEST


@pytest.fixture
def write_manifest():
    """Return a helper that writes manifest text into a directory."""
    return _write_manifest
