# Corpus First-Wave Checkpoint

Date: 2026-10-26. CLI: installed `arazzo-cli` 0.8.2. Scope: `asl-3c7ae`,
under `asl-4e2e8`; original intent and bounded mandate in
`plans/current/useful-corpus.md`.

## Delivered Evidence

- Nine workflow specifications, including six new providers from the original
  shortlist, local OpenAPI companions, provider READMEs, manifest metadata,
  synthetic JSON fixtures, exact request expectations, and jq projections.
- `python3 scripts/verify.py`: 59 passing full-chain scenarios, including
  negative termination paths. No live provider requests by this command.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 27 passing harness
  regressions. Guards cover external sources/servers/redirects, wrong requests,
  missing expectations, output types, malformed/duplicate manifest entries,
  unregistered specs and path escapes.
- CLI 0.8.2 accepts numeric inputs outside JSON Schema min/max constraints even
  with `--strict-inputs`. Collection workflows explicitly gate those bounds
  after the first small identity request, before fetching collections. The
  separate CLI gap is captured in `asl-fab23`; no runtime changes were made.
- NWS canonical address remains Apple Headquarters; full active-alert lists
  are exposed and rendered. Coordinate-only NWS and Socket obsolete expression
  syntax migrated. Socket low quota and rejected auth stop before lookup.
- CI source installs pinned tooling and then runs offline checks. It has not
  run on GitHub: this repository currently has no remote. CLI sibling checkout
  and existing `.vscode/launch.json` remain untouched.

## Live Proof, Separately

Provider READMEs carry exact commands, source links, and detailed boundaries.

| Provider | Attempts in this wave | Observation |
|---|---|---|
| GitHub | One, no retry | Public repository -> 2 releases -> 2 issues/PRs; jq passed |
| PyPI | One, no retry | sampleproject 4.0.0 -> 2 release files and advisory metadata; no artifact downloads |
| Docker Hub | One, no retry | library/alpine -> selected latest tag -> 16 image records; no image pull |
| Crossref | One plus one diagnostic retry | Publication sort + cursor returned 400; corrected indexed sort then passed DOI -> member 297 -> 2 works + cursor |
| NWS | None | Existing workflow verified with fixtures, no new live claim |
| Open Library | None | Fixture proof only; real contact identity and exclusive identified rate budget needed |
| crates.io | None | Fixture proof only; CLI cannot enforce policy-required successful-request spacing |
| Socket | Zero | No token or quota used |

## Decisions and Remaining Gates

Decided by recommendation: retain provider layout; CLI+jq for users; PyYAML
safe loading for contributor tooling; no custom expression evaluator; strict
loopback-only fixture routing; allow an empty final edition page while preserving
the resolved work. No paid or authenticated write workflows added.

`asl-2c490` is paused on Steve's approval for a separately scoped CLI pacing
capability. No artificial failed requests or hidden retry delays were added.
Open Library and crates.io are honestly registered as `dry-run`, not live-ready.
System success for fully policy-compliant live use of all six additions is
therefore not yet achieved; the offline implementation slice is complete.

For the next wave, Steve can pick two or three services and provide safe test
accounts/workspaces, permitted actions, cleanup rules and spending caps. Stripe
must stay test-mode; Slack needs a designated development channel. No keys should
be pasted into chat or committed. New wave scope requires renewal of the bounded
mandate; this checkpoint is not an unattended recurring job.
