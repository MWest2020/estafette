# checks Specification

## Purpose
TBD - created by archiving change checks-static-v1. Update Purpose after archive.
## Requirements
### Requirement: External tool runner

The system SHALL provide a runner that invokes an external tool as a
subprocess, captures the tool's version string, and returns its exit code and
captured output. If the tool is not installed, the runner SHALL raise a clear
estafette-environment error naming the missing tool — never report a pass and
never attribute the absence to the target repository.

#### Scenario: Tool version is captured

- **WHEN** a check runs an installed external tool
- **THEN** the tool's version is captured and made available for the report (invariant I5)

#### Scenario: Missing tool is a loud environment error

- **WHEN** a check requires a tool that is not installed
- **THEN** estafette exits with a clear error naming the tool, and does not emit a pass or a target gap

### Requirement: Static checks conform to the Check protocol

Each static check SHALL implement the `Check` protocol: expose a `name` and a
`run(target) -> CheckResult(status, gaps, evidence)`. On failure a check SHALL
populate `gaps` with actionable items (each with a concrete remediation) and
never return a bare failure (invariant I3). Checks SHALL be independently
runnable and testable.

#### Scenario: A failing check yields actionable gaps

- **WHEN** any static check fails on a target
- **THEN** its `CheckResult` has `status = fail` and at least one gap with a concrete remediation

#### Scenario: A passing check yields evidence

- **WHEN** any static check passes on a target
- **THEN** its `CheckResult` has `status = pass` and evidence describing what was inspected

### Requirement: REUSE compliance check

The system SHALL provide a check that wraps `reuse lint` to determine whether
every file carries licence and copyright information.

#### Scenario: Non-compliant file is reported

- **WHEN** the target has a file lacking licence/copyright information
- **THEN** the check fails with a gap naming the file(s) and how to add the missing info

### Requirement: Licence consistency check

The system SHALL provide an estafette-owned check that compares the declared
licence across the manifest, file headers, `pyproject.toml`/`package.json`, and
the `LICENSE` file, and reports any disagreement.

#### Scenario: Disagreeing licences are reported

- **WHEN** the manifest declares one licence and `pyproject.toml` declares another
- **THEN** the check fails with a gap naming each source and the value it declared

### Requirement: Secrets check

The system SHALL provide a check that wraps `gitleaks` to detect secrets in the
target.

#### Scenario: Planted secret is detected

- **WHEN** the target contains a detectable secret
- **THEN** the check fails with a gap naming the location (path, and line where available) without echoing the secret value

### Requirement: SBOM check

The system SHALL provide a check that wraps `syft` to generate an SBOM,
verifies it generates cleanly, and verifies it matches the manifest's declared
dependencies.

#### Scenario: SBOM does not match declared deps

- **WHEN** the generated SBOM contains a component not present in the declared dependencies (or vice versa)
- **THEN** the check fails with a gap listing the mismatched components

### Requirement: Dependency reality check

The system SHALL provide an estafette-owned check that diffs declared
dependencies against actual imports and lockfiles, in both directions.

#### Scenario: Undeclared dependency is reported

- **WHEN** the code imports a dependency that is not declared
- **THEN** the check fails with a gap of the form "dependency X is used in code but not declared"

#### Scenario: Phantom dependency is reported

- **WHEN** a dependency is declared but never imported or locked
- **THEN** the check fails with a gap naming the unused declared dependency

