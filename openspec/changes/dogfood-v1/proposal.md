## Why

The whole point of v1 is one honest transferability report on one real project,
committed as the annex to the SIDN Pioniers application. This change runs
estafette against a real proof of concept end to end, fixes what the experience
teaches, and commits the (anonymised where needed) report to `reports/`. It is
the acceptance test for the entire v1 engine and the definition-of-done for the
grant deliverable.

## What Changes

- Select ONE real PoC (an own archived PoC, or a public Common Ground / public-
  code project) and author a `transfer.yaml` for it — the honest manifest.
- Run `uvx estafette assess <repo>` end to end (bronze verdict + informational
  silver preview) in under 10 minutes on the alma workstation.
- Fix what dogfooding reveals — bugs, unclear gaps, brittle parsing, poor
  wording — feeding fixes back into the relevant capabilities.
- Commit the resulting `report.md` / `report.json` under `reports/` (anonymised
  where needed) and reference it in the SIDN application.

## Capabilities

### New Capabilities

<!-- None: this change validates existing capabilities end to end and may
     modify them via bug fixes discovered during dogfooding. -->

### Modified Capabilities

- `report`: add the requirement that `reports/` contains at least one real,
  reproducible, human-readable transferability report produced by estafette on
  an actual project — the grant annex.

## Impact

- **New content:** a committed real report under `reports/`, plus the target's `transfer.yaml`.
- **Likely code touches:** small fixes across `checks/`, `harness/`, `report.py`, and wording of gaps — scope discovered during the run, kept minimal.
- **Docs:** README/links referencing the annex report.
- **Constraints:** the target must be one this environment is permitted to operate on; picking it is the first task. Anonymise any sensitive detail before committing (I5 keeps reports safe to commit — secrets are located, never echoed).
- **Definition of done for v1:** met when this report exists, is byte-reproducible, reads top to bottom, and is referenced in the SIDN Pioniers application.
