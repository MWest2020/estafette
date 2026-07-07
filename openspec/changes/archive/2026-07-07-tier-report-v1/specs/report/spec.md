## ADDED Requirements

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
