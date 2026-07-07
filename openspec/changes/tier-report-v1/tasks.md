## 1. Bronze tier

- [x] 1.1 Implement `tier.py`: `TIER_DOC_VERSION` and a `Criterion` list mapping B1–B6 to results
- [x] 1.2 `compute_bronze(results, manifest) -> BronzeVerdict(passed, criteria[])` (pure)
- [x] 1.3 B4 = AND of `sbom` and `deps_reality`; B5/B6 recorded as structurally satisfied
- [x] 1.4 Tests: all-pass → bronze; each single failing criterion → not-bronze with the right criterion flagged

## 2. Report model + rendering

- [x] 2.1 Implement `report.py`: `TransferabilityReport` (pydantic v2) with commit, tool versions, per-check results, gaps, silver preview, verdict
- [x] 2.2 Render `report.json` (sorted keys, fixed separators) and `report.md` (fixed section order)
- [x] 2.3 Capture commit via `git -C <target> rev-parse HEAD`; non-git → unavailable, not fabricated
- [x] 2.4 Exclude timing / absolute temp paths from the body; normalise evidence (sorted, target-prefix stripped)

## 3. Append-only writing

- [x] 3.1 Write under `reports/`, keyed by commit; never overwrite a differing existing report
- [x] 3.2 Tests: same commit + version → byte-identical body; differing report is not clobbered

## 4. CLI + docs

- [x] 4.1 `assess` computes the verdict, writes the report, prints verdict + report path
- [x] 4.2 Remove the "tier verdict not yet implemented" notice; silver stays informational
- [x] 4.3 Cut `docs/tiers.md` to v1.0 (bronze normative + implemented)
- [ ] 4.4 `ruff` + `pytest` green; every module ≤ 200 lines (I7); CI stays green
