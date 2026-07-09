# estafette — project context

> One sentence: *"Can someone who was not involved get this running?
> Estafette answers that question mechanically."*

Estafette makes public-sector proofs of concept **transferable — and
measurably so**. It is a CLI that mechanically assesses a repository against a
*transfer manifest* and produces a **transferability report** with a tier
verdict. It orchestrates existing scanners; it does not reinvent them.

- **Licence:** EUPL-1.2 (see `LICENSE`), public from day one.
- **Language:** Python 3.12+.
- **Docs:** English.
- **This repository is the evidence artefact for the SIDN Pioniers grant
  application.** A private repo that "goes public later" does not count.

## Purpose of v1 (and what it is NOT)

The goal of v1 is explicitly **not** to build the whole proposal. The goal is:
**one command that, on one real existing PoC, produces an honest
transferability report.** That report is the annex to the SIDN application.
Everything that does not contribute to that is v2.

## Core invariants

These are load-bearing. A change that violates one of these is rejected, not
merged.

- **I1 — Mechanical or it doesn't count.** A tier is only ever the output of
  the engine on a specific commit. No self-declared checkboxes, no
  human-judgment criteria in the tier definition.
- **I2 — Orchestrate, don't reinvent.** Licence clarity = the REUSE tool.
  SBOM = `syft`. Secrets = `gitleaks`. Vulnerabilities = `trivy` (v2).
  Estafette's own code is the manifest schema, the harness, the tier
  semantics and the report — nothing else.
- **I3 — Diagnose, don't just fail.** Every failed check must emit an
  actionable gap ("dependency X used in code but not declared"), never a bare
  red cross. The gap report is the product.
- **I4 — Untrusted code never runs ambient.** The build harness runs in
  rootless `podman`: no network in the run stage, dependency fetch only in the
  build stage, CPU/memory/time caps, no host env, no secrets, read-only bind
  of the target repo.
- **I5 — Deterministic and reproducible.** Same commit + same estafette
  version → byte-identical report body. The report includes tool versions and
  the target commit hash. Append-only: reports are never overwritten, they
  accumulate under `reports/`.
- **I6 — No LLM anywhere in the verdict path.** (An LLM may later draft
  remediation prose from the gap report; it never scores.)
- **I7 — Engineering constraints.** Files ≤ 200 lines. `uv`, never `pip`.
  `pydantic` v2 for all schemas. Commits stay local until Mark pushes.

## Architecture (target)

```
estafette/
  pyproject.toml            # uv-managed, console script: estafette
  LICENSE                   # EUPL-1.2
  src/estafette/
    manifest.py             # TransferManifest (pydantic): licence, deps,
                            #   data requirements (schema/volume/sensitivity/
                            #   synthetic-data), deployment target,
                            #   owner/contact, honest status. Designed as an
                            #   EXTENSION PROFILE of publiccode.yml, not a
                            #   competitor: field names align where overlap
                            #   exists.
    checks/
      protocol.py           # Check protocol: name, run(target) ->
                            #   CheckResult(status, gaps[], evidence)
      reuse.py              # wraps `reuse lint`
      licence_consistency.py# declared licence vs file headers vs manifest
                            #   vs pyproject/package.json
      secrets.py            # wraps gitleaks
      sbom.py               # wraps syft; validates SBOM generates cleanly
                            #   and matches declared deps
      deps_reality.py       # declared deps vs imports/lockfiles diff
      build.py              # clean-environment build via harness
    harness/
      podman.py             # rootless podman runner per I4:
                            #   build stage (network: allowlist),
                            #   run stage (network: none),
                            #   caps: cpu/mem/wallclock,
                            #   verdict: reached-running-state or diagnostic
                            #   classification:
                            #     missing-declared-dep |
                            #     undeclared-system-dep |
                            #     unreachable-internal-service |
                            #     requires-unavailable-data |
                            #     other (with captured log tail)
    tier.py                 # versioned tier semantics (v1: bronze only).
                            #   Tier doc lives in docs/tiers.md and is
                            #   normative.
    report.py               # TransferabilityReport (pydantic) -> report.json
                            #   + report.md (human). Includes: commit, tool
                            #   versions, per-check evidence, gap list, tier.
    cli.py                  # `estafette assess <path|git-url> [--manifest path]`
  docs/
    tiers.md                # normative tier criteria, versioned
    manifest-spec.md        # the transfer manifest specification
  reports/                  # append-only example reports (real PoCs,
                            #   anonymised where needed)
  tests/                    # pytest; fixtures = tiny synthetic repos
                            #   (one passing, one per gap class)
```

