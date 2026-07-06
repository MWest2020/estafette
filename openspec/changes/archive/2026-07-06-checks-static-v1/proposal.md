## Why

`init-core-v1` gave us the manifest, the CLI surface, and the `Check` protocol
— but no actual checks, so `assess` can only echo the manifest. This change
implements the five **static checks** that make up everything in the bronze
tier except the manifest-presence gate: they are what turn estafette from a
schema into an assessor. Per invariant **I2**, estafette orchestrates existing
tools rather than reinventing them; the estafette-owned logic here is only the
adapters, the diff logic, and the gap reporting.

This change deliberately stops short of a **tier verdict** — assembling checks
into a bronze pass/fail plus the report artifacts is `tier-report-v1`. Here,
`assess` runs the checks and prints honest **per-check** results and gaps.

## What Changes

- Add a small **tool runner** (`checks/tooling.py`): run an external tool as a
  subprocess, capture its version (invariant I5), and fail loudly and clearly
  if the tool is not installed (a missing tool is an estafette-environment
  error, never a silent pass or a target gap).
- Implement five checks, each conforming to the `Check` protocol and each
  independently testable against fixtures:
  - `reuse.py` — wraps `reuse lint` (licence + copyright on every file).
  - `licence_consistency.py` — estafette-owned: declared licence vs file
    headers vs manifest vs `pyproject.toml`/`package.json`.
  - `secrets.py` — wraps `gitleaks`.
  - `sbom.py` — wraps `syft`; verifies the SBOM generates cleanly and matches
    declared dependencies.
  - `deps_reality.py` — estafette-owned: declared deps vs actual
    imports/lockfiles diff.
- Every failing check emits actionable **gaps** with concrete remediation
  (invariant I3), never a bare failure.
- Extend `assess` to run the checks and print per-check status + gaps + the
  tool versions used. Still **no tier verdict** (invariant I1).

## Capabilities

### New Capabilities

- `checks`: the five static checks, their shared tool-runner, the missing-tool
  behaviour, and the evidence/gap contract each check produces.

### Modified Capabilities

- `cli`: `assess` now runs the static checks and prints per-check results and
  gaps; it still emits no tier verdict, and the "not yet implemented" notice
  narrows to "tier verdict not yet implemented".

## Impact

- **New code:** `src/estafette/checks/{tooling,reuse,licence_consistency,secrets,sbom,deps_reality}.py`.
- **Modified code:** `src/estafette/cli.py` (run checks, print results).
- **New runtime tool dependencies (external, not Python):** `reuse`, `gitleaks`,
  `syft` — invoked as subprocesses; documented as prerequisites.
- **Tests:** fixture repos under `tests/fixtures/` — one clean repo plus one
  repo per gap class (missing licence header, licence mismatch, planted secret,
  SBOM/deps mismatch, undeclared import).
- **Docs:** note the external tool prerequisites in the README.
- **No** tier logic, report artifacts, or harness — deferred to `tier-report-v1`
  and `harness-v1`.
