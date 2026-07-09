## Why

v1 delivered the engine: `assess` produces a deterministic `report.json` per PoC
per commit under `reports/`. That directory is already a version-controlled,
machine-readable **database** of assessments. The product the grant funds is a
**platform that shows the assessed PoCs** — and in its simplest honest form that
is just a static page rendered from those reports. No server, no framework, no
real database: `reports/` *is* the database, and a static site is the view.

This is the first v2 change. It supersedes the v1 scope line "no catalogue"
(project.md) — but not "estafette is a CLI": the catalogue is a **static
artifact the CLI emits**, nothing runs dynamically.

## What Changes

- Add `estafette catalogue [--reports-dir reports] [--out site]`: read every
  `report.json` under the reports directory and render a **static site** — an
  `index.html` listing each PoC (name, tier verdict, commit, gap summary, link)
  plus a per-report detail page. Plain HTML + inline CSS; no JS framework, no
  network assets.
- Keep it **deterministic** (invariant I5): the same reports produce a
  byte-identical site; no build timestamps in the output.
- Add a GitHub Pages workflow that builds the site from `reports/` and deploys
  it — static hosting, still no server.
- Update `project.md`: v2 begun; catalogue is in scope as a CLI-emitted static
  artifact.

## Capabilities

### New Capabilities

- `catalogue`: the `estafette catalogue` command and its deterministic static
  site generation from the report database.

## Impact

- **New code:** `src/estafette/catalogue.py` (load + render); a `catalogue` command in `cli.py`.
- **New CI:** `.github/workflows/pages.yml` (build + deploy to GitHub Pages).
- **Docs:** `project.md` v2 note; README section on the catalogue/Pages.
- **Tests:** render from a fixture reports dir (index + detail present, tier shown); determinism (two runs byte-identical); empty reports dir handled gracefully.
- **No** server, database engine, or web framework — `reports/` in git is the datastore, output is static HTML.
- **Superseded:** the v1 "no catalogue / full stop" scope line; "estafette is a CLI" still holds (the site is generated output).
