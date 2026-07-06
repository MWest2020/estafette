## MODIFIED Requirements

### Requirement: assess command surface

The system SHALL expose a console command `estafette assess <path|git-url>`
accepting an optional `--manifest <path>` option. The command loads and
validates the manifest, then runs the static checks and prints, per check, its
status and any gaps, plus the versions of the external tools used. It SHALL NOT
emit a tier verdict (that arrives in `tier-report-v1`).

#### Scenario: assess with a valid manifest runs checks

- **WHEN** `estafette assess <path>` is run against a repository with a valid manifest
- **THEN** the command runs the static checks and prints each check's status and gaps, and exits 0 when the command itself completed (regardless of individual check outcomes)

#### Scenario: assess with an invalid manifest

- **WHEN** `estafette assess <path>` is run and the manifest fails validation
- **THEN** the command exits non-zero and prints the validation error as an actionable message, without running checks

#### Scenario: assess with a missing external tool

- **WHEN** a required external tool is not installed
- **THEN** the command exits non-zero with a clear message naming the missing tool

### Requirement: No fake verdicts

The CLI SHALL NOT print a tier verdict or any tier name until the tier
capability is implemented. Per-check pass/fail is permitted once the checks
exist; any not-yet-implemented output (currently the tier verdict) MUST be
clearly labelled as such (invariant I1).

#### Scenario: Output has no tier

- **WHEN** the assess command runs before the tier capability exists
- **THEN** its output contains no tier name (e.g. bronze/silver/gold) and clearly states the tier verdict is not yet implemented
