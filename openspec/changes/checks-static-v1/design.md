## Context

`init-core-v1` established the `Check` protocol
(`name`, `run(target) -> CheckResult(status, gaps, evidence)`) but no checks.
Three of the five checks wrap external tools (`reuse`, `gitleaks`, `syft`); two
are estafette-owned diff logic (`licence_consistency`, `deps_reality`). The
common risk is subprocess handling: version capture for reproducibility (I5),
and honest behaviour when a tool is absent.

## Goals / Non-Goals

**Goals:**

- Five independently-runnable, independently-tested checks conforming to the
  protocol.
- One small shared tool runner: run tool, capture version, fail loudly if
  missing.
- Actionable gaps for every failure (I3); evidence for every pass.
- `assess` runs the checks and prints per-check results — still no tier.

**Non-Goals:**

- No tier assembly, no `report.json`/`report.md`, no bronze verdict
  (`tier-report-v1`).
- No build harness (`harness-v1`).
- No vendoring or reimplementing of `reuse`/`gitleaks`/`syft` (I2).

## Decisions

- **Subprocess, not library bindings.** Invoke `reuse`, `gitleaks`, `syft` as
  subprocesses via one `tooling.py` runner. Keeps I2 honest, avoids pinning to
  their Python APIs, and makes version capture uniform.
- **Missing tool = environment error, not a target gap.** If a required tool is
  not on PATH, estafette raises a clear error and `assess` exits non-zero. A
  missing scanner must never read as "the target passed" (I1) or as the
  target's fault.
- **Checks return, they do not print.** Each check returns a `CheckResult`;
  only the CLI renders. Keeps checks unit-testable and keeps rendering in one
  place for the future report.
- **Secrets are located, never echoed.** The secrets check reports path/line,
  never the secret value, so reports remain safe to commit (feeds I5's
  append-only reports).
- **Fixtures are tiny synthetic repos.** One clean repo plus one repo per gap
  class (missing header, licence mismatch, planted secret, SBOM/deps mismatch,
  undeclared import). This is the only way to test mechanically per I1.
- **Per-check exit semantics.** `assess` exits 0 when it *ran* successfully,
  even if checks report failures — the verdict is not the command's exit code.
  Non-zero is reserved for command-level failure (bad manifest, missing tool).
  The tier gate in `tier-report-v1` will decide how verdict maps to exit code.

## Risks / Trade-offs

- **External tool version drift.** `syft`/`gitleaks`/`reuse` output formats
  change across versions. Mitigation: capture versions in evidence (I5), parse
  defensively, and pin expectations in fixtures; treat unparseable output as a
  loud error, not a silent pass.
- **`deps_reality` language coverage.** Full import/lockfile analysis is
  language-specific. v1 targets Python (imports + `uv.lock`/`requirements`) and
  reads `package.json` for the JS licence-consistency case only; broader
  ecosystems are a later increment. Documented so the dogfood PoC choice
  accounts for it.
- **Determinism of SBOM matching.** Name-normalisation between declared deps
  and SBOM components can cause false mismatches. Mitigation: normalise names
  (case, separators) and report the normalised comparison in evidence.
