## Context

`checks-static-v1` covers everything in bronze except the manifest gate. This
change builds the piece that makes *silver* meaningful and that embodies I4:
a harness that builds and runs untrusted PoC code without letting it run
ambient. In v1 the harness is informational (a silver preview), so it can be
imperfect at the edges (classification heuristics, missing podman) without
endangering the real bronze verdict.

## Goals / Non-Goals

**Goals:**

- Rootless-podman two-stage execution with the I4 isolation properties.
- A deterministic, unit-testable diagnostic classifier over captured logs.
- A `SilverPreview` surfaced informationally by `assess`.
- Graceful degradation when podman is absent or the manifest has no build recipe.

**Non-Goals:**

- No silver/gold *gating* — the preview never changes the bronze verdict.
- No report artifacts (`tier-report-v1`).
- No true per-host build-stage egress allowlist (documented hardening TODO).
- No Windows support.

## Decisions

- **Build recipe is declared, not guessed.** The manifest's `build.containerfile`
  points at a Containerfile/Dockerfile (with default detection). No recipe →
  preview is "not assessable", never a guess. This keeps the harness mechanical
  (I1) and honest.
- **Two podman invocations map to the two stages.** `podman build` (network
  permitted, for deps) then `podman run --network=none` with `--cpus`,
  `--memory`, `--read-only`, no `--env` passthrough, wall-clock enforced by a
  subprocess timeout plus `podman kill`. The security-critical property — the
  *run* stage has no network — is enforced hard.
- **Build-stage egress is not yet allowlisted.** Dependency fetch needs network,
  and build scripts (setup.py, npm postinstall) run arbitrary code with it.
  v1 permits build-stage network and records this as a known limitation; a
  slirp4netns/proxy allowlist is the hardening follow-up. The run stage — where
  the assessed code actually executes — remains network-free, preserving I4's
  core intent.
- **Readiness is declared.** `exits-zero` for batch PoCs, `stays-up` for
  services (still healthy at the end of a fixed window). Mode + timeout are
  recorded so the verdict is reproducible.
- **Classification is a pure function of logs.** `classify(build_log, run_log)
  -> Category` uses ordered regex heuristics; the first match wins; `other`
  carries a log tail. Being pure, it is fully unit-testable without podman, and
  because it feeds only an informational preview, a misclassification is
  low-stakes and always accompanied by evidence.
- **Missing podman degrades, it does not fail.** Unlike the bronze scanners
  (hard error on absence), an absent/unusable podman yields an "unavailable"
  preview. Rationale: the harness is informational in v1; bronze must not
  depend on it.
- **Timing is evidence, not verdict.** Durations are non-deterministic and are
  kept out of the byte-identical report body (I5); only the verdict,
  classification, and gaps are part of the reproducible body.

## Risks / Trade-offs

- **Rootless podman setup is finicky** (subuid/subgid, newuidmap, cgroups v2).
  Mitigation: detect and degrade gracefully with a clear reason; document setup;
  gate integration tests on a working podman.
- **Arbitrary build code runs with network** (allowlist gap). Mitigation:
  documented limitation; run stage stays network-free; a future allowlist
  closes it. Flagged explicitly because it is a real security trade-off.
- **Classification false positives/negatives.** Mitigation: always attach a log
  tail; keep the preview informational so misclassification cannot corrupt a
  tier score; grow the heuristic set from real dogfood logs.
- **"Stays-up" is timing-based.** A fixed readiness window can misjudge slow
  starts. Mitigation: window is configurable per manifest and recorded; document
  the trade-off.
- **CI cannot easily run rootless podman.** Mitigation: unit-test the classifier
  and manifest changes in CI (no podman); run harness integration tests locally
  / on the alma workstation where podman is configured, and skip them cleanly in
  CI.
