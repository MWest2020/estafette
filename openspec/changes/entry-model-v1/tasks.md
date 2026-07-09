## 1. PoC entry model

- [x] 1.1 Implement `entry.py`: `Kind` enum (`code|findings|both`) and `PoCEntry` (name, owner, contact, status, kind, conclusion, repo?, doc?, demo?, publiccode?, assessment?)
- [x] 1.2 `conclusion` required non-empty; reuse manifest `Status`
- [x] 1.3 `load_entries(catalog_dir)` from `*.yaml`, lenient (skip unparseable)
- [x] 1.4 Tests: findings-only valid without repo; missing conclusion rejected; invalid kind rejected; loader skips unparseable

## 2. Entry-based catalogue

- [x] 2.1 Rework `catalogue.py` to render entries (index + per-entry detail)
- [x] 2.2 Conclusion shown on every entry (snippet in index, prominent in detail)
- [x] 2.3 If `assessment` resolves to a report.json → bronze badge + check detail; else no badge
- [x] 2.4 Deterministic (sorted; no timestamps/absolute paths); empty catalog → "no entries yet"
- [x] 2.5 Tests: lists all entries; badge only where assessed; determinism; empty

## 3. CLI, seed, Pages

- [x] 3.1 `estafette catalogue [--catalog catalog] [--out site]`
- [x] 3.2 Seed `catalog/estafette.yaml` (kind code, references reports/<commit>/report.json)
- [x] 3.3 Update `pages.yml` to build from `catalog/` (and trigger on `catalog/**`)

## 4. Docs + verification

- [x] 4.1 `docs/catalog-spec.md` (entry fields; publiccode-wrapping principle)
- [x] 4.2 `project.md` platform note (entries; verdict as bonus; harvester deferred)
- [x] 4.3 `ruff` + `pytest` green; every module ≤ 200 lines (I7); CI stays green
