## Why

The catalogue can *show* PoC entries but there is still no way for other
organisations to *contribute* them — the "platform to share" half of the ask.
`project.md` and `docs/catalog-spec.md` both name this as the deferred "next
design step": how entries are **submitted / hosted / harvested**. Today
`catalog/` holds exactly one entry (estafette assessing itself); a catalogue of
one is not a platform. Mark's decision: build the two standard on-ramps — **PR
submission** and a **crawl/harvester** — in their simplest honest form.

## What Changes

- **PR submission (open, zero infra).** Anyone adds a `catalog/*.yaml` entry via
  a pull request. A CI job validates every entry against the `PoCEntry` schema
  and fails the PR with an actionable message on an invalid entry, so review is
  the only gate. A `CONTRIBUTING`/how-to-submit doc explains the flow.
- **Crawl / harvester (pull).** A configured list of **repos** (`sources.yaml`)
  is crawled by `estafette harvest`, which fetches each repo's well-known
  `poc.yaml` (falling back to `publiccode.yml`, wrapped as `kind: code`) and
  aggregates the entries — leniently, per the existing loader contract — into the
  entry set the catalogue renders. `poc.yaml` is the direct analog of
  `publiccode.yml`: a well-known file each PoC hosts on its own repo root, so
  discovery is by convention, not a hand-maintained URL list (invariant I2:
  orchestrate, don't reinvent).
- **One entry set feeds the site.** Local `catalog/*.yaml` and harvested entries
  merge into the same list `estafette catalogue` already renders. No server, no
  DB, deterministic output (I5): sources are sorted, fetch failures are skipped
  with a recorded note, no timestamps leak in.
- Seed `sources.yaml` with a documented example (and estafette's own entry as a
  self-reference), and update the Pages workflow to harvest-then-build.

## Capabilities

### New Capabilities

- `submission`: how PoC entries enter the catalogue — PR-based submission
  (schema validation in CI + contributor docs) and a crawl/harvester
  (`sources.yaml` repo list + a well-known `poc.yaml` per repo + `estafette
  harvest`) that pulls and aggregates entries from many orgs.

### Modified Capabilities

- `poc-entry`: the entry loader gains a **source** dimension — entries load not
  only from a local catalog directory but also from harvested remote sources,
  merged leniently into one set (a failed source is skipped, not fatal).

## Impact

- **New code:** `src/estafette/harvest.py` (source-list model + fetcher +
  aggregation); a `harvest` subcommand in `cli.py`; entry-validation hook reused
  by the CI job.
- **New content/config:** `sources.yaml` (repo list); a `poc.yaml` convention
  documented for hosting repos; a contributor doc (`docs/submitting.md` or
  `CONTRIBUTING.md`).
- **CI:** a workflow that validates `catalog/*.yaml` on PRs; `pages.yml` runs
  `estafette harvest` before `estafette catalogue`.
- **Docs:** `docs/catalog-spec.md` "next design step" section resolved;
  `project.md` platform note updated (harvester built, not deferred).
- **Tests:** entry validation surfaces actionable errors; source-list (repo)
  parsing; harvest fetches `poc.yaml` with publiccode.yml fallback, merges local
  + remote, and skips a failing/invalid source; determinism of the merged set.
- **Out of scope:** any login/auth or push-based submission service (breaks
  "no server"); publiccode.yml *export* and live OpenCatalogi *integration*
  (runs elsewhere). Network fetch in `harvest` is a CLI/CI action, never part of
  the verdict path (I6 untouched).
