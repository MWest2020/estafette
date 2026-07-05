## 1. Package skeleton

- [x] 1.1 Create `src/estafette/__init__.py` with version export
- [x] 1.2 Confirm `pyproject.toml` builds a `estafette` console script via `uv` (hatchling backend)
- [x] 1.3 Add `checks/__init__.py` and `harness/__init__.py` package markers
- [x] 1.4 Verify every module is ≤ 200 lines (invariant I7)

## 2. Transfer manifest

- [x] 2.1 Implement `TransferManifest` pydantic v2 model in `manifest.py` (fields per `docs/manifest-spec.md`)
- [x] 2.2 Implement `status` enum (`concept`/`poc`/`beta`/`stable`/`obsolete`) and `data` sub-model
- [x] 2.3 Implement `load_manifest(path)` with YAML parsing and actionable errors (default `transfer.yaml`)
- [x] 2.4 Align field names with `publiccode.yml` where concepts overlap

## 3. Check protocol placeholder

- [x] 3.1 Define `Check` protocol and `CheckResult(status, gaps[], evidence)` in `checks/protocol.py`
- [x] 3.2 No concrete checks implemented in this change

## 4. CLI stub

- [x] 4.1 Implement `estafette assess <path|git-url> [--manifest path]` in `cli.py` using typer
- [x] 4.2 Load + validate manifest; print summary and an explicit "checks and tier not yet implemented" notice
- [x] 4.3 Ensure no tier name or pass/fail claim is ever printed (invariant I1)
- [x] 4.4 Non-zero exit and actionable message on invalid/missing manifest

## 5. Tests

- [x] 5.1 Fixture: one valid manifest → parses
- [x] 5.2 Fixtures: missing-required-field and invalid-status → validation errors
- [x] 5.3 Test `load_manifest` default path and missing-file behaviour
- [x] 5.4 Test `assess` exit codes and honest placeholder output

## 6. CI

- [x] 6.1 Add `.github/workflows/ci.yml`: `uv sync`, `ruff check`, `pytest` on push/PR
- [ ] 6.2 Confirm CI is green on the first push
