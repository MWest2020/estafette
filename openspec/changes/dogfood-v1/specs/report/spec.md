## ADDED Requirements

### Requirement: Committed real-world report

The repository SHALL contain, under `reports/`, at least one real
transferability report produced by estafette on an actual project. The report
SHALL be reproducible (byte-identical body for its recorded commit and estafette
version) and human-readable top to bottom. Any sensitive detail SHALL be
anonymised before committing.

#### Scenario: The annex report exists and is reproducible

- **WHEN** the committed real report's commit is re-assessed with the recorded estafette version
- **THEN** the regenerated report body is byte-identical to the committed one

#### Scenario: The report is self-contained for a reviewer

- **WHEN** a disclosure-minded reviewer opens the committed `report.md`
- **THEN** they can read the commit, what passed, every gap with a concrete remediation, the bronze verdict, and the informational silver preview, without other context
