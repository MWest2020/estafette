---
status: draft
last_reviewed: 2026-07-12
---

# estafette — documentation

**estafette** mechanically assesses whether a public-sector proof of concept is
*transferable* — whether someone who was not involved can pick it up — and emits
a deterministic transferability report with a tier verdict. It is a CLI that
orchestrates existing scanners rather than reinventing them.

**Status:** v1 complete (bronze verdict + report); v2 in progress (the
catalogue platform). See the [README](../README.md) for installation, usage, and
the project overview.

## Reference

- [Transferability tiers](reference/tiers.md) — normative tier criteria (bronze
  implemented; silver/gold roadmap).
- [Transfer manifest specification](reference/manifest-spec.md) — the declared,
  machine-readable manifest estafette checks against reality.
- [PoC catalogue — entry specification](reference/catalog-spec.md) — the entry
  model behind the catalogue.
