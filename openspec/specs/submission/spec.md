# submission Specification

## Purpose
TBD - created by archiving change submission-v1. Update Purpose after archive.
## Requirements
### Requirement: PR submission is validated in CI

The system SHALL provide a way to validate every `catalog/*.yaml` entry against
the `PoCEntry` schema, suitable for running as a CI job on a pull request. The
check SHALL exit non-zero and name the offending file with an actionable message
when an entry is invalid, so that an invalid submission cannot merge; a valid set
SHALL exit zero.

#### Scenario: Invalid submitted entry fails the check

- **WHEN** the validation check runs over a catalog directory containing an entry with an empty `conclusion`
- **THEN** it exits non-zero and the message names that file and the missing/empty `conclusion`

#### Scenario: Valid submissions pass the check

- **WHEN** the validation check runs over a catalog directory where every entry is schema-valid
- **THEN** it exits zero and reports the number of entries validated

### Requirement: Source list for the harvester

The system SHALL read a `sources.yaml` file listing external **repos** to crawl.
Each source SHALL identify a repo (a base URL); it SHALL NOT require the
submitter to name a file path or declare a file type — the entry file is found by
convention. An unparseable `sources.yaml` or a malformed source entry SHALL
produce an actionable error naming the problem rather than silently harvesting
nothing.

#### Scenario: Malformed source is rejected with an actionable error

- **WHEN** a source entry is missing its repo URL
- **THEN** parsing fails with an error naming the offending entry and the required field

#### Scenario: Missing source list is not fatal

- **WHEN** no `sources.yaml` exists
- **THEN** harvest does nothing and reports that there are no sources, without crashing

### Requirement: The poc.yaml hosting contract is documented

A hosting repo SHALL expose its entry as a file named exactly `poc.yaml` at the
repo root, whose content is a valid `PoCEntry` (same schema as a
`catalog/*.yaml`): required `name`, `owner`, `contact`, `status`, `kind`, and a
non-empty `conclusion`; optional `repo`, `doc`, `demo`, `publiccode`,
`assessment`. This contract SHALL be documented for contributors — required vs
optional fields, allowed enum values, placement, and a copyable example — in the
catalogue documentation. A `poc.yaml` that is missing, unparseable, or
schema-invalid SHALL be skipped with a recorded reason, never failing the harvest.

#### Scenario: The contract is documented with an example

- **WHEN** a contributor reads the catalogue documentation
- **THEN** it states that a hosting repo places a `poc.yaml` at its root, lists the required and optional fields with allowed `status`/`kind` values, and shows a copyable example

#### Scenario: A schema-invalid poc.yaml is skipped

- **WHEN** a harvested repo's `poc.yaml` omits `conclusion`
- **THEN** that source is skipped with a reason and the other sources still harvest

### Requirement: Harvest fetches and aggregates entries

The system SHALL provide an `estafette harvest` command that, for each repo in
`sources.yaml`, fetches the well-known `poc.yaml` from the repo root and produces
`PoCEntry` records merged into the entry set the catalogue renders. When a repo
has no `poc.yaml`, the harvester SHALL fall back to its `publiccode.yml` and wrap
it into a `PoCEntry` with `kind: code` (invariant I2, not forked). A source that
fails to fetch, has neither file, or yields an invalid entry SHALL be skipped and
recorded in a summary, never failing the whole harvest. Repos SHALL be processed
in a deterministic (sorted) order and the output SHALL contain no timestamps or
absolute paths (invariant I5).

#### Scenario: A failing source is skipped, others still harvest

- **WHEN** one repo is unreachable and the others expose a valid `poc.yaml`
- **THEN** the reachable repos are harvested, the failing one is skipped, and the summary reports how many of how many succeeded and why the one was skipped

#### Scenario: poc.yaml is preferred, publiccode.yml is the fallback

- **WHEN** a repo has no `poc.yaml` but does have a `publiccode.yml`
- **THEN** it becomes a `PoCEntry` with `kind: code` deriving name/repo/contact from the publiccode.yml, marked as auto-derived

#### Scenario: Harvest is deterministic

- **WHEN** harvest runs twice over the same sources with the same responses
- **THEN** the two aggregated entry sets are byte-identical

