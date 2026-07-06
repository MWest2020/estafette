"""Shared test fixtures: tiny synthetic manifests and repos."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

# --- REUSE-compliance building blocks -------------------------------------
MIT_LICENSE_TEXT = "MIT License\n\nPermission is hereby granted, free of charge...\n"

# A REUSE.toml that blanket-annotates every file, so a fixture repo is
# REUSE-compliant without needing a header in every single file.
REUSE_TOML = """\
version = 1

[[annotations]]
path = ["**"]
precedence = "aggregate"
SPDX-FileCopyrightText = "2026 Example"
SPDX-License-Identifier = "MIT"
"""


def requires(tool: str):
    """Skip marker for tests that need an external tool installed."""
    return pytest.mark.skipif(shutil.which(tool) is None, reason=f"{tool} not installed")


def build_repo(root: Path, files: dict[str, str]) -> Path:
    """Write ``files`` (relative path -> content) under ``root``."""
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def make_reuse_compliant(root: Path) -> None:
    """Add REUSE.toml + LICENSES/MIT.txt so ``root`` passes `reuse lint`."""
    build_repo(root, {"REUSE.toml": REUSE_TOML, "LICENSES/MIT.txt": MIT_LICENSE_TEXT})

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


@pytest.fixture
def repo(tmp_path):
    """Return a helper that builds a repo under a fresh subdir of tmp_path."""

    def _build(files: dict[str, str], *, compliant: bool = False, name: str = "r") -> Path:
        root = tmp_path / name
        root.mkdir(exist_ok=True)
        build_repo(root, files)
        if compliant:
            make_reuse_compliant(root)
        return root

    return _build
