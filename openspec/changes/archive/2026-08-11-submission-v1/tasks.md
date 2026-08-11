## 1. PR submission validation

- [x] 1.1 Add a strict entry-validation path (e.g. `estafette catalogue --check` or `estafette validate --catalog <dir>`) that loads `catalog/*.yaml` strictly and exits non-zero naming the first invalid file + reason; exits zero with a count when all valid
- [x] 1.2 Reuse `entry.py` `PoCEntry` for validation — no second schema
- [x] 1.3 Tests: empty `conclusion` fails with the file named; a valid set passes with a count
- [x] 1.4 CI workflow `.github/workflows/validate-catalog.yml` runs the check on PRs touching `catalog/**`

## 2. Source list + harvester

- [x] 2.1 `harvest.py`: `Source` (repo base URL) model; `load_sources(path)` from `sources.yaml`, actionable error on a malformed source; missing file → empty, no crash
- [x] 2.2 Fetcher: plain HTTP GET on the raw path, size cap, no auth; fetch `poc.yaml` then fall back to `publiccode.yml`; a fetch failure / neither-file returns a skip-reason rather than raising
- [x] 2.3 `poc.yaml` → parse into `PoCEntry`; `publiccode.yml` → wrap into `PoCEntry(kind=code)` deriving name/repo/contact, mark auto-derived (I2)
- [x] 2.4 `harvest(sources, out)` aggregates: sorted order, skip failing/invalid with recorded reason, emit a summary "harvested N of M; skipped X: reason"; deterministic output (no timestamps/abs paths)
- [x] 2.5 Tests: malformed source rejected; missing `sources.yaml` non-fatal; one failing repo skipped others harvest; publiccode fallback wrapped as code; harvest twice → byte-identical

## 3. Merge into the loader + catalogue

- [x] 3.1 Extend entry loading to merge local `catalog/*.yaml` with harvested entries into one deterministic set; local wins on name collision
- [x] 3.2 `estafette harvest` subcommand writing normalised entries where the loader reads them (e.g. gitignored `catalog/.harvested/`); `.gitignore` updated
- [x] 3.3 Tests: local + harvested merge; local entry wins collision; unparseable still skipped

## 4. Config, docs, CI, verification

- [x] 4.1 Seed `sources.yaml` with a documented example repo (+ estafette self-reference); add a root `poc.yaml` for this repo so it is self-harvestable
- [x] 4.2 Contributor doc (`docs/submitting.md` or `CONTRIBUTING.md`): how to submit an entry via PR, the `poc.yaml` convention for hosting repos, and how to add a repo to `sources.yaml`
- [x] 4.3 Document the **`poc.yaml` contract** in `docs/catalog-spec.md`: exact filename + repo-root placement, required vs optional fields, allowed `status`/`kind` values, a copyable example, and "invalid → skipped with a reason"
- [x] 4.4 Document harvester **limits & compute** (raw-fetch not the API; size/timeout caps; `O(repos)×1–2`; org-crawl needs the API — future) in `docs/catalog-spec.md`, and update `project.md` platform note (harvester built, not deferred; resolve the "next design step" section)
- [x] 4.5 `pages.yml`: run `estafette harvest` before `estafette catalogue`
- [x] 4.6 `ruff` + `pytest` green (98 passed, 1 skipped, incl. 17 nieuwe); elke
      module ≤ 200 regels (harvest 200, cli 194, entry 86); live CLI-smoke groen
      (check/harvest/render). CI-green (GitHub Actions) asserted lokaal — de twee
      workflows draaien pas na push.
- [x] 4.7 Verse reviewer + security review: beide PASS. Security-hardening verwerkt:
      https-only scheme-guard + https-only redirects (geen SSRF/file:// pivot),
      `assessment` gestript op geharvestte entries (geen arbitrary file-read), en
      slug-collision-guard in `_write_harvested` (geen dataverlies). Elk met test.
