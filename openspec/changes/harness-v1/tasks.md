## 1. Manifest build section

- [x] 1.1 Add optional `build` sub-model to `manifest.py`: `containerfile`, `readiness`, `timeout_seconds`, `cpus`, `memory`
- [x] 1.2 `readiness` enum (`exits-zero` | `stays-up`); invalid value → actionable error
- [x] 1.3 Default containerfile detection (`Containerfile`/`Dockerfile`)
- [x] 1.4 Update `docs/manifest-spec.md` with the build section
- [x] 1.5 Tests: build section parses; omitted section still valid; bad readiness rejected

## 2. Diagnostic classifier (pure, no podman)

- [x] 2.1 Implement `harness/classify.py`: `classify(build_log, run_log) -> Category`
- [x] 2.2 Ordered heuristics for `missing-declared-dep`, `undeclared-system-dep`, `unreachable-internal-service`, `requires-unavailable-data`
- [x] 2.3 `other` carries a captured log tail
- [x] 2.4 Tests: one representative log per category, including `other`

## 3. Podman runner

- [x] 3.1 Implement `harness/podman.py`: detect usable rootless podman; capture version
- [x] 3.2 Build stage: `podman build` (network permitted), capture build log
- [x] 3.3 Run stage: `podman run --network=none` with cpu/memory/read-only, no host env
- [x] 3.4 Enforce wall-clock cap (subprocess timeout + `podman kill`); record the cap hit
- [x] 3.5 Implement readiness evaluation (`exits-zero` / `stays-up`)
- [x] 3.6 Graceful "unavailable" result when podman is absent/unusable

## 4. Silver preview

- [x] 4.1 Implement `checks/build.py`: build → run → classify → `SilverPreview`
- [x] 4.2 `SilverPreview` = would-pass bool | unavailable(reason), plus gaps + evidence
- [x] 4.3 Keep timing out of the deterministic body; record it as evidence (I5)

## 5. CLI integration

- [x] 5.1 `assess` runs the harness after the static checks and prints the silver preview
- [x] 5.2 Preview clearly labelled INFORMATIONAL; no gated tier verdict (I1)
- [x] 5.3 Missing podman / no build recipe → preview unavailable, command still exits 0

## 6. Docs, verification, CI

- [x] 6.1 Refine `docs/tiers.md` silver section to match the implemented preview
- [x] 6.2 README: podman as an optional prerequisite; note the build-stage egress limitation
- [x] 6.3 `ruff` + `pytest` green; every module ≤ 200 lines (I7)
- [ ] 6.4 Harness integration tests gated on podman; classifier/manifest tests run in CI; CI stays green
