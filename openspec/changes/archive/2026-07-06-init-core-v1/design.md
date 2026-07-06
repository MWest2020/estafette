## Context

This is the first change in an empty repository. Nothing exists yet except
project context, licence, README, and docs. Everything downstream
(`checks-static-v1`, `harness-v1`, `tier-report-v1`, `dogfood-v1`) depends on
the shape decided here, so the priority is a small, correct spine that does not
paint later changes into a corner — and that never lies about a verdict it
cannot yet produce.

## Goals / Non-Goals

**Goals:**

- A buildable, testable `uv` package with a working `estafette` console script.
- A well-typed `TransferManifest` (`pydantic` v2) that later checks compare
  reality against.
- A `Check` protocol so `checks-static-v1` plugs in without reshaping the core.
- CI that lints and tests on every push/PR — the guardrail for all later work.

**Non-Goals:**

- No checks, no harness, no tier, no report generation (explicitly deferred).
- No exporters, server, or web UI (out of scope for all of v1).
- No fake or placeholder verdicts.

## Decisions

- **CLI framework: `typer`.** Minimal, typed, gives `estafette assess` with
  little boilerplate; keeps `cli.py` well under 200 lines.
- **Manifest format: YAML via `pyyaml`, modelled with `pydantic` v2.** YAML
  matches `publiccode.yml` conventions; pydantic gives validation and clear
  errors for free (serving invariant I3 — actionable gaps).
- **`publiccode.yml` alignment.** Reuse its field names where concepts overlap
  (`licence`/`legal.license`, `name`) so the manifest reads as a profile, not a
  rival. estafette-specific additions: honest `status` and concrete `data`
  requirements.
- **`Check` protocol lands now, empty.** Defines `name` and
  `run(target) -> CheckResult(status, gaps[], evidence)` so later changes only
  add modules under `checks/`. No concrete checks in this change.
- **Honest placeholder.** `assess` validates the manifest and prints a summary
  plus an explicit "checks and tier not yet implemented" notice — never a tier
  or pass/fail (invariant I1).
- **File-size discipline (I7).** Split modules before they approach 200 lines;
  `manifest.py`, `cli.py`, `checks/protocol.py` stay small and single-purpose.

## Risks / Trade-offs

- **`typer` as a dependency vs stdlib `argparse`.** Accepted: `typer` keeps the
  CLI small and typed; it is a well-maintained, widely-used dependency. Revisit
  only if dependency minimalism becomes a grant-relevant concern.
- **Manifest schema will evolve.** The `data`/gold fields are declared now but
  only consumed later; getting names right early avoids churn. Mitigated by
  keeping the schema documented in `docs/manifest-spec.md` and versioned with
  the tier doc.
- **git-url targets.** `assess` accepts a git URL per the spec, but full clone
  handling can be minimal in this change (local path is the primary path);
  robust cloning can harden in a later change without changing the surface.
