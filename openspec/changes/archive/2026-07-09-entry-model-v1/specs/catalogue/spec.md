## MODIFIED Requirements

### Requirement: Static catalogue generation

The system SHALL provide a command `estafette catalogue` that reads the **PoC
entries** under a catalog directory and renders a static site (an index page
plus a per-entry detail page) using only self-contained HTML and inline CSS — no
server, no database engine, and no web framework. Every entry SHALL be listed
with its conclusion; entries that reference an assessment SHALL show the bronze
verdict badge; findings-only entries SHALL appear without a badge.

#### Scenario: Index lists all entries with conclusions

- **WHEN** `estafette catalogue --catalog <dir> --out <site>` runs over a directory of entries
- **THEN** `<site>/index.html` lists every entry with its name, kind, and conclusion, each linking to its detail page

#### Scenario: Verdict badge only where assessed

- **WHEN** one entry references an assessment and another (findings-only) does not
- **THEN** the first shows a bronze verdict badge and the second shows none, and both are listed

#### Scenario: Empty catalog directory

- **WHEN** the catalog directory contains no entries
- **THEN** the command writes an index page stating there are no entries yet, and does not crash
