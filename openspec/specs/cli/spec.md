# cli Specification

## Purpose
TBD - created by archiving change init-core-v1. Update Purpose after archive.
## Requirements
### Requirement: assess command surface

The system SHALL expose a console command `estafette assess <path|git-url>`
accepting an optional `--manifest <path>` option. The command loads and
validates the manifest, runs the static checks, and — when possible — runs the
build harness to produce an informational silver preview, printing per-check
status, gaps, tool versions, and the silver preview. It SHALL NOT emit a gated
tier verdict (that arrives in `tier-report-v1`).

#### Scenario: assess prints an informational silver preview

- **WHEN** `estafette assess <path>` runs against a repository whose manifest has a build section and podman is available
- **THEN** the output includes the silver preview (would-pass yes/no + gaps), clearly labelled informational, alongside the static-check results

#### Scenario: assess without podman still completes

- **WHEN** podman is not installed
- **THEN** assess still runs the static checks and prints the silver preview as unavailable, and exits 0 when the command itself completed

#### Scenario: assess with an invalid manifest

- **WHEN** `estafette assess <path>` is run and the manifest fails validation
- **THEN** the command exits non-zero and prints the validation error as an actionable message, without running checks or the harness

### Requirement: No fake verdicts

The CLI SHALL NOT print a tier verdict or any tier name until the tier
capability is implemented. Per-check pass/fail is permitted once the checks
exist; any not-yet-implemented output (currently the tier verdict) MUST be
clearly labelled as such (invariant I1).

#### Scenario: Output has no tier

- **WHEN** the assess command runs before the tier capability exists
- **THEN** its output contains no tier name (e.g. bronze/silver/gold) and clearly states the tier verdict is not yet implemented

