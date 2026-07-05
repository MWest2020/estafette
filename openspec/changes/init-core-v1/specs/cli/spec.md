## ADDED Requirements

### Requirement: assess command surface

The system SHALL expose a console command `estafette assess <path|git-url>`
accepting an optional `--manifest <path>` option. In this change the command
loads and validates the manifest and prints a placeholder result; it SHALL NOT
emit a tier verdict or run checks.

#### Scenario: assess with a valid manifest

- **WHEN** `estafette assess <path>` is run against a repository with a valid manifest
- **THEN** the command exits 0 and prints the parsed manifest summary plus a clear notice that checks and tier verdict are not yet implemented

#### Scenario: assess with an invalid manifest

- **WHEN** `estafette assess <path>` is run and the manifest fails validation
- **THEN** the command exits non-zero and prints the validation error as an actionable message

### Requirement: No fake verdicts

The CLI SHALL NOT print a tier verdict, pass/fail check status, or any score
until the corresponding capability is implemented. Placeholder output MUST be
clearly labelled as not-yet-implemented (invariant I1).

#### Scenario: Placeholder output is honest

- **WHEN** the assess command runs before checks exist
- **THEN** its output contains no tier name and no per-check pass/fail claim
