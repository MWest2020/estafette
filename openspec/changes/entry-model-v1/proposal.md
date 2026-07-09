## Why

The platform-first reframe: the catalogue is the product, and a PoC may deliver
**code, only findings, or both**. The mechanical verdict is now an optional
*badge*, not a gate. The catalogue's unit therefore becomes a **PoC entry**, not
an assessment.

We must not reinvent the wheel (invariant I2). publiccode.yml already describes
public-sector *software* — and OpenCatalogi already federates it. But
publiccode.yml is **software-only** (`url` and `softwareType` are mandatory), has
**no `poc` status** (`concept/development/beta/stable/obsolete`), and has **no
field for a PoC's conclusion / findings**. So it cannot hold a findings-only PoC,
nor the experiment outcome. Those two gaps are exactly what a PoC catalogue adds.

So: **wrap publiccode.yml, don't fork it.** The PoC entry adds only what
publiccode cannot express — `kind` and `conclusion` — and *references* a real
publiccode.yml (for code) and an estafette assessment (for the verdict).

## What Changes

- Add a `PoCEntry` model (pydantic v2): `name`, `owner`, `contact`, `status`,
  `kind` (`code | findings | both`), a required **`conclusion`** (the star),
  optional links (`repo`, `doc`, `demo`), an optional `publiccode` reference
  (path/URL to a real publiccode.yml — the OpenCatalogi on-ramp), and an optional
  `assessment` reference (path to an estafette `report.json`).
- Entries live as YAML files under `catalog/` — portable, git-hostable per org
  (this is what a future harvester/submission flow will aggregate).
- Rework `estafette catalogue` to render **entries**: every entry is listed with
  its conclusion; findings-only entries have no badge; entries that reference an
  assessment show the bronze badge and check detail.
- Seed `catalog/estafette.yaml` (kind `code`, referencing the committed report).
- Update the Pages workflow to build from `catalog/`.

## Capabilities

### New Capabilities

- `poc-entry`: the PoC entry descriptor — code/findings/both, a required
  conclusion, and references to publiccode.yml and an estafette assessment.

### Modified Capabilities

- `catalogue`: renders PoC entries (not raw reports); the verdict is an optional
  badge on entries that carry an assessment.

## Impact

- **New code:** `src/estafette/entry.py`; reworked `src/estafette/catalogue.py`; `catalogue --catalog` in `cli.py`.
- **New content:** `catalog/estafette.yaml`; a future `catalog/*.yaml` per submitted PoC.
- **CI:** `pages.yml` builds from `catalog/`.
- **Docs:** `docs/catalog-spec.md`; `project.md` platform note.
- **Tests:** entry validation (findings-only valid without repo; missing conclusion rejected); catalogue renders entries (badge only where an assessment exists); determinism.
- **Out of scope (next design step):** the **submission / hosting / harvester** ("watcher") that ingests entries from many orgs — login vs open, push vs crawl — to be thought out. Also: publiccode.yml *export* and OpenCatalogi *integration* (the latter runs elsewhere; Conduction repos are not operable from this agent).
