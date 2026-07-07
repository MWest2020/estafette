# tier Specification

## Purpose
TBD - created by archiving change tier-report-v1. Update Purpose after archive.
## Requirements
### Requirement: Bronze verdict is mechanical

The system SHALL compute the bronze verdict purely from the engine's output:
bronze is reached when every bronze criterion passes. The criteria are B1 REUSE
compliance, B2 licence consistency, B3 no secrets, B4 SBOM generates and matches
declared deps (sbom and deps_reality checks), B5 manifest present and valid, and
B6 contact/owner non-empty. No self-declared or human-judged input SHALL affect
the verdict (invariant I1).

#### Scenario: All criteria pass yields bronze

- **WHEN** every bronze criterion passes for a target
- **THEN** the verdict is bronze

#### Scenario: Any failing criterion withholds bronze

- **WHEN** at least one bronze criterion fails
- **THEN** the verdict is not-bronze, and the report lists which criteria failed with their gaps

### Requirement: Tier semantics are versioned

The tier computation SHALL record the tier-doc version it evaluated against, so
a verdict is reproducible and auditable (invariant I5).

#### Scenario: Verdict records tier version

- **WHEN** a verdict is produced
- **THEN** it carries the tier-doc version used to compute it

