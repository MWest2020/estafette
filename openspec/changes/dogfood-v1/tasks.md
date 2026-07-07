## 1. Select target and write manifest

- [ ] 1.1 Choose ONE real PoC operations are permitted on (prefer an own archived PoC); record the rationale
- [ ] 1.2 Author an honest `transfer.yaml` (licence, owner, contact, status, deps, build if applicable)

## 2. Run end to end

- [ ] 2.1 Run `uvx estafette assess <repo>` (bronze verdict + silver preview)
- [ ] 2.2 Confirm it completes in under 10 minutes; record actual timing out-of-body
- [ ] 2.3 Note every gap and rough edge encountered

## 3. Fix what dogfooding teaches

- [ ] 3.1 Fix bugs / unclear gaps / brittle parsing found, as minimal scoped changes to the owning capability
- [ ] 3.2 Re-run until the report is clear and the run is smooth

## 4. Commit the annex

- [ ] 4.1 Anonymise any sensitive detail without changing the recorded commit's real body
- [ ] 4.2 Commit `report.md` + `report.json` under `reports/`
- [ ] 4.3 Verify reproducibility: re-assess the recorded commit → byte-identical body
- [ ] 4.4 Reference the committed report in the SIDN Pioniers application; note the link in the README
