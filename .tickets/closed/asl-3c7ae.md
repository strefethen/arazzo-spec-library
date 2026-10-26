---
title: Deliver the first useful offline-verified API workflow corpus
type: chore
priority: 3
resolution: completed
close_reason: 233d6be six new provider workflows, 27 unit tests, 59 offline scenarios and independent candidate review PASS; four bounded live smokes, zero Socket quota
created_at: 2026-10-26T18:34:07Z
last_changed: 2026-10-26T18:57:30Z
plan: plans/current/useful-corpus.md
files:
    AGENTS.md: c
    README.md: m
    docs/**: m
    fixtures/openapi/crates/**: c
    fixtures/openapi/crossref/**: c
    fixtures/openapi/dockerhub/**: c
    fixtures/openapi/github/**: c
    fixtures/openapi/nws/**: r
    fixtures/openapi/openlibrary/**: c
    fixtures/openapi/pypi/**: c
    fixtures/responses/crates/**: c
    fixtures/responses/crossref/**: c
    fixtures/responses/dockerhub/**: c
    fixtures/responses/github/**: c
    fixtures/responses/nws/**: r
    fixtures/responses/openlibrary/**: c
    fixtures/responses/pypi/**: c
    manifest.yaml: m
    scripts/**: c
    specs/crates/**: c
    specs/crossref/**: c
    specs/dockerhub/**: c
    specs/github/**: c
    specs/nws/**: r
    specs/openlibrary/**: c
    specs/pypi/**: c
    specs/socket/package-risk-triage.arazzo.yaml: m
    tests/**: c
    views/*.jq: m
changes:
    - at: 2026-10-26T18:56:48.094418Z
      action: close
      from: in_progress
      to: closed
      resolution: completed
      reason: 233d6be six new provider workflows, 27 unit tests, 59 offline scenarios and independent candidate review PASS; four bounded live smokes, zero Socket quota
assignee: codex
---
# Deliver the first useful offline-verified API workflow corpus

## Goal
Deliver the bounded useful first wave authorized by Steve on 2026-10-26: six real API workflows with trustworthy offline execution proof, preserving NWS and Socket quota.

## Design
Use the provider/OpenAPI/response/view ownership already present in manifest.yaml and specs/nws/address-forecast.arazzo.yaml. Use the installed arazzo-cli 0.8.2 public validate/list/show/run surfaces. Companion documents remain local; the Python/PyYAML verifier copies and rebases only server URLs into a temporary loopback tree and strictly matches recorded requests without executing manifest shell commands. Six providers: GitHub, PyPI, Docker Hub, Open Library, Crossref, crates.io. Preserve existing files; no sibling CLI writes, authenticated mutations or Socket live calls. Optional live smokes report independent evidence, not a completion prerequisite. Decided by recommendation: CLI+jq for user commands and existing installed PyYAML for contributor verification.
### File Impact
- Modify: README.md, manifest.yaml, docs corpus/reference navigation, specs/socket/package-risk-triage.arazzo.yaml: integrate and conform the corpus; preserve NWS behavior.
- Create: scripts/verify.py and scripts/fixture_server.py own contributor verification and strict HTTP fixture transport; tests/ owns scenarios/regressions; provider folders under specs/, fixtures/openapi/, fixtures/responses/, views/ own six additions; AGENTS.md owns local conventions; docs/corpus/candidate-apis.md owns shortlist.
- Must not grow: sibling arazzo-cli runtime; no custom expression evaluator or Arazzo parser.
### Inputs / Outputs
Manifest version 1 gains optional tests and documentation/provenance metadata. Test scenarios declare workflow, inputs, ordered HTTP expectations and expected output subset/error; no shell evaluation.

## Acceptance Criteria
- Six new provider workflows have useful response-to-request dataflow, local OpenAPI companions, provider READMEs, jq views and manifest discovery.
- One offline command validates/discovers/dry-runs every entry and executes deterministic fixtures, failing on bad requests, missing outputs and unconsumed expectations.
- Existing NWS works with fixture execution; Socket validates with corrected syntax, proves low-quota stop offline, and receives zero live calls.
- Candidate catalog and agent guidance make scope, evidence levels, safe usage and next authenticated-wave gates clear.

## Testing Obligations
- Run python3 -m unittest discover -s tests -p 'test_*.py' for harness regressions including wrong query/header/body, extra/missing requests, malformed manifests and output mismatches.
- Run python3 scripts/verify.py across all manifest entries using arazzo-cli 0.8.2 and jq; include positive and negative workflow scenarios.
- Inspect documented copy-paste commands and jq projections; bounded public-provider live smoke attempts must be reported with date/outcome separately from fixture proof.
- Obtain read-only fresh candidate review covering specs, request expectations and default no-external-network behavior; correct blocking findings.


### Evidence
Candidate: 233d6bebee2c9c65a40748d01d5a27d9741e631c. Independent fresh-context ticket-code-review returned PASS (agent 01a1798f-6ed3-7631-8a6b-47ec298965d2), bound to the retained contract and notes-only revision 8471a1af8f1aa68b30aba5aae92f84601ab587ae6044407b1fe4381828e6f000.

The reviewer independently reran 27 unit tests and 59 complete fixture scenarios on candidate-matching source with CLI 0.8.2. actionlint and the staged whitespace check passed. All four Acceptance Criteria and all Testing Obligations passed. Four bounded public-provider live observations are recorded in the provider READMEs and plans/assessments/corpus-first-wave-2026-10-26.md; they were not repeated for review. Socket received zero live calls.

The repository had no prior commit: pre-candidate tkt scope failed because HEAD was absent. The initial file inventory, ready local files check and explicit path staging supplied the baseline; adjacent changes are documented in notes. The unchanged VS Code launch configuration and empty placeholders were excluded. No sibling CLI writes, remote push or GitHub CI run occurred. Open Library identity and crates.io pacing prerequisites remain explicitly gated; no all-provider live-completion claim is made.

## Note (2026-10-26 18:49 UTC)
Decided by recommendation: allow a valid empty final Open Library edition page while preserving work metadata; retain failure for no search match/unresolved work. New discovery fact: installed catalog is provider-local, not recursive; docs corrected. Adjacent forecast expansions: NWS point syntax migration, all-alert projection, strict geocode and alert-presence guards; requirements-dev and offline CI config added. Baseline had no Git commits; tkt scope cannot operate until initial candidate exists. Unchanged .vscode/ and invalid/ remain outside candidate.

## Note (2026-10-26 18:52 UTC)
Current official provider contracts checked; four new providers live-proved within budgets. Open Library and crates.io remain explicitly dry-run because contact/pacing gates are outside this slice. Discovered CLI0.8.2 ignores numeric JSON Schema bounds: added standard simple input-bound criteria after small identity requests, before any collection query, with four negative scenarios. No custom parser or artificial retries. Separate CLI gap captured as paused asl-fab23.

## Note (2026-10-26 18:56 UTC) — Closed
233d6be six new provider workflows, 27 unit tests, 59 offline scenarios and independent candidate review PASS; four bounded live smokes, zero Socket quota
