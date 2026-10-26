# Candidate APIs

Recovered from the original API shortlist; this is the expansion queue, not a
claim that unbuilt services have been verified. `manifest.yaml` is the inventory
of implemented specifications. The current bounded wave is recorded in
`plans/current/useful-corpus.md` until completed.

## Public First Wave

| Provider | Useful question and workflow | Boundary |
|---|---|---|
| NWS | What's the forecast and every active alert for an address? Address -> coordinates -> grid -> forecast/alerts | US coverage; Nominatim usage policy |
| GitHub | What's happening in this public repository? Identity -> recent releases -> recent issues/PRs | Read-only; anonymous rate limits; bounded pages |
| PyPI | What exactly is this project's resolved release? Project -> exact release -> hashes/files/yanked/vulnerability metadata | Metadata only, never install; not a safety verdict |
| Docker Hub | Which platforms and immutable digests does this tag resolve to? Repository -> tag -> image metadata | Public repos only; mutable tags; no image pull |
| Open Library | Which work matched and which editions are available? Search -> selected work -> editions | First match, bounded editions; conservative pacing |
| Crossref | Who deposited this DOI and what else did they publish? DOI -> member -> related works | Depositor is not necessarily journal/publisher brand; bounded list |
| crates.io | What dependencies/features would this crate version bring? Crate -> version -> dependency requirements | Metadata only; not a dependency lock or audit |
| Socket.dev | What package risk signals are available? Quota -> PURL lookup | Manual-live only; free quota must not be consumed by tests |

## Authenticated Wave

Build only against sandbox/test resources with explicit permissions and budgets.
No credentials belong in this repository. Steve can unlock the next wave by
choosing two or three services and identifying a safe test workspace/account.

| Provider | Candidate workflow | Needed Before Live Proof |
|---|---|---|
| Stripe | Customer -> PaymentIntent -> state -> refund | Test-mode account, key, cleanup policy; never real payments |
| Twilio | Send message -> fetch delivery state | Test credentials or approved destination and spending cap |
| Slack | Find channel -> message -> thread -> history | Development workspace, bot scopes, designated test channel |
| Notion | Query data source -> page -> update | Test workspace and current versioned API contract |
| GitLab | Project -> MR -> pipeline status | Public read-only first; sandbox for writes |
| Jira Cloud | Issue -> comment -> transition -> JQL | Test project and allowed transitions |
| Zendesk | Ticket -> attachment token -> comment -> solve | Sandbox and retention/cleanup rules |
| Shopify | Product -> inventory -> fulfillment | Development store; choose REST/GraphQL compatibility intentionally |
| Cloudflare | Zone -> DNS record lifecycle | Dedicated test zone and narrowly scoped token |
| Vercel | Project -> deployment -> alias | Test project with deployment/cost limits |

## Later Coverage

Plaid sandbox token exchange and transaction sync; Microsoft Graph OAuth and
calendar/mail/files; Salesforce, HubSpot, Airtable, Asana, Trello and Intercom
for CRM/productivity/support. Add them when they demonstrate a new valuable
workflow, not merely to increase provider counts.

## Selection Rule

Prefer clear user outcomes, real inter-step dataflow, useful outputs, reproducible
negative cases, and cheap proof. Keep pagination, async completion, authentication,
idempotency, and destructive operations explicit. One complete vertical slice
beats many validation-only files.
