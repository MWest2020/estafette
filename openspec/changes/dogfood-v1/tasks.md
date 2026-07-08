## 1. Select target and write manifest

- [x] 1.1 Choose ONE real PoC operations are permitted on (estafette itself — a real, local, network-free target); rationale recorded in the commit
- [x] 1.2 Author an honest `transfer.yaml` (licence, owner, contact, status, deps)

## 2. Run end to end

- [x] 2.1 Run `estafette assess .` (bronze verdict + silver preview)
- [x] 2.2 Confirm it completes in under 10 minutes (runs in seconds)
- [x] 2.3 Note every gap and rough edge encountered

## 3. Fix what dogfooding teaches

- [x] 3.1 Fix bugs / unclear gaps found (licence_consistency false positive; deps_reality tests+alias; secrets .pyc constant-fold) as minimal scoped changes
- [x] 3.2 Re-run until the report is clean and the run is smooth (bronze PASS)

## 4. Commit the annex

- [x] 4.1 No sensitive detail to anonymise (contact is a public issue URL); body reproducible
- [x] 4.2 Commit `report.md` + `report.json` under `reports/`
- [x] 4.3 Verify reproducibility: re-assess the recorded commit → byte-identical body
- [x] 4.4 Reference the committed report in the README (the SIDN Pioniers application links to it)
