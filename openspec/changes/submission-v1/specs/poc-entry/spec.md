## MODIFIED Requirements

### Requirement: Loading entries

The system SHALL load PoC entries from YAML files under a catalog directory and
SHALL merge them with entries obtained from harvested remote sources into one
entry set, skipping unparseable or invalid entries rather than failing the whole
load. When a harvested entry and a local entry share the same name, the local
`catalog/*.yaml` entry SHALL take precedence (local is authoritative). The merged
set SHALL be deterministic (sorted, no timestamps).

#### Scenario: Unparseable entry is skipped

- **WHEN** one entry file is invalid YAML
- **THEN** the other entries still load and the invalid one is skipped

#### Scenario: Local and harvested entries merge

- **WHEN** the catalog directory has local entries and harvested entries are present
- **THEN** the loader returns one set containing both, sorted deterministically

#### Scenario: Local entry wins a name collision

- **WHEN** a harvested entry has the same name as a local `catalog/*.yaml` entry
- **THEN** the local entry is used and the harvested duplicate is dropped
