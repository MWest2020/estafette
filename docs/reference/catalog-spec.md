---
status: draft
last_reviewed: 2026-07-12
---

# PoC catalogue — entry specification

The catalogue's unit is a **PoC entry**: a shareable proof of concept that
delivered code, only findings, or both. The transferability *verdict* is an
optional badge, not a requirement for being catalogued.

Entries are YAML files under `catalog/` (one per PoC). The authoritative schema
is `src/estafette/entry.py`; this document explains it.

## Not reinventing publiccode.yml

[`publiccode.yml`](https://yml.publiccode.tools/) already describes public-sector
*software*, and OpenCatalogi federates it. But it is **software-only** (`url` and
`softwareType` are mandatory), has **no `poc` status**, and **no field for a
PoC's conclusion**. So it cannot represent a findings-only PoC or an experiment's
outcome. estafette therefore **wraps** publiccode.yml rather than forking it: an
entry adds only what publiccode lacks (`kind`, `conclusion`) and *references* a
real publiccode.yml for the software metadata.

## Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | PoC name. |
| `owner` | string | yes | Owning organisation/person. |
| `contact` | string | yes | A reachable contact. |
| `status` | enum | yes | `concept` \| `poc` \| `beta` \| `stable` \| `obsolete`. |
| `kind` | enum | yes | `code` \| `findings` \| `both`. |
| `conclusion` | string | yes | **The takeaway of the PoC** — the point of the entry. |
| `repo` | string | no | Link to the code repository. |
| `doc` | string | no | Link to the findings/writeup. |
| `demo` | string | no | Link to a demo. |
| `publiccode` | string | no | Path/URL to a real `publiccode.yml` (software metadata; OpenCatalogi on-ramp). |
| `assessment` | string | no | Path to an estafette `report.json`; when present, its bronze verdict is shown as a badge. |

## Example (findings-only)

```yaml
name: Address matching spike
owner: Example Municipality
contact: dev@example.gov
status: poc
kind: findings
conclusion: >-
  Fuzzy-matching BAG addresses against the input register hit 92% precision but
  needs a human review step below 0.8 confidence. Not production-ready; the
  register API rate limit (5 req/s) is the real blocker.
doc: https://example.gov/spikes/address-matching.pdf
```

## Rendering

`estafette catalogue --catalog catalog --out site` renders every entry into a
static site: an index (name, kind, status, verdict badge where assessed,
conclusion) and a per-entry detail page (full conclusion, links, and the
assessment criteria when present). Output is deterministic (invariant I5).

## Submission & harvesting

Entries enter the catalogue two ways (see [`../submitting.md`](../submitting.md)):
a **pull request** adding a `catalog/*.yaml` (CI validates it via `estafette
catalogue --check`), or the **harvester** pulling a well-known `poc.yaml` from
each repo listed in `sources.yaml`. Both produce the same `PoCEntry`; only the
ingress differs. Local `catalog/*.yaml` and harvested entries merge into one
deterministic set — the local entry wins on a name collision.

### The `poc.yaml` / `catalog/*.yaml` contract

A `poc.yaml` is nothing more than a `PoCEntry` serialized as a single UTF-8 YAML
document. In a hosting repo it lives at the **repo root** under exactly that
filename; as a local submission it is any `catalog/<name>.yaml`. One
authoritative definition: `src/estafette/entry.py`.

- **Required:** `name`, `owner`, `contact`, `status`
  (`concept|poc|beta|stable|obsolete`), `kind` (`code|findings|both`), and a
  non-empty `conclusion` (the PoC's takeaway — the star of the entry).
- **Optional:** `repo`, `doc`, `demo`, `publiccode`, `assessment`.
- A file that is **missing, unparseable, or schema-invalid is skipped with a
  recorded reason** — never fatal (I3). A repo that also carries a
  `publiccode.yml` needs no duplication: `poc.yaml` wins, publiccode is only the
  fallback (wrapped as `kind: code`, marked auto-derived).

```yaml
# poc.yaml (repo root) — or catalog/my-poc.yaml
name: My PoC
owner: My Org
contact: https://github.com/my-org/my-poc/issues
status: poc
kind: findings
conclusion: >-
  One paragraph: what we tried, what we learned, whether it is worth adopting.
repo: https://github.com/my-org/my-poc
```

### Harvester limits & compute

- **Where it runs.** `estafette harvest` is a stateless CLI step, run in GitHub
  Actions (the Pages workflow, `harvest` before `catalogue`) — **not on our
  cluster**. It can equally run on a workstation or via cron; nothing requires a
  server or persistent state.
- **Raw fetch, not the GitHub API.** Each repo costs a plain HTTPS GET on the raw
  path (`.../HEAD/poc.yaml`, then `.../publiccode.yml` as fallback) — 1–2 requests
  per repo. This avoids the API's rate ceilings; `raw.githubusercontent.com` has
  only soft abuse limits a curated list never approaches, and raw paths are
  host-agnostic (GitLab/Gitea work the same). Request count is strictly
  `O(repos) × (1–2)` — no pagination, recursion, or org enumeration.
- **Self-imposed caps.** A per-fetch size cap (~512 KB) and timeout; a source that
  exceeds either is skipped with a reason. No auth, public repos only. No code
  execution (I6): only declared fields are read into the pydantic model.
- **When the API becomes necessary (future, out of scope).** Moving from a
  hand-listed **repo** list to an **org crawl** ("find every repo in these orgs
  with a `poc.yaml`") needs repo enumeration via the GitHub API — a token and its
  1000–5000/hour ceiling. That is a separate future change; v1 stays on the
  limit-free repo list.
