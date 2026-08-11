# poc-entry Specification

## Purpose
TBD - created by archiving change entry-model-v1. Update Purpose after archive.
## Requirements
### Requirement: PoC entry descriptor

The system SHALL define a `PoCEntry` model with `name`, `owner`, `contact`,
`status`, a `kind` (`code | findings | both`), and a required non-empty
`conclusion`. It MAY carry links (`repo`, `doc`, `demo`), an optional
`publiccode` reference to a real publiccode.yml, and an optional `assessment`
reference to an estafette report. The model SHALL NOT duplicate publiccode.yml's
software schema — it references it (invariant I2).

#### Scenario: Findings-only entry is valid without a repo

- **WHEN** an entry has `kind: findings`, a conclusion, and no repo/publiccode
- **THEN** it validates and is a first-class catalogue entry

#### Scenario: Conclusion is required

- **WHEN** an entry omits `conclusion` (or leaves it empty)
- **THEN** validation fails with an actionable error

#### Scenario: Invalid kind is rejected

- **WHEN** `kind` is a value outside `code | findings | both`
- **THEN** validation fails naming the allowed values

### Requirement: Assessment is optional enrichment

The catalogue SHALL show an entry's verdict when the entry references an
estafette assessment, and SHALL still catalogue entries that reference none. A
verdict is a bonus, never a requirement for sharing (platform-first reframe).

#### Scenario: Entry without an assessment is still catalogued

- **WHEN** an entry has no `assessment` reference
- **THEN** it appears in the catalogue with its conclusion and no verdict badge

#### Scenario: Entry with an assessment shows the verdict

- **WHEN** an entry references a valid report.json
- **THEN** its catalogue entry shows the bronze verdict from that report

### Requirement: Loading entries

The system SHALL load PoC entries from YAML files under a catalog directory and
SHALL merge them with entries obtained from harvested remote sources into one
entry set, skipping unparseable or invalid entries rather than failing the whole
load. When a harvested entry and a local entry share the same name, the local
`catalog/*.yaml` entry SHALL take precedence (local is authoritative). The merged
set SHALL be deterministic (sorted, no timestamps).

#### Scenario: Unparseable entry is skipped

- **WHEN** one entry file is invalid YAML
- **THEN** the other entries still load and the invalid one is skipped

#### Scenario: Local and harvested entries merge

- **WHEN** the catalog directory has local entries and harvested entries are present
- **THEN** the loader returns one set containing both, sorted deterministically

#### Scenario: Local entry wins a name collision

- **WHEN** a harvested entry has the same name as a local `catalog/*.yaml` entry
- **THEN** the local entry is used and the harvested duplicate is dropped

