# Habitat builder — apply-docs-contract

_run_id builder-apply-docs-contract-20260712-184214 · verdict ok · 2026-07-12T18:46:07Z_

---

Done. Change **`apply-docs-contract`** is implemented and pushed. STOP here per role — Mark merges.

## Run report

**Branch:** `habitat/builder/apply-docs-contract` (pushed to origin). Commits: `fc4ba97` (docs contract) + `85a2498` (task note).

### What I did (tasks 1.1–3.1 ✅, 4.1 blocked on tooling)

- **Migrated** `docs/{catalog-spec,manifest-spec,tiers}.md` → `docs/reference/` with content intact.
- **Deprecated stubs** left at the three old paths, pointing to the new location (external links may exist — README links to all three).
- **`docs/index.md`** added: what estafette is, status (v1 done / v2 in progress), link to README, links to the reference section.
- **Front matter** on every page: `status` + `last_reviewed: 2026-07-12`, **no** `owner`. Migrated-without-review = `draft`; stubs = `deprecated`; new index = `draft`.
- **Empty `how-to/` and `explanation/` dirs omitted** (minimum viable = index + one reference page).
- **`.mcp.json`** was already correct from the seed (template, placeholder `TODO-change-3`) — no change needed (task 2.4).
- **Self-check** passed: only `docs/reference/` carries subdir markdown; stubs at root are contract-sanctioned; every page has front matter; language English throughout. REUSE is covered by the blanket `**` annotation in `REUSE.toml` (no per-file headers needed).

### Task 4.1 — PR could not be opened automatically
No `gh` CLI and no GitHub token in this environment. **Please open the PR manually:**

- **Open URL:** https://github.com/MWest2020/estafette/pull/new/habitat/builder/apply-docs-contract
- **Title:** `docs: apply handbook docs contract`
- **Ready-to-paste body** (contract checklist + PR-body-only notes):

```markdown
Applies the handbook docs contract (Westmarch `add-docs-contract`, change 2) to
this repo. Execution by a habitat-builder Job; **merge by Mark**.

## Contract points applied
- [x] `docs/` follows the contract: `index.md` at the root + a `reference/` section. Empty `how-to/` and `explanation/` dirs omitted.
- [x] Existing loose docs migrated to `docs/reference/`: `catalog-spec.md`, `manifest-spec.md`, `tiers.md`.
- [x] Deprecated stubs left at the old paths, pointing to the new location (external links may exist).
- [x] `docs/index.md` added: what estafette is, status, link to README, links to reference.
- [x] YAML front matter on every page: `status` + `last_reviewed`, no `owner`. Migrated = `draft` / `last_reviewed: 2026-07-12`; stubs = `deprecated`.
- [x] One language: English. README kept; index links to it, does not replace it.
- [x] `.mcp.json` present per the seed template; placeholder `TODO-change-3` left in place (resolved in change 3).

## Notes for the reviewer (out of scope, PR-body only)
- The internal hostname appears in `openspec/project.md` and the archive — outside scope of this change (no OpenSpec edits made); flagged for awareness only.
- REUSE covered by the blanket `**` annotation in `REUSE.toml`. (`reuse lint` couldn't run in the build env — missing charset module, unrelated to these changes.)

## Non-goals
No merge (Mark merges), no scope outside this change, no edits to CLAUDE.md / `.claude/agents/` / CI.
```

One thing worth flagging: task 1.1 named branch `docs/contract`, but the habitat Job set up `habitat/builder/apply-docs-contract`. I worked on that existing non-main branch rather than create a second one — the intent (work off a branch, not main; PR into `main`) holds. Rename before opening the PR if you prefer the `docs/contract` name.
