# estafette

**Can someone who was not involved get this running? Estafette answers that
question mechanically.**

Estafette makes public-sector proofs of concept **transferable — and
measurably so**. It is a command-line tool that assesses a repository against
a *transfer manifest* and produces a **transferability report** with a tier
verdict. It orchestrates existing, trusted scanners rather than reinventing
them.

- **Status:** early development (v1 in progress). See
  [`openspec/project.md`](openspec/project.md) for the full plan.
- **Licence:** [EUPL-1.2](LICENSE) — public from day one.
- **Python:** 3.12+
- **Package/runner:** [`uv`](https://docs.astral.sh/uv/)

> The name *estafette* is Dutch for a relay race. A proof of concept is the
> baton: the point is whether it can be handed off cleanly to someone who
> wasn't there when it was built.

## What it does

Given a repository and a transfer manifest, estafette runs a fixed set of
mechanical checks and reports, per check:

- the **status** (pass / fail),
- an actionable **gap** for every failure (e.g. *"dependency `X` is imported in
  code but not declared"*), never a bare red cross, and
- the **evidence** it used, so the verdict is auditable.

It then assigns a **tier**. In v1 the only implemented tier is **bronze** —
the floor that makes reuse conversations possible.

### Bronze tier

1. REUSE-compliant (every file has licence + copyright info)
2. Declared licence is consistent everywhere it appears
3. No secrets detected
4. SBOM generates cleanly and matches declared dependencies
5. Transfer manifest present and valid
6. Contact/owner field non-empty

**Silver** (builds reproducibly in an isolated harness) and **gold**
(third-party deployable, data requirements satisfiable) are specified as
roadmap in [`docs/tiers.md`](docs/tiers.md) and not yet enforced. The build
harness itself *is* built in v1, and its result is reported informationally
("would this pass silver: yes/no + gaps").

## Design principles

Estafette **orchestrates, it does not reinvent**:

| Concern                | Tool                    |
| ---------------------- | ----------------------- |
| Licence clarity        | [REUSE](https://reuse.software/) |
| Software bill of materials | [`syft`](https://github.com/anchore/syft) |
| Secret detection       | [`gitleaks`](https://github.com/gitleaks/gitleaks) |
| Vulnerabilities        | [`trivy`](https://github.com/aquasecurity/trivy) *(v2)* |

Estafette's own code is the manifest schema, the build harness, the tier
semantics, and the report — nothing else. Full invariants are in
[`openspec/project.md`](openspec/project.md); highlights:

- **Mechanical or it doesn't count** — a tier is only ever the output of the
  engine on a specific commit.
- **Diagnose, don't just fail** — the gap report is the product.
- **Untrusted code never runs ambient** — the build harness runs in rootless
  `podman` with no network in the run stage and strict resource caps.
- **Deterministic and reproducible** — same commit + same estafette version →
  byte-identical report body.
- **No LLM anywhere in the verdict path.**

## Usage (target)

```bash
uvx estafette assess <path-or-git-url> [--manifest path/to/manifest.yaml]
```

This produces `report.json` and a human-readable `report.md` under `reports/`.

> The CLI is under construction. Track progress via the OpenSpec changes in
> [`openspec/changes/`](openspec/changes/).

## The transfer manifest

The transfer manifest is designed as an **extension profile of
[`publiccode.yml`](https://yml.publiccode.tools/)**, not a competitor: field
names align where overlap exists. See
[`docs/manifest-spec.md`](docs/manifest-spec.md).

## Development

This project uses the [OpenSpec](https://github.com/Fission-AI/OpenSpec)
workflow (propose → apply → archive). Proposed and in-progress work lives under
[`openspec/changes/`](openspec/changes/).

```bash
uv sync            # install dependencies
uv run pytest      # run tests
```

## Licence

[EUPL-1.2](LICENSE). Copyright the estafette contributors.
