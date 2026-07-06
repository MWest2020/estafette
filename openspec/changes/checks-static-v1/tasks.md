## 1. Tool runner

- [ ] 1.1 Implement `checks/tooling.py`: `run_tool(argv)` capturing exit code + output
- [ ] 1.2 Capture and expose each tool's version string (invariant I5)
- [ ] 1.3 Raise a clear estafette-environment error when a tool is not on PATH
- [ ] 1.4 Unit-test the runner (installed tool, missing tool) with a stub binary

## 2. REUSE check

- [ ] 2.1 Implement `checks/reuse.py` wrapping `reuse lint`
- [ ] 2.2 Map non-compliant files to gaps with remediation
- [ ] 2.3 Fixture: clean repo passes; repo with a header-less file fails

## 3. Licence consistency check

- [ ] 3.1 Implement `checks/licence_consistency.py` (manifest vs headers vs pyproject/package.json vs LICENSE)
- [ ] 3.2 Report each disagreeing source and its declared value as a gap
- [ ] 3.3 Fixture: consistent repo passes; mismatched-licence repo fails

## 4. Secrets check

- [ ] 4.1 Implement `checks/secrets.py` wrapping `gitleaks`
- [ ] 4.2 Report location (path/line) without echoing the secret value
- [ ] 4.3 Fixture: clean repo passes; repo with a planted secret fails

## 5. SBOM check

- [ ] 5.1 Implement `checks/sbom.py` wrapping `syft`; verify SBOM generates cleanly
- [ ] 5.2 Normalise + match SBOM components against declared deps; report mismatches
- [ ] 5.3 Fixture: matching repo passes; mismatched-deps repo fails

## 6. Dependency reality check

- [ ] 6.1 Implement `checks/deps_reality.py`: declared deps vs imports/lockfiles (both directions)
- [ ] 6.2 Emit "used in code but not declared" and "declared but unused" gaps
- [ ] 6.3 Fixture: honest repo passes; undeclared-import repo fails

## 7. CLI integration

- [ ] 7.1 Extend `assess` to run all five checks and print per-check status + gaps
- [ ] 7.2 Print the external tool versions used (invariant I5)
- [ ] 7.3 Exit 0 on successful run regardless of check outcomes; non-zero on bad manifest or missing tool
- [ ] 7.4 Ensure no tier name is printed; narrow the notice to "tier verdict not yet implemented" (invariant I1)

## 8. Verification

- [ ] 8.1 All checks green under `ruff` and `pytest`; every module ≤ 200 lines (I7)
- [ ] 8.2 Document external tool prerequisites (`reuse`, `gitleaks`, `syft`) in the README
- [ ] 8.3 CI installs the external tools (or skips those tests deterministically) and stays green
