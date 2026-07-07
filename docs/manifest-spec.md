# Transfer manifest specification

**Status:** draft for `init-core-v1`. The authoritative schema is the
`pydantic` model in `src/estafette/manifest.py`; this document explains it.

The **transfer manifest** is the declared, machine-readable answer to *"what
would someone need in order to take this over?"* Estafette compares this
declaration against the mechanical reality of the repository and reports the
gaps.

## Design stance

The manifest is deliberately an **extension profile of
[`publiccode.yml`](https://yml.publiccode.tools/)**, not a competitor. Where a
concept already exists in publiccode.yml, estafette **aligns field names**
rather than inventing new ones. Estafette adds only the fields needed to make
transferability *mechanically checkable* — chiefly honest status and concrete
data requirements.

The manifest is a YAML file (default name `transfer.yaml`, overridable with
`--manifest`).

## Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Human-readable project name. |
| `licence` | SPDX id (string) | yes | Aligns with `publiccode.yml: legal.license`. Must match the repository's actual licence (checked by `licence_consistency`). |
| `owner` | string | yes | Owning organisation or person. |
| `contact` | string | yes | A reachable contact (email or handle). Non-empty is a bronze criterion (B6). |
| `status` | enum | yes | Honest lifecycle status: `concept` \| `poc` \| `beta` \| `stable` \| `obsolete`. |
| `deps` | list | no | Declared runtime dependencies; compared against imports/lockfiles by `deps_reality`. |
| `deployment_target` | string | no | Where this is meant to run (e.g. `kubernetes`, `docker-compose`, `vm`). Used by gold (roadmap). |
| `data` | object | no | Data requirements — see below. |
| `build` | object | no | How the harness builds and runs the target — see below. |

### `build` — harness recipe

Tells the build harness how to build and run the target (declared, never
guessed). When absent, the silver preview is reported as *not assessable*.

| Field | Type | Notes |
|-------|------|-------|
| `containerfile` | string | Path to a Containerfile/Dockerfile (default detection when omitted). |
| `readiness` | enum | `stays-up` (default) or `exits-zero` — how "reached a running state" is decided. |
| `timeout_seconds` | int | Wall-clock cap / readiness window (default 30). |
| `cpus` | number | CPU cap for the run stage. |
| `memory` | string | Memory cap for the run stage (e.g. `256m`). |

The run stage always executes with no network, no host environment, and a
read-only root filesystem (invariant I4), regardless of these values.

### `data` — data requirements

| Field | Type | Notes |
|-------|------|-------|
| `schema` | string | Reference/description of the data schema required. |
| `volume` | string | Rough size class (e.g. `<1GB`, `1-100GB`, `>100GB`). |
| `sensitivity` | enum | `none` \| `personal` \| `special-category` \| `secret`. |
| `synthetic_data` | boolean | Whether usable synthetic/test data ships with the repo. |

These fields are declarative in v1 and feed the gold tier (roadmap). They are
recorded in the report so a reviewer sees them even before gold is enforced.

## Example

```yaml
name: Example PoC
licence: EUPL-1.2
owner: Example Municipality
contact: dev@example.gov
status: poc
deps:
  - fastapi
  - pydantic
deployment_target: docker-compose
data:
  schema: "OpenAPI 3 person record"
  volume: "<1GB"
  sensitivity: personal
  synthetic_data: true
```

## Validation

`estafette assess` loads the manifest and validates it against the schema.
Bronze criterion **B5** requires the manifest to be present and valid; **B6**
requires `contact`/`owner` to be non-empty. Validation errors are reported as
actionable gaps (invariant **I3**), never bare failures.
