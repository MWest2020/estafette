## 1. Tool runner

- [x] 1.1 Implement `checks/tooling.py`: `run_tool(argv)` capturing exit code + output
- [x] 1.2 Capture and expose each tool's version string (invariant I5)
- [x] 1.3 Raise a clear estafette-environment error when a tool is not on PATH
- [x] 1.4 Unit-test the runner (installed tool, missing tool) with a stub binary

## 2. REUSE check

- [x] 2.1 Implement `checks/reuse.py` wrapping `reuse lint`
- [x] 2.2 Map non-compliant files to gaps with remediation
- [x] 2.3 Fixture: clean repo passes; repo with a header-less file fails

## 3. Licence consistency check

- [x] 3.1 Implement `checks/licence_consistency.py` (manifest vs headers vs pyproject/package.json vs LICENSE)
- [x] 3.2 Report each disagreeing source and its declared value as a gap
- [x] 3.3 Fixture: consistent repo passes; mismatched-licence repo fails

## 4. Secrets check

- [x] 4.1 Implement `checks/secrets.py` wrapping `gitleaks`
- [x] 4.2 Report location (path/line) without echoing the secret value
- [x] 4.3 Fixture: clean repo passes; repo with a planted secret fails

## 5. SBOM check

- [x] 5.1 Implement `checks/sbom.py` wrapping `syft`; verify SBOM generates cleanly
- [x] 5.2 Normalise + match SBOM components against declared deps; report mismatches
- [x] 5.3 Fixture: matching repo passes; mismatched-deps repo fails

## 6. Dependency reality check

- [x] 6.1 Implement `checks/deps_reality.py`: declared deps vs imports/lockfiles (both directions)
- [x] 6.2 Emit "used in code but not declared" and "declared but unused" gaps
- [x] 6.3 Fixture: honest repo passes; undeclared-import repo fails

## 7. CLI integration

- [x] 7.1 Extend `assess` to run all five checks and print per-check status + gaps
- [x] 7.2 Print the external tool versions used (invariant I5)
- [x] 7.3 Exit 0 on successful run regardless of check outcomes; non-zero on bad manifest or missing tool
- [x] 7.4 Ensure no tier name is printed; narrow the notice to "tier verdict not yet implemented" (invariant I1)

## 8. Verification

- [x] 8.1 All checks green under `ruff` and `pytest`; every module ≤ 200 lines (I7)
- [x] 8.2 Document external tool prerequisites (`reuse`, `gitleaks`, `syft`) in the README
- [ ] 8.3 CI installs the external tools (or skips those tests deterministically) and stays green
