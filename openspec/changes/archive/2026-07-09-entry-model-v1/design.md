## Context

The reframe makes the catalogue the product and the verdict a bonus. publiccode.yml
(verified against yml.publiccode.tools) is software-only — `url` + `softwareType`
mandatory, statuses `concept/development/beta/stable/obsolete` (no `poc`), and no
outcome/conclusion field. So it cannot represent a findings-only PoC or an
experiment's conclusion. Those two gaps are the only things the entry adds.

## Goals / Non-Goals

**Goals:**

- A `PoCEntry` that reuses publiccode.yml by reference and adds only `kind` +
  `conclusion`.
- Findings-only PoCs as first-class catalogue entries.
- Catalogue renders entries; verdict is an optional badge.

**Non-Goals:**

- No forking/duplicating of the publiccode.yml schema.
- No submission/hosting/harvester yet (next design step).
- No publiccode.yml export or OpenCatalogi integration in this change.

## Decisions

- **Wrap publiccode, don't fork it (I2).** For software, the entry points at a
  real publiccode.yml via `publiccode`; OpenCatalogi already reads those. The
  entry never redefines publiccode's fields.
- **Entry carries a small uniform identity** (`name`, `owner`, `contact`,
  `status`) so findings-only and code entries render identically in the index,
  and findings entries (which have no publiccode.yml) are still attributable. The
  mild overlap with publiccode for code entries is accepted; when a publiccode
  ref exists it is the source of truth for software metadata.
- **Keep the PoC-oriented `status`** (reuses the manifest `Status`, incl. `poc`).
  publiccode lacks `poc`; mapping poc→concept/development belongs to a future
  exporter, not here.
- **`conclusion` is required and first-class.** It is the star of a PoC ("vooral
  de conclusie"); the index shows a snippet, the detail page shows it prominently.
- **Assessment by reference, optional.** An entry may point at a `report.json`;
  the catalogue loads it for the badge + check detail. No assessment → still
  catalogued, no badge (verdict is a bonus).
- **Entries are portable YAML under `catalog/`.** Each org can host its own entry
  file in its own repo; a future harvester/submission flow aggregates them —
  exactly the OpenCatalogi harvest pattern, deferred to its own design.

## Risks / Trade-offs

- **Identity duplication with publiccode** for code entries. Accepted for a
  uniform, self-describing index; a later exporter can derive the entry's
  identity from the referenced publiccode.yml to remove the overlap.
- **Schema will meet real usecases tomorrow.** The fields are deliberately few
  (kind + conclusion + refs); adding a field when a usecase needs it is cheap.
  Locking the *principle* now, not an elaborate schema.
- **`assessment`/`publiccode` path resolution.** Paths are resolved relative to
  the working directory (repo root); documented, and unresolved refs degrade to
  "no badge" rather than crashing.
