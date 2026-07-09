"""PoC entry — the unit of the catalogue (platform-first reframe).

Wraps publiccode.yml by reference rather than duplicating it (invariant I2):
publiccode.yml is software-only, has no `poc` status and no conclusion field, so
a PoC entry adds exactly what it lacks — `kind` and `conclusion` — and points at
a real publiccode.yml (for code) and an estafette assessment (for the verdict).
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from estafette.manifest import Status


class Kind(StrEnum):
    code = "code"
    findings = "findings"
    both = "both"


class PoCEntry(BaseModel):
    """A shareable proof of concept: code, findings, or both."""

    name: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    contact: str = Field(min_length=1)
    status: Status
    kind: Kind
    conclusion: str = Field(min_length=1)  # the star — the PoC's takeaway
    repo: str | None = None
    doc: str | None = None
    demo: str | None = None
    publiccode: str | None = None  # reference to a real publiccode.yml (software)
    assessment: str | None = None  # reference to an estafette report.json (verdict)


def load_entries(catalog_dir: Path) -> list[PoCEntry]:
    """Load PoC entries from ``*.yaml`` under ``catalog_dir``, skipping bad ones."""
    entries: list[PoCEntry] = []
    if not catalog_dir.is_dir():
        return entries
    for path in sorted(catalog_dir.glob("*.yaml")):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            entries.append(PoCEntry.model_validate(raw))
        except (yaml.YAMLError, ValueError, OSError, ValidationError):
            continue
    return sorted(entries, key=lambda e: e.name)
