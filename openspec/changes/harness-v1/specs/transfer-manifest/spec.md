## ADDED Requirements

### Requirement: Build section

The manifest MAY include an optional `build` section that tells the harness how
to build and run the target — declared, not guessed. It MAY specify:
`containerfile` (path to a Containerfile/Dockerfile, with sensible default
detection), `readiness` (`exits-zero` | `stays-up`), `timeout_seconds`, and
resource caps (`cpus`, `memory`). When absent, the harness reports the silver
preview as not assessable rather than guessing.

#### Scenario: Build section parses

- **WHEN** a manifest includes a `build` section with a containerfile and readiness mode
- **THEN** it validates and the values are available to the harness

#### Scenario: Build section is optional

- **WHEN** a manifest omits the `build` section
- **THEN** the manifest still validates, and the harness reports silver as not assessable (no build recipe)

#### Scenario: Invalid readiness mode is rejected

- **WHEN** `build.readiness` is set to a value outside the allowed set
- **THEN** manifest validation fails with an actionable error naming the allowed values
