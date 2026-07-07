# build-harness Specification

## Purpose
TBD - created by archiving change harness-v1. Update Purpose after archive.
## Requirements
### Requirement: Isolated two-stage execution

The harness SHALL build and run the target using rootless `podman` in two
stages. The **build stage** MAY access the network to fetch dependencies. The
**run stage** SHALL execute with `--network=none`, with CPU, memory, and
wall-clock caps, with no host environment variables and no secrets passed in,
and with any target mount bound read-only (invariant I4).

#### Scenario: Run stage has no network

- **WHEN** the harness runs the target
- **THEN** the run stage is executed with networking disabled, so untrusted code cannot reach the network

#### Scenario: Resource caps are enforced

- **WHEN** the run stage exceeds its CPU, memory, or wall-clock cap
- **THEN** the harness terminates it and records the cap that was hit

#### Scenario: No host environment leaks in

- **WHEN** the target runs
- **THEN** it receives no host environment variables and no secrets from the estafette process

### Requirement: Reached-running-state verdict

The harness SHALL determine whether the target reached a running state
according to a declared readiness mode: `exits-zero` (the process completes
successfully within the timeout) or `stays-up` (the process is still healthy at
the end of a fixed readiness window). The readiness mode and timeout used SHALL
be recorded.

#### Scenario: Service stays up

- **WHEN** readiness mode is `stays-up` and the container is still running at the end of the window
- **THEN** the harness reports reached-running-state = true

#### Scenario: Process exits non-zero

- **WHEN** the target exits with a non-zero status
- **THEN** the harness reports reached-running-state = false and proceeds to classify the failure

### Requirement: Diagnostic classification

On failure the harness SHALL classify the outcome into exactly one category:
`missing-declared-dep`, `undeclared-system-dep`, `unreachable-internal-service`,
`requires-unavailable-data`, or `other`. Every classification SHALL include an
actionable gap; `other` SHALL additionally carry a captured tail of the logs
(invariant I3). Classification is a pure function of the captured logs so it is
independently testable.

#### Scenario: Missing declared dependency

- **WHEN** the build/run logs show a declared dependency failing to install or import
- **THEN** the outcome is classified `missing-declared-dep` with a gap naming the dependency

#### Scenario: Undeclared system dependency

- **WHEN** the logs show a missing system package or shared library
- **THEN** the outcome is classified `undeclared-system-dep` with a gap naming the system requirement

#### Scenario: Unclassifiable failure keeps evidence

- **WHEN** the failure matches no known category
- **THEN** the outcome is classified `other` and includes a captured log tail so a human can diagnose it

### Requirement: Silver preview result

The harness SHALL return a `SilverPreview` stating whether the target would pass
silver (reached-running-state with no blocking gaps) plus any gaps. This result
is INFORMATIONAL in v1 and MUST NOT be presented as a gated tier verdict
(invariant I1).

#### Scenario: Would pass silver

- **WHEN** the target builds and reaches a running state with no blocking gaps
- **THEN** the silver preview says it would pass silver

### Requirement: Graceful degradation without podman

When rootless `podman` is not installed or not usable, the harness SHALL return
a silver preview of "unavailable" naming the reason, and SHALL NOT raise a hard
error — the bronze verdict does not depend on the harness in v1.

#### Scenario: Podman absent

- **WHEN** podman is not installed
- **THEN** the silver preview is reported as unavailable with the reason, and the overall command still completes

### Requirement: Deterministic preview body

The preview's verdict, classification, and gaps SHALL be deterministic for a
given commit and estafette version (invariant I5). Non-deterministic timing
(wall-clock durations) SHALL be recorded as evidence only and kept out of the
byte-identical report body.

#### Scenario: Timing excluded from reproducible body

- **WHEN** the same commit is assessed twice with the same estafette version
- **THEN** the deterministic preview body is identical, even though measured durations differ

