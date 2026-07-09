## 1. Catalogue generation

- [ ] 1.1 Implement `catalogue.py`: `load_reports(reports_dir) -> list[TransferabilityReport]` (lenient; skip unparseable)
- [ ] 1.2 Render `index.html`: table of PoC name, bronze verdict badge, commit, gap count, link to detail
- [ ] 1.3 Render a detail page per report (criteria, per-check gaps, silver preview)
- [ ] 1.4 Escape all injected text (`html.escape`); inline CSS; no external assets
- [ ] 1.5 Deterministic: sort by (name, commit); no timestamps/absolute paths
- [ ] 1.6 Empty reports dir → valid "no reports yet" index, no crash

## 2. CLI

- [ ] 2.1 Add `estafette catalogue [--reports-dir reports] [--out site]`
- [ ] 2.2 Print the output path and the number of reports rendered

## 3. Tests

- [ ] 3.1 Fixture reports dir → index lists PoC names + verdict; detail pages exist
- [ ] 3.2 Determinism: two runs → byte-identical `index.html`
- [ ] 3.3 Empty reports dir handled; a name with HTML characters is escaped

## 4. Pages + docs

- [ ] 4.1 Add `.github/workflows/pages.yml` (build site from `reports/`, deploy to Pages)
- [ ] 4.2 Update `project.md` (v2 begun; catalogue in scope as a CLI-emitted static artifact)
- [ ] 4.3 README: catalogue usage + Pages link; note the one-time Pages enablement
- [ ] 4.4 `ruff` + `pytest` green; every module ≤ 200 lines (I7); CI stays green
