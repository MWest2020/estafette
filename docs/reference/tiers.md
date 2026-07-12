---
status: draft
last_reviewed: 2026-07-12
---

# Transferability tiers

**Version:** 1.0 (bronze implemented and emitted by the engine; silver
informational; gold specified as roadmap)

The engine emits the bronze verdict mechanically into the transferability report
(`report.json` + `report.md`), recording this tier-doc version alongside the
target commit and tool versions.

This document is **normative**. A tier is only ever the output of the estafette
engine on a specific commit (invariant **I1**). Nothing in this document may be
satisfied by self-declaration or human judgement; every criterion below maps to
a mechanical check.

Tiers are cumulative: silver requires bronze, gold requires silver.

---

## Bronze — reuse conversations are possible

Bronze is the floor. It answers: *is this repository legally and
informationally clear enough that a third party can even begin to evaluate
reusing it?*

A repository is **bronze** if and only if all of the following mechanical
checks pass:

| # | Criterion | Check | Tool |
|---|-----------|-------|------|
| B1 | REUSE-compliant — every file has licence + copyright information | `reuse lint` passes | REUSE |
| B2 | Declared licence is consistent everywhere it appears (file headers, manifest, `pyproject.toml`/`package.json`, `LICENSE`) | `licence_consistency` finds no disagreement | estafette |
| B3 | No secrets detected | `gitleaks` finds nothing | gitleaks |
| B4 | SBOM generates cleanly and matches declared dependencies | `syft` produces a valid SBOM; `deps_reality` finds no undeclared/phantom deps | syft + estafette |
| B5 | Transfer manifest present and valid | manifest parses against the schema | estafette |
| B6 | Contact/owner field is non-empty | manifest `owner`/`contact` populated | estafette |

Every failing criterion **must** emit an actionable gap (invariant **I3**),
never a bare failure.

---

## Silver — builds reproducibly *(roadmap — specified, not enforced in v1)*

Silver answers: *can a third party actually build this from a clean
environment, without tribal knowledge?*

A repository is **silver** if it is bronze **and** the build harness reaches a
running state from a clean, isolated environment.

The harness (invariant **I4**) runs in rootless `podman`:

- **build stage:** dependency fetch permitted via a network allowlist only;
- **run stage:** no network at all;
- CPU / memory / wall-clock caps;
- no host environment, no secrets, read-only bind of the target repository.

On failure the harness must return a diagnostic classification, not a bare
error:

- `missing-declared-dep`
- `undeclared-system-dep`
- `unreachable-internal-service`
- `requires-unavailable-data`
- `other` (with a captured log tail)

**v1 status:** the harness **is** built in v1, but silver is **not gated**. The
harness result is reported **informationally** as a silver preview: *"would
this pass silver: yes/no + gaps."*

The preview is driven by the manifest's `build` section (containerfile,
readiness mode, timeout, caps). Reaching a running state is judged by the
declared readiness mode (`stays-up` or `exits-zero`). On failure the harness
emits one diagnostic classification with an actionable gap. When rootless
podman is absent or unusable, or the manifest declares no build recipe, the
preview reports *not assessable* — it never blocks the bronze verdict.

> **Known limitation (v1):** the build stage currently has unrestricted network
> egress (dependency fetch runs arbitrary build scripts). The *run* stage —
> where the assessed code executes — is strictly network-free. A build-stage
> egress allowlist is planned hardening.

---

## Gold — third-party deployable *(roadmap — specified, not enforced in v1)*

Gold answers: *can a third party deploy and operate this, including satisfying
its data requirements?*

A repository is **gold** if it is silver **and**:

- it reaches a running deployable state against its declared deployment target;
- its declared data requirements (schema, volume, sensitivity, synthetic-data
  availability) are satisfiable by a third party.

Gold criteria will be made fully mechanical before implementation. Not
implemented in v1.

---

## Versioning

Tier semantics are versioned. A report always records the tier-doc version it
was evaluated against, alongside the estafette version and target commit hash,
so a verdict is reproducible and auditable (invariant **I5**).
