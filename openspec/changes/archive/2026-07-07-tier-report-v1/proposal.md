## Why

Everything is in place to produce a verdict except the verdict itself. This
change assembles the check results into the **bronze tier** and emits the
**transferability report** (`report.json` + `report.md`) — the artefact a
disclosure-minded reviewer reads top to bottom, and the annex to the SIDN
application. It is the last engine change before dogfooding.

## What Changes

- Add `tier.py`: versioned bronze semantics that map the six bronze criteria
  (B1–B6 in `docs/tiers.md`) onto the existing check results plus manifest
  presence, yielding a single mechanical bronze pass/fail (invariant I1). No
  self-declared criteria; the tier is purely a function of the engine's output.
- Add `report.py`: a `TransferabilityReport` (pydantic v2) rendered to
  `report.json` and a human-readable `report.md`. The body includes the target
  commit hash, tool versions, per-check status + evidence, the full gap list,
  the informational silver preview, and the bronze verdict.
- Make the report **deterministic and append-only** (invariant I5): same commit
  + same estafette version → byte-identical body; timing excluded; reports
  accumulate under `reports/` and are never overwritten.
- Extend `assess` to compute the tier and write the report, printing the bronze
  verdict and the report path.
- Cut `docs/tiers.md` to v1.0 (bronze normative and implemented).

## Capabilities

### New Capabilities

- `tier`: versioned bronze tier semantics — the mechanical mapping from check
  results to a bronze verdict.
- `report`: the `TransferabilityReport` model, its deterministic body, and the
  `report.json` / `report.md` rendering under an append-only `reports/`.

### Modified Capabilities

- `cli`: `assess` now emits a bronze verdict and writes the report; the
  "tier verdict not yet implemented" notice is removed.

## Impact

- **New code:** `src/estafette/{tier,report}.py`.
- **Modified code:** `src/estafette/cli.py` (verdict + report write), `src/estafette/assessment.py` (bundle results for the report).
- **Docs:** `docs/tiers.md` → v1.0.
- **Tests:** tier mapping (all-pass → bronze; each failing criterion → not bronze); report determinism (same inputs → byte-identical body; timing absent); commit-hash capture (git and non-git targets); append-only write behaviour.
- **Determinism (I5):** commit hash + tool versions recorded; wall-clock kept out of the body.
- **Out of scope:** silver/gold gating (still roadmap; silver stays informational).
