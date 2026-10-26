---
status: decomposed
epic: asl-4e2e8
created: 2026-10-26
---

# Useful Arazzo Corpus: First Wave

**Seed:** Steve: "I want you to work autonomously to build an absolutely kickass
corpus of valuable arazzo specs. Something that's truly useful. Tell me how I can
help. Start with the list at the top of this session and start building."
Also: inspect `~/github/arazzo-cli` and surrounding work as the quality bar.

## Bounded Mandate

Steve's 2026-10-26 request delegates selection and implementation of useful
workflows within this repository. This checkpoint bounds the first execution to
six additional public providers from the original shortlist: GitHub, PyPI,
Docker Hub, Open Library, Crossref, and crates.io. Preserve NWS as the canonical
reference; fix stale Socket syntax without calling Socket. No CLI changes,
paid calls, authenticated writes, releases, public GitHub writes, or automation.
One writer per path; read-only independent review. At most one live workflow
attempt plus one diagnostic retry per public provider; no Socket live attempts.
One plan review and one final candidate review, with one correction pass each.
The mandate expires at this wave's verified checkpoint; further waves require
renewal. No credentials are needed to complete the offline acceptance bar.

## Outcome and Non-Goals

An agent can discover, inspect, and execute genuinely useful workflows with the
installed `arazzo-cli` and project useful results with `jq`. Each new workflow
has meaningful response-to-request dataflow, a local documented OpenAPI subset,
provider documentation, and deterministic execution proof. Live success and
offline proof are explicitly separate. Six providers is a cap, not a reason to
accept shallow or broken additions.

No synthetic CRUD demos, blanket API scraping, dependency installation during
verification, mutations to user accounts, or claims that clean vulnerability
metadata proves package safety. Adoption skills follow the proven pattern;
concise repository agent guidance is included now.

## User-Visible Workflows

- GitHub: repository identity -> bounded recent issues/PRs and release metadata.
- PyPI: project -> resolved version -> exact release files, hashes, yanked and
  vulnerability metadata, without downloading or executing packages.
- Docker Hub: repository -> tag metadata -> image platforms and digests.
- Open Library: book search -> selected work -> editions, visibly identifying
  the selected match and avoiding claims of exhaustive search.
- Crossref: DOI -> depositor or journal -> related publication metadata.
- crates.io: crate -> selected version -> dependency requirements and features.
- NWS: preserve address -> coordinates -> grid -> forecast and alerts.
- Socket: conformant, quota-gated, offline-only verification; no free quota use.

## Decision-Relevant Facts

The repository has three specs and response fixtures, but no verifier or Git
commits. Its existing Socket spec uses obsolete runtime-expression and target
syntax. The installed CLI is `arazzo-cli` 0.8.2; `arazzo` is absent. The sibling
CLI checkout contains unrelated uncommitted work and remains read-only.

The original shortlist was recovered from this session's initial API catalog:
public providers above, then Stripe, Twilio, Slack, Notion, GitLab, Jira,
Zendesk, Shopify, Cloudflare, Vercel; later Plaid, Microsoft Graph, Salesforce,
HubSpot, Airtable, Asana, Trello, Intercom, and Socket supply-chain flows.

## Architecture

Keep provider folders, local OpenAPI companions, response fixtures, manifest,
and jq views. `manifest.yaml` remains discovery authority. Add optional
structured test-case references and provenance metadata rather than executing
manifest shell strings. Contributor verification uses Python/PyYAML plus the
real CLI; user workflows still need only CLI and jq.

The verification harness owns testing, not Arazzo parsing or evaluation. It
loads YAML with the installed parser, copies a workflow and its local OpenAPI
companions into a temporary tree, rebases only OpenAPI server URLs to a
loopback fixture server, and executes the CLI unchanged. Ordered request
expectations check method, path, query, headers, and JSON payload. Unexpected
requests fail; all expected requests must be consumed. Reject remote sources,
URL-based operation targets and server overrides before execution; disable
redirects and proxy inheritance for fixture runs. Assert CLI exit status, JSON
kind/code, expected output values/types, and jq projection. No live fallback.
Fixture responses never establish live API compatibility by themselves.

Provider directories own specifications and documentation; `views/` owns
presentation; `tests/` owns scenarios and harness regressions; `scripts/`
owns manifest-driven verification. Avoid inventing a second workflow runner.

## Verification and Risks

Check every entry's files, workflow IDs, source companions, strict CLI
validation, dry-run first steps, and jq output. Execute happy paths and focused
negative cases against loopback fixtures, including empty results, missing
resources, rate limiting, and low Socket quota. Test harness failures so bad
request wiring cannot pass with canned responses. Run bounded, opt-in live
smokes where network permits, then record date, CLI version, and outcome.

Do not leak tokens or private addresses into fixtures. Provider-provided
strings are untrusted data. Anonymous rate limits and provider terms remain
documented; no retries in normal workflows that silently spend quota. Bounded
collections expose pagination information and are never called exhaustive.

## System Success Condition

A single offline command verifies all registered entries and their declared
fixtures without external HTTP traffic. Every newly accepted workflow has
offline end-to-end proof and a documented copy-paste live command with a useful
jq view. The candidate catalog distinguishes built, queued, manual-live, and
blocked work. Final reporting names live successes and limitations separately.

**Disposition:** Decomposed to `asl-4e2e8` / `asl-3c7ae`. Delegated acceptance
2026-10-26 under Steve's autonomous in-repository mandate above. Independent
review identified network-boundary and output-proof requirements, now explicit.
The reported missing Nominatim companion was checked on disk and already exists;
full NWS fixture execution remains required. No live proof is implied.
