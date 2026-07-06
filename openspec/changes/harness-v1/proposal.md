## Why

The build harness is the technically interesting artefact for the SIDN grant:
it answers "can someone who wasn't involved actually *build and run* this from
a clean environment?" mechanically and safely. It is also invariant **I4** made
real — untrusted PoC code must never run ambient. This change builds the
rootless-podman harness and its diagnostic classification.

Per the v1 plan, the harness result is **informational**: it produces a
**silver preview** ("would this pass silver: yes/no + gaps"), not a gated
verdict. Silver stays un-enforced until a later change; here we build the
engine and surface its finding. The bronze verdict (from `checks-static-v1`)
remains the only real verdict.

## What Changes

- Add `harness/podman.py`: a rootless-podman runner with two stages and hard
  isolation (invariant I4):
  - **build stage** — `podman build` (dependency fetch permitted);
  - **run stage** — `podman run --network=none`, CPU/memory/wall-clock caps,
    no host environment, no secrets, read-only mounts.
- Add `harness/classify.py`: a pure function mapping build/run logs to one
  diagnostic category — `missing-declared-dep` | `undeclared-system-dep` |
  `unreachable-internal-service` | `requires-unavailable-data` | `other` (the
  last carrying a captured log tail).
- Add `checks/build.py`: orchestrates build → run → classify and returns a
  `SilverPreview` (reached-running-state or a classification + actionable gaps).
- Extend the manifest with an optional `build` section describing how to build
  and what "running" means (containerfile, readiness mode, timeout, caps).
- Extend `assess` to run the harness when possible and print the silver preview
  informationally. A missing/unusable podman **degrades gracefully** ("silver
  preview unavailable: <reason>") — unlike the bronze scanners, it is not a
  hard error, because the harness is informational in v1.

## Capabilities

### New Capabilities

- `build-harness`: the rootless-podman runner, its isolation guarantees, the
  diagnostic classification, and the `SilverPreview` result contract.

### Modified Capabilities

- `transfer-manifest`: add an optional `build` section (containerfile path,
  readiness mode + timeout, resource caps) so the harness knows how to build
  and when the target has "reached a running state" — declared, not guessed.
- `cli`: `assess` runs the harness (when available) and prints an informational
  silver preview; still no gated tier verdict.

## Impact

- **New code:** `src/estafette/harness/{podman,classify}.py`, `src/estafette/checks/build.py`.
- **Modified code:** `src/estafette/manifest.py` (build section), `src/estafette/cli.py` (silver preview), `src/estafette/assessment.py`.
- **New runtime dependency (external):** rootless `podman` — optional; absence degrades the silver preview gracefully.
- **Tests:** classification unit tests (pure, no podman); harness integration tests gated on podman availability (skip cleanly when absent); fixtures — a repo that builds+runs, plus one per diagnostic class.
- **Determinism (I5):** the preview's verdict, classification, and gaps are deterministic; wall-clock timing is recorded as non-reproducible evidence and kept OUT of the byte-identical report body.
- **Docs:** `docs/tiers.md` silver section refined; README notes podman as an optional prerequisite.
- **Out of scope:** silver/gold *gating* (a later change); a true build-stage egress allowlist (documented hardening TODO — see design.md).
