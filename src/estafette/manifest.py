"""The transfer manifest: schema, loading, and validation.

The manifest is an extension profile of publiccode.yml (field names align where
concepts overlap). The authoritative schema is this module; docs/manifest-spec.md
explains it. See invariant I3: validation failures become actionable messages,
never raw tracebacks.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

DEFAULT_MANIFEST_NAME = "transfer.yaml"


class Status(StrEnum):
    """Honest lifecycle status of the project."""

    concept = "concept"
    poc = "poc"
    beta = "beta"
    stable = "stable"
    obsolete = "obsolete"


class Sensitivity(StrEnum):
    """Sensitivity class of the data the project requires."""

    none = "none"
    personal = "personal"
    special_category = "special-category"
    secret = "secret"


class DataRequirements(BaseModel):
    """Declared data requirements (feed the gold tier; roadmap)."""

    model_config = ConfigDict(populate_by_name=True)

    schema_: str | None = Field(default=None, alias="schema")
    volume: str | None = None
    sensitivity: Sensitivity | None = None
    synthetic_data: bool | None = None


class TransferManifest(BaseModel):
    """The declared answer to 'what would someone need to take this over?'."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    licence: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    contact: str = Field(min_length=1)
    status: Status
    deps: list[str] = Field(default_factory=list)
    deployment_target: str | None = None
    data: DataRequirements | None = None


class ManifestError(Exception):
    """Raised for any manifest problem, carrying an actionable message."""


def resolve_manifest_path(target: str, manifest: str | Path | None = None) -> Path:
    """Resolve the manifest path: explicit override, else transfer.yaml in target."""
    if manifest is not None:
        return Path(manifest)
    return Path(target) / DEFAULT_MANIFEST_NAME


def _format_validation_error(exc: ValidationError) -> str:
    lines = ["Manifest failed validation:"]
    for err in exc.errors():
        loc = ".".join(str(x) for x in err["loc"]) or "(root)"
        lines.append(f"  - {loc}: {err['msg']}")
    return "\n".join(lines)


def load_manifest(path: str | Path) -> TransferManifest:
    """Load and validate a manifest from a YAML file.

    Raises ManifestError (with an actionable message) on any failure.
    """
    p = Path(path)
    if not p.exists():
        raise ManifestError(
            f"Manifest not found: {p}. Add a '{DEFAULT_MANIFEST_NAME}' or pass --manifest."
        )
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ManifestError(f"Manifest is not valid YAML ({p}): {exc}") from exc
    if not isinstance(raw, dict):
        raise ManifestError(f"Manifest must be a YAML mapping with fields ({p}).")
    try:
        return TransferManifest.model_validate(raw)
    except ValidationError as exc:
        raise ManifestError(_format_validation_error(exc)) from exc
