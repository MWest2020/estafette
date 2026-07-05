## Why

estafette needs a spine before it can do anything useful: a repository
skeleton, the data model that everything else compares reality against (the
**transfer manifest**), a CLI entry point, and CI so that every later change is
verified. This is change 1 of the v1 roadmap (see `openspec/project.md`). It
deliberately implements **no checks and no verdict** — those come in
`checks-static-v1`, `harness-v1`, and `tier-report-v1`. The point here is to
make the project buildable, testable, and extensible without violating the core
invariants from day one.

## What Changes

- Establish the Python package skeleton under `src/estafette/` (`uv`-managed,
  console script `estafette`), with all modules ≤ 200 lines (invariant I7).
- Introduce the **`TransferManifest`** `pydantic` v2 model (`manifest.py`),
  designed as an extension profile of `publiccode.yml`, plus loading and
  validation from a YAML file.
- Provide the **`estafette assess <path|git-url> [--manifest path]`** CLI stub:
  it loads and validates the manifest and prints a placeholder result. It does
  **not** run checks or emit a tier yet (that stays honest — no fake verdicts).
- Add `docs/manifest-spec.md` (the manifest specification) — done.
- Add **CI** (GitHub Actions): lint (`ruff`) + tests (`pytest`) on push/PR.
- Add the `Check` protocol placeholder (`checks/protocol.py`) so later changes
  plug in without reshaping the core.

## Capabilities

### New Capabilities

- `transfer-manifest`: the transfer manifest schema, its YAML loading, and
  validation semantics; alignment with `publiccode.yml`.
- `cli`: the `estafette assess` command surface — argument parsing, manifest
  loading, and honest placeholder output pending real checks.

### Modified Capabilities

<!-- None; this is the first change. -->

## Impact

- **New code:** `src/estafette/{__init__,cli,manifest}.py`,
  `src/estafette/checks/protocol.py`.
- **Docs:** `docs/manifest-spec.md`, `docs/tiers.md` (roadmap tiers).
- **Tooling:** `pyproject.toml` (uv, hatchling, ruff, pytest), `.github/workflows/ci.yml`.
- **Tests:** `tests/` with manifest validation fixtures (valid + each invalid class).
- **Dependencies:** `pydantic>=2`, `pyyaml`, `typer` (runtime); `pytest`, `ruff` (dev).
- **No** checks, harness, tier, or report logic — explicitly deferred.
