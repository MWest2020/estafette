## Context

The checks, harness, and CLI plumbing exist; the manifest is loaded and
validated before checks run. What's missing is the mapping from results to a
verdict and the durable, reproducible report. This is the last engine change
before dogfooding, so the report format is what the SIDN reviewer will actually
read — clarity and determinism matter most.

## Goals / Non-Goals

**Goals:**

- A mechanical bronze verdict that is a pure function of the check results.
- A deterministic, append-only report in machine (`json`) and human (`md`) form.
- Honest provenance: commit hash + tool versions in the body.

**Non-Goals:**

- No silver/gold gating (silver stays an informational preview).
- No exporters (publiccode.yml/OpenCatalogi) — v2.
- No LLM-drafted prose (I6) — the report is generated mechanically.

## Decisions

- **Bronze = conjunction of the five checks, plus structurally-satisfied B5/B6.**
  B5 (manifest present/valid) and B6 (contact non-empty) are already guaranteed
  by the time checks run (assess fails earlier otherwise), but the report lists
  all six criteria explicitly so the verdict is self-explanatory. B4 is the AND
  of the `sbom` and `deps_reality` checks, per `docs/tiers.md`.
- **Tier semantics are versioned in code and doc.** `tier.py` carries a
  `TIER_DOC_VERSION` recorded in every verdict, matching `docs/tiers.md` v1.0.
- **Determinism by construction.** The report body is built only from
  deterministic inputs (verdict, criteria, gaps, tool versions, commit hash).
  Timings and absolute temp paths are excluded. JSON is written with sorted keys
  and a fixed separator; the markdown is templated in a fixed order.
- **Commit hash via `git -C <target> rev-parse HEAD`.** Non-git targets record
  the commit as unavailable — never fabricated (I5 honesty).
- **Append-only writes.** Reports are keyed by commit under `reports/`. Because
  the body is deterministic, a re-run of the same commit is byte-identical and
  safe; if a differing report already exists at the target path, the writer
  writes a sibling rather than overwriting, so history accumulates (I5).
- **Report drives off the same bundle the CLI already has.** `assess` collects
  check results + silver preview + manifest, hands them to `report.py`; no
  second pass over the target, keeping it deterministic and fast.

## Risks / Trade-offs

- **Determinism leaks.** Tool output can embed absolute paths or ordering that
  varies. Mitigation: normalise evidence (sort lists, strip the target prefix)
  before it enters the body; a determinism test asserts byte-identical repeats.
- **Append-only vs clutter.** Accumulating reports can pile up. Accepted for v1:
  the grant needs the audit trail; pruning is a later concern.
- **`report.md` scope creep.** It is tempting to make the human report elaborate.
  Keep it to the DoD shape: commit, what passed, gaps with remediations, verdict,
  silver preview. Anything more is v2.
