# Change: apply-docs-contract

> Seed-change, aangeleverd vanuit Westmarch (personal-handbook, change 2
> add-docs-contract). Uitvoering door een habitat-builder-Job; merge door Mark.

## Why

estafette is NLnet-traject-repo; er liggen 3 spec-pagina's los in docs/ zonder contractstructuur.
Zonder uniform contract is handbook-aggregatie zinloos: het handbook (hub)
importeert `docs/` van dit repo at build time.

## What changes

- `docs/` volgens het contract hieronder (additief + migratie van bestaande
  docs; geen verwijderingen buiten wat hieronder expliciet staat).
- `.mcp.json` in de root volgens template (handbook-URL blijft placeholder
  `TODO-change-3`).
- Géén andere wijzigingen. Eén branch, één PR, titel:
  `docs: apply handbook docs contract`.

## Docs-contract (bindend, uit Westmarch add-docs-contract)

```
docs/
  index.md          # wat is dit, status, max 3 regels boilerplate
  how-to/           # taakgericht
  reference/        # feiten (config, API, schema's)
  explanation/      # waarom-besluiten; ADR's onder explanation/adr/NNNN-titel.md
```

- Lege mappen weglaten. Minimum viable: `index.md` + één reference-pagina.
- Front matter per pagina (YAML): `status: current|draft|deprecated` +
  `last_reviewed: <ISO-datum>`. GEEN `owner`-veld.
- Gemigreerde pagina's zonder inhoudelijke review: `status: draft`,
  `last_reviewed` = migratiedatum. Alleen een echte review zet `current`.
- Eén taal per repo (deze repo: English).
- README blijft; `docs/index.md` verwijst ernaar, vervangt niet.
- Bestaande losse docs migreren; stub met verwijzing achterlaten op de oude
  plek als er externe links naartoe kunnen bestaan.


## Repo-specifiek

- `docs/catalog-spec.md`, `docs/manifest-spec.md`, `docs/tiers.md` →
  `docs/reference/`; stubs achterlaten (er kunnen externe links bestaan).
- `docs/index.md` nieuw: wat is estafette (PoC-overdraagbaarheids-assessment),
  status, link README + reference.
- Interne hostnaam komt voor in `openspec/project.md` en archief: BUITEN
  scope (geen openspec-wijzigingen); alleen vermelden in de PR-body.
- Taal: Engels (publiek open-source-repo).

## Non-goals

- Geen merge (Mark merget), geen scope buiten deze change, geen wijzigingen
  aan CLAUDE.md / .claude/agents/ / CI.
