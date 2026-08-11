## Context

The catalogue renders `PoCEntry` YAML from a local `catalog/` directory
(`entry.py` + `catalogue.py`, both shipped in `entry-model-v1`). Entries are
deliberately portable YAML so that "any org can host in its own repo" — the
loader is already lenient (skips unparseable files). What is missing is the two
on-ramps that turn a local directory into a shared platform: letting others
submit entries, and pulling entries others host. Both must respect the
invariants — no server, no DB, deterministic static output (I5), orchestrate
don't reinvent (I2), no LLM in any verdict (I6), files ≤200 lines (I7).

## Goals / Non-Goals

**Goals:**
- PR submission: an outside contributor adds `catalog/<poc>.yaml`, and CI
  validates it against `PoCEntry` and fails the PR with an actionable message if
  invalid — review is the only human gate.
- Crawl: `estafette harvest` reads a `sources.yaml` list of **repos**, fetches
  the well-known `poc.yaml` from each (falling back to `publiccode.yml`), and
  merges the results into the entry set the catalogue renders.
- One merged, deterministic entry set (local + harvested) feeds `catalogue`.

**Non-Goals:**
- Any login/auth or push-based submission *service* (a server — out of scope by
  invariant).
- publiccode.yml *export* and live OpenCatalogi *integration* (runs elsewhere).
- Deduplication cleverness, ranking, or a scheduler. Harvest is a plain CLI/CI
  action run on demand.

## Decisions

- **Two mechanisms, one data model.** Both on-ramps produce `PoCEntry` objects
  and feed the existing loader/renderer. PR submission adds a *file* to
  `catalog/`; harvest adds *fetched* entries at build time. No new entry schema.

- **Harvest writes into the same set, not a parallel store.** `estafette
  harvest` fetches sources and yields `PoCEntry` objects that `catalogue` merges
  with local `catalog/*.yaml`. Simplest form: harvest writes normalised entries
  into a gitignored `catalog/.harvested/` (or an out dir) that the loader also
  reads; the local `catalog/*.yaml` remains authoritative on name collision.
  *Alternative rejected:* a separate database or a merged single file — breaks
  "reports/catalog IS the database" simplicity and determinism.

- **`poc.yaml` is the well-known entry file; `sources.yaml` is just a repo
  list.** Mirroring publiccode.yml exactly (I2): a PoC repo hosts a `poc.yaml`
  on its root — same `PoCEntry` schema as a `catalog/*.yaml`, different location.
  `sources.yaml` is therefore only a list of repos (base URLs), *not* a list of
  file URLs with a `type` field. The harvester derives the file to fetch by
  convention. *Alternative rejected:* per-source `type`/`url` — that reinvents
  discovery instead of reusing the publiccode convention, and pushes bookkeeping
  onto submitters.

- **Discovery by convention, publiccode as fallback (I2).** For each repo the
  harvester fetches `poc.yaml`; if absent it fetches `publiccode.yml` and wraps
  it into a `PoCEntry` with `kind: code`, pulling `name`/`repo`/`contact` from
  publiccode fields with `conclusion` derived from its description and marked
  auto-derived. Fetch is a plain HTTP GET on the raw path — no auth, public
  repos only. This is the OpenCatalogi on-ramp made concrete.

- **The `poc.yaml` contract.** A `poc.yaml` is nothing more than a `PoCEntry`
  serialized as YAML, placed at the **repo root** under exactly that filename.
  Same schema as a `catalog/*.yaml`, one authoritative definition (`entry.py`),
  documented once in `docs/catalog-spec.md`:
  - **Required:** `name`, `owner`, `contact`, `status`
    (`concept|poc|beta|stable|obsolete`), `kind` (`code|findings|both`), and a
    non-empty `conclusion`.
  - **Optional:** `repo`, `doc`, `demo`, `publiccode`, `assessment`.
  - Single YAML document, UTF-8. A `poc.yaml` that is missing, unparseable, or
    schema-invalid is **skipped with a recorded reason** — the same lenient
    contract as a local entry (I3). A hosting repo that also carries a
    `publiccode.yml` needs no duplication: `poc.yaml` wins, publiccode is only
    the fallback.

- **Failure is lenient and visible (I3/I5).** A source that 404s, times out, or
  yields an invalid entry is *skipped*, recorded in a harvest summary
  (`harvested N of M sources; skipped X: reason`), and never fails the whole
  build. Determinism: sources processed in sorted order, no timestamps in
  output.

- **CI validation reuses the loader.** The PR-validation job runs a thin
  `estafette` check (e.g. `estafette catalogue --check` or a `validate`
  path) that loads `catalog/*.yaml` strictly and exits non-zero naming the first
  invalid file. Reuses `entry.py` — no second schema.

## Limits & compute

- **Where it runs.** `estafette harvest` is a stateless CLI step. By default it
  runs in **GitHub Actions** (the Pages workflow, `harvest` before `catalogue`)
  on GitHub-hosted runners — **not on our cluster**. It can equally run on the
  cluster or a workstation via cron; nothing in the design requires a server or
  persistent state.

- **Network path: raw fetch, not the GitHub API.** Each repo costs a plain
  HTTPS GET on the raw file path (`.../HEAD/poc.yaml`, then `.../publiccode.yml`
  as fallback) — 1–2 requests per repo. This deliberately avoids the GitHub REST
  API, and therefore avoids its rate ceilings (60/hour unauthenticated, 1000/h
  for the Actions `GITHUB_TOKEN`, 5000/h for a PAT). `raw.githubusercontent.com`
  is a CDN with only soft abuse limits that a curated list never approaches: a
  200-repo `sources.yaml` is ~200–400 GETs, once per build. Raw fetch is also
  host-agnostic (GitLab/Gitea raw paths work the same), where the API would not.

- **Self-imposed caps.** Per-fetch **size cap** (a few hundred KB) and a
  per-fetch **timeout**; a source that exceeds either is skipped with a reason,
  never fatal. No pagination, no recursion, no org enumeration — request count is
  strictly `O(repos) × (1–2)`. No auth, public repos only. No code execution
  (I6): only declared fields are read into the pydantic model.

- **Threshold where the API becomes necessary (open question, out of scope).**
  Moving from a hand-listed **repo** list to an **org crawl** ("find every repo
  in these orgs that has a `poc.yaml`") requires repo enumeration via the GitHub
  API — hence a token and its 1000–5000/hour ceiling. That is a separate future
  change; v1 stays on the limit-free repo list.

## Risks / Trade-offs

- **Network fetch introduces non-determinism** → confine it to `harvest`
  (a CLI/CI step), keep `catalogue` pure over the on-disk entry set, and cache
  harvested entries so a re-render without re-harvest is byte-identical.
- **A malicious/huge remote entry** → harvest only reads declared fields into
  the pydantic model (no code execution, I6 untouched), caps fetch size, and a
  human still reviews what lands in `catalog/` for PR submissions; harvested
  entries are clearly attributed to their source.
- **publiccode → entry mapping is lossy** (no real conclusion) → mark such
  entries as auto-derived so a maintainer can later replace them with a curated
  entry; the code on-ramp is still better than absence.
- **Two mechanisms = more surface** → they share one model, one loader, one
  renderer; only the *ingress* differs, keeping each file ≤200 lines (I7).
