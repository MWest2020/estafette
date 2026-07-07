# cli Specification

## Purpose
TBD - created by archiving change init-core-v1. Update Purpose after archive.
## Requirements
### Requirement: assess command surface

The system SHALL expose a console command `estafette assess <path|git-url>`
accepting an optional `--manifest <path>` option. The command loads and
validates the manifest, runs the static checks, runs the build harness for an
informational silver preview, computes the **bronze verdict**, and writes the
transferability report (`report.json` + `report.md`) under `reports/`. It SHALL
print the bronze verdict and the report path.

#### Scenario: assess emits a bronze verdict and a report

- **WHEN** `estafette assess <path>` runs against a repository with a valid manifest
- **THEN** it prints the bronze verdict, writes `report.json` and `report.md` under `reports/`, and prints the report path

#### Scenario: assess with an invalid manifest

- **WHEN** the manifest fails validation
- **THEN** the command exits non-zero with an actionable message and writes no report

### Requirement: No fake verdicts

The CLI SHALL present only the mechanically-computed bronze verdict; silver and
gold SHALL NOT be presented as gated verdicts (silver remains an informational
preview) until their capabilities are implemented (invariant I1).

#### Scenario: Only bronze is gated

- **WHEN** assess prints its verdict
- **THEN** it states the bronze verdict and shows silver only as an informational preview, with no gold verdict

