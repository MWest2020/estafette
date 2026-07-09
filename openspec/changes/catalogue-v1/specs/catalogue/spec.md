## ADDED Requirements

### Requirement: Static catalogue generation

The system SHALL provide a command `estafette catalogue` that reads every
`report.json` under a reports directory and renders a static site (an index page
plus a per-report detail page) using only self-contained HTML and inline CSS —
no server, no database engine, and no web framework.

#### Scenario: Index lists assessed PoCs

- **WHEN** `estafette catalogue --reports-dir <dir> --out <site>` runs over a directory containing reports
- **THEN** `<site>/index.html` is written listing each report's PoC name, bronze verdict, and commit, each linking to its detail page

#### Scenario: Detail page per report

- **WHEN** the catalogue is generated
- **THEN** each report has a detail page showing its criteria, per-check gaps, and the silver preview

#### Scenario: Empty reports directory

- **WHEN** the reports directory contains no reports
- **THEN** the command writes an index page stating there are no reports yet, and does not crash

### Requirement: Deterministic site

The generated site SHALL be deterministic: the same set of reports SHALL produce
byte-identical output (invariant I5). No build timestamps or absolute paths SHALL
appear in the output.

#### Scenario: Same reports reproduce the site

- **WHEN** the catalogue is generated twice from the same reports
- **THEN** the two `index.html` outputs are byte-identical
