# transfer-manifest Specification

## Purpose
TBD - created by archiving change init-core-v1. Update Purpose after archive.
## Requirements
### Requirement: Transfer manifest schema

The system SHALL define a `TransferManifest` model using `pydantic` v2 that
captures the declared information needed to transfer a project. Field names
SHALL align with `publiccode.yml` where an equivalent concept exists.

The model SHALL include: `name`, `licence` (SPDX identifier), `owner`,
`contact`, `status` (one of `concept`, `poc`, `beta`, `stable`, `obsolete`),
optional `deps`, optional `deployment_target`, and an optional `data` object
(`schema`, `volume`, `sensitivity`, `synthetic_data`).

#### Scenario: Valid manifest parses

- **WHEN** a YAML manifest containing all required fields with valid values is loaded
- **THEN** a `TransferManifest` instance is produced with those values

#### Scenario: Missing required field is rejected

- **WHEN** a YAML manifest omits a required field (e.g. `contact`)
- **THEN** validation fails with an error identifying the missing field

#### Scenario: Invalid status is rejected

- **WHEN** a manifest sets `status` to a value outside the allowed enum
- **THEN** validation fails with an error identifying the invalid value and the allowed set

### Requirement: Manifest loading

The system SHALL load a manifest from a YAML file path, defaulting to
`transfer.yaml` in the target repository and overridable via `--manifest`.

#### Scenario: Default manifest path

- **WHEN** no `--manifest` option is given and `transfer.yaml` exists in the target
- **THEN** that file is loaded as the manifest

#### Scenario: Missing manifest file

- **WHEN** the resolved manifest path does not exist
- **THEN** the system reports an actionable error naming the expected path, and does not crash with a raw traceback

