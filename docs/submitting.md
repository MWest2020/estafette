---
status: draft
last_reviewed: 2026-09-03
---

# Submitting a PoC to the catalogue

There are two ways to get a proof of concept into the catalogue. Both produce the
same thing — a `PoCEntry` (see [`catalog-spec.md`](reference/catalog-spec.md)) — they only
differ in how it arrives. No account, no server: submission is a pull request or a
file the harvester finds.

## 1. Submit by pull request (open, zero infra)

1. Add one file `catalog/<your-poc>.yaml` with the entry fields (see the contract
   in [`catalog-spec.md`](reference/catalog-spec.md#the-pocyaml--catalogyaml-contract)).
2. Open a pull request. CI runs `estafette catalogue --check`, which validates
   every `catalog/*.yaml` against the schema and **fails the PR** naming the first
   invalid file and reason. A green check means the entry is well-formed.
3. A maintainer reviews and merges — review is the only human gate.

Validate locally before you push:

```bash
uv run estafette catalogue --check --catalog catalog
```

## 2. Host a `poc.yaml` and let the harvester pull it

If you would rather keep the entry in your own repo:

1. Put a `poc.yaml` at the **root** of your public repo — same schema as a
   `catalog/*.yaml`. (Already have a `publiccode.yml`? You can skip `poc.yaml`;
   the harvester falls back to it and wraps it as `kind: code`. `poc.yaml` wins
   when both are present.)
2. Ask a maintainer to add your repo's raw base URL to `sources.yaml`, e.g.
   `https://raw.githubusercontent.com/<org>/<repo>/HEAD`.
3. `estafette harvest` (run in CI before the site build) fetches your `poc.yaml`
   and merges it into the catalogue. A local `catalog/*.yaml` with the same
   `name` always wins over a harvested entry.

```bash
uv run estafette harvest --sources sources.yaml --catalog catalog
uv run estafette catalogue --catalog catalog --out site
```

A source that 404s, times out, or ships an invalid entry is **skipped with a
recorded reason** — never fatal to the build.
