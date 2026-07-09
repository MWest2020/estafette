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

## Out of scope (next design step)

How entries are **submitted/hosted/harvested** — open vs login, push vs crawl —
is a separate design. Because entries are portable YAML any org can host in its
own repo, a future harvester can aggregate them, the same way OpenCatalogi
harvests publiccode.yml.
