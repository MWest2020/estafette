## Context

By this point the engine produces a bronze verdict and a report. Dogfooding is
where the engine meets a repository nobody tailored for it — the real test of
"can someone who wasn't involved get this running?" applied to estafette itself
being useful. The output is the SIDN annex, so honesty and reproducibility beat
a flattering verdict.

## Goals / Non-Goals

**Goals:**

- One real PoC assessed end to end, verdict + silver preview, under 10 minutes.
- Fixes for whatever the run exposes, kept minimal and fed to the right capability.
- A committed, reproducible, anonymised annex report.

**Non-Goals:**

- No new engine capabilities — this validates and hardens existing ones.
- No cherry-picking a repo guaranteed to pass; a report with honest gaps is more
  credible for the grant than a green one.

## Decisions

- **Target selection is the first task, and is environment-constrained.** Prefer
  an own archived PoC to avoid operating on third-party or restricted repos.
  (Note: some org repos — e.g. Conduction's — are off-limits to this agent; the
  target must be one operations are permitted on.) Record why the target was
  chosen.
- **Author an honest `transfer.yaml`.** Declare licence, owner, contact, status,
  deps, and a `build` section if a Containerfile exists. Do not massage it to
  pass — the gaps are the product (I3).
- **Fix forward, minimally.** Bugs found become small, scoped commits against the
  owning capability (a check, the harness, the report). Resist rewrites.
- **Anonymise before committing.** Reports locate secrets without echoing them
  (I5), but scrub any incidental sensitive detail (internal hostnames, personal
  emails) from the committed copy while keeping the body reproducible.
- **Reference the annex in the application.** The committed report path is what
  the SIDN Pioniers application links to.

## Risks / Trade-offs

- **The chosen PoC may fail bronze.** That is acceptable and arguably better —
  an honest gap report demonstrates the tool working. Document the verdict as-is.
- **Anonymisation vs reproducibility.** Scrubbing must not change the recorded
  commit's real body, or reproducibility breaks. Mitigation: anonymise the
  target inputs (or use a synthetic fork) so the recorded body is the real body.
- **10-minute budget.** syft/harness on a large repo can be slow. Mitigation:
  pick a small-to-medium PoC; record actual timing out-of-body.
- **Environment limits.** If no permitted target can build (no podman / network),
  the silver preview will read "not assessable" — still a valid, honest annex;
  bronze is the real verdict.
