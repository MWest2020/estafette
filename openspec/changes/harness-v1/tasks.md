## 1. Manifest build section

- [ ] 1.1 Add optional `build` sub-model to `manifest.py`: `containerfile`, `readiness`, `timeout_seconds`, `cpus`, `memory`
- [ ] 1.2 `readiness` enum (`exits-zero` | `stays-up`); invalid value → actionable error
- [ ] 1.3 Default containerfile detection (`Containerfile`/`Dockerfile`)
- [ ] 1.4 Update `docs/manifest-spec.md` with the build section
- [ ] 1.5 Tests: build section parses; omitted section still valid; bad readiness rejected

## 2. Diagnostic classifier (pure, no podman)

- [ ] 2.1 Implement `harness/classify.py`: `classify(build_log, run_log) -> Category`
- [ ] 2.2 Ordered heuristics for `missing-declared-dep`, `undeclared-system-dep`, `unreachable-internal-service`, `requires-unavailable-data`
- [ ] 2.3 `other` carries a captured log tail
- [ ] 2.4 Tests: one representative log per category, including `other`

## 3. Podman runner

- [ ] 3.1 Implement `harness/podman.py`: detect usable rootless podman; capture version
- [ ] 3.2 Build stage: `podman build` (network permitted), capture build log
- [ ] 3.3 Run stage: `podman run --network=none` with cpu/memory/read-only, no host env
- [ ] 3.4 Enforce wall-clock cap (subprocess timeout + `podman kill`); record the cap hit
- [ ] 3.5 Implement readiness evaluation (`exits-zero` / `stays-up`)
- [ ] 3.6 Graceful "unavailable" result when podman is absent/unusable

## 4. Silver preview

- [ ] 4.1 Implement `checks/build.py`: build → run → classify → `SilverPreview`
- [ ] 4.2 `SilverPreview` = would-pass bool | unavailable(reason), plus gaps + evidence
- [ ] 4.3 Keep timing out of the deterministic body; record it as evidence (I5)

## 5. CLI integration

- [ ] 5.1 `assess` runs the harness after the static checks and prints the silver preview
- [ ] 5.2 Preview clearly labelled INFORMATIONAL; no gated tier verdict (I1)
- [ ] 5.3 Missing podman / no build recipe → preview unavailable, command still exits 0

## 6. Docs, verification, CI

- [ ] 6.1 Refine `docs/tiers.md` silver section to match the implemented preview
- [ ] 6.2 README: podman as an optional prerequisite; note the build-stage egress limitation
- [ ] 6.3 `ruff` + `pytest` green; every module ≤ 200 lines (I7)
- [ ] 6.4 Harness integration tests gated on podman; classifier/manifest tests run in CI; CI stays green
