# report Specification

## Purpose
TBD - created by archiving change tier-report-v1. Update Purpose after archive.
## Requirements
### Requirement: Transferability report content

The system SHALL produce a `TransferabilityReport` rendered to both
`report.json` and a human-readable `report.md`. Both SHALL include the target
commit hash, the versions of every tool used, per-check status and evidence, the
full gap list, the informational silver preview, and the bronze verdict.

#### Scenario: Report includes provenance and verdict

- **WHEN** a report is generated for a target
- **THEN** it contains the commit hash, tool versions, per-check results, gaps, the silver preview, and the bronze verdict

#### Scenario: Human report is readable top to bottom

- **WHEN** `report.md` is generated
- **THEN** a reviewer can read commit, what passed, every gap with a concrete remediation, and the verdict, in order

### Requirement: Deterministic report body

For a given target commit and estafette version, the report body SHALL be
byte-identical across runs (invariant I5). Non-deterministic values (wall-clock
timings, absolute temporary paths) SHALL NOT appear in the body.

#### Scenario: Same commit reproduces the body

- **WHEN** the same commit is assessed twice with the same estafette version
- **THEN** the two report bodies are byte-identical

### Requirement: Append-only reports

Reports SHALL accumulate under `reports/` and SHALL never be overwritten
(invariant I5). A run SHALL NOT silently replace an existing differing report.

#### Scenario: Existing report is not clobbered

- **WHEN** a report already exists and a new run would differ from it
- **THEN** the new report is written without destroying the existing one

### Requirement: Commit hash capture

The system SHALL record the target's commit hash. When the target is not a git
repository, the report SHALL record that fact honestly rather than fabricating a
hash.

#### Scenario: Non-git target

- **WHEN** the target is not a git repository
- **THEN** the report records the commit as unavailable rather than inventing one

### Requirement: Committed real-world report

The repository SHALL contain, under `reports/`, at least one real
transferability report produced by estafette on an actual project. The report
SHALL be reproducible (byte-identical body for its recorded commit and estafette
version) and human-readable top to bottom. Any sensitive detail SHALL be
anonymised before committing.

#### Scenario: The annex report exists and is reproducible

- **WHEN** the committed real report's commit is re-assessed with the recorded estafette version
- **THEN** the regenerated report body is byte-identical to the committed one

#### Scenario: The report is self-contained for a reviewer

- **WHEN** a disclosure-minded reviewer opens the committed `report.md`
- **THEN** they can read the commit, what passed, every gap with a concrete remediation, the bronze verdict, and the informational silver preview, without other context

