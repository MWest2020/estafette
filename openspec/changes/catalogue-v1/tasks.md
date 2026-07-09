## 1. Catalogue generation

- [x] 1.1 Implement `catalogue.py`: `load_reports(reports_dir) -> list[TransferabilityReport]` (lenient; skip unparseable)
- [x] 1.2 Render `index.html`: table of PoC name, bronze verdict badge, commit, gap count, link to detail
- [x] 1.3 Render a detail page per report (criteria, per-check gaps, silver preview)
- [x] 1.4 Escape all injected text (`html.escape`); inline CSS; no external assets
- [x] 1.5 Deterministic: sort by (name, commit); no timestamps/absolute paths
- [x] 1.6 Empty reports dir → valid "no reports yet" index, no crash

## 2. CLI

- [x] 2.1 Add `estafette catalogue [--reports-dir reports] [--out site]`
- [x] 2.2 Print the output path and the number of reports rendered

## 3. Tests

- [x] 3.1 Fixture reports dir → index lists PoC names + verdict; detail pages exist
- [x] 3.2 Determinism: two runs → byte-identical `index.html`
- [x] 3.3 Empty reports dir handled; a name with HTML characters is escaped

## 4. Pages + docs

- [x] 4.1 Add `.github/workflows/pages.yml` (build site from `reports/`, deploy to Pages)
- [x] 4.2 Update `project.md` (v2 begun; catalogue in scope as a CLI-emitted static artifact)
- [x] 4.3 README: catalogue usage + Pages link; note the one-time Pages enablement
- [x] 4.4 `ruff` + `pytest` green; every module ≤ 200 lines (I7); CI stays green