## Tier v1: bronze only

Bronze = the floor that makes reuse conversations possible:

1. REUSE-compliant (every file has licence + copyright info)
2. Declared licence is consistent everywhere it appears
3. No secrets detected
4. SBOM generates cleanly and matches declared dependencies
5. Transfer manifest present and valid
6. Contact/owner field non-empty

**Silver** (builds reproducibly in the harness) and **gold** (third-party
deployable, data requirements satisfiable) are *specified* in `docs/tiers.md`
as roadmap but **not implemented** in v1 — except that the build harness
itself *is* built in v1 and its result is reported informationally ("would
this pass silver: yes/no + gaps"). Rationale: the harness is the technically
interesting artefact for the grant application; the silver gate can mature
later.

## Roadmap — OpenSpec changes to propose, in order

1. `init-core-v1` — skeleton, TransferManifest schema, manifest-spec.md, CLI
   stub, CI (lint + tests on GitHub Actions). **← current**
2. `checks-static-v1` — reuse, licence_consistency, secrets, sbom,
   deps_reality. Each check independently testable against fixtures.
3. `harness-v1` — podman build harness per I4 with the diagnostic
   classification. This is the hard one; budget it accordingly.
4. `tier-report-v1` — bronze verdict, report.json + report.md, docs/tiers.md
   v1.0.
5. `dogfood-v1` — run estafette against ONE real PoC (from the
   Conduction/Common Ground orbit or an own archived PoC), fix what the
   experience teaches, commit the anonymised report to `reports/`. This report
   is the SIDN annex.

## Out of scope for v1 (written down to prevent drift)

- **Exporters** (publiccode.yml emit, OpenCatalogi) — v2, and part of the
  grant-funded work, so deliberately not pre-built.
- **Silver/gold enforcement, trivy vulnerability scanning, PII scan**
  (candidate: reuse OpenAnonymiser later — note the synergy, build nothing).
- **Any server, web UI, badge service, or catalogue.** Estafette is a CLI.
  Full stop.
- **Windows support.**

## Definition of done for v1

`uvx estafette assess <repo>` on the chosen real PoC produces, in under 10
minutes on the alma workstation, a `report.md` that a disclosure-minded
reviewer can read top to bottom: commit hash, what passed, every gap with a
concrete remediation, bronze verdict, and an informational silver preview from
the harness. The report is committed under `reports/` and referenced in the
SIDN Pioniers application. Nothing in the verdict path involves a model, and
every line of the report can be regenerated byte-identically.

## v2 (in progress): the platform

v1 is complete: the CLI produces a bronze verdict and a deterministic report per
PoC under `reports/`. v2 turns that report database into a **platform that shows
the assessed PoCs**. The first v2 change (`catalogue-v1`) does this in its
simplest honest form: `reports/` *is* the database, and `estafette catalogue`
renders it to a **static site** (GitHub Pages) — no server, no DB engine, no web
framework. This supersedes the v1 "no catalogue" scope line below; "estafette is
a CLI" still holds, because the site is a CLI-emitted static artifact. A real
database can later slot in behind the same report loader without a rewrite.

## Conventions

- **Workflow:** OpenSpec (propose → apply → archive). Non-trivial work starts
  as a change under `openspec/changes/`.
- **Naming:** relates to *estafette* = relay race; a PoC is the baton being
  handed off. (A dormant CI/CD product shares the name; we live in the
  personal namespace `MWest2020/estafette` — no URL collision.)
