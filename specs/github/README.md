# GitHub Repository Activity

`repository-activity` makes three anonymous GET requests: repository identity,
one bounded releases page, and one bounded recently updated issues/PRs page.
Resolved owner/name values become the canonical identity used in later requests.
Empty releases are valid: this uses `GET /releases`, not `/releases/latest`.

Run from the repository root with installed `arazzo-cli` 0.8.2+ and jq:

```bash
set -o pipefail
arazzo-cli --json run specs/github/repository-activity.arazzo.yaml repository-activity \
  --strict-inputs --input-json 'owner="cli"' --input-json 'repo="cli"' \
  --input-json 'page=1' --input-json 'per_page=5' \
  --http-timeout 10s --execution-timeout 30s --max-response-size 2097152 \
| jq -er -f views/github.repository-activity.summary.jq
```

No-network discovery, validation, and first-step request preview:

```bash
set -o pipefail
arazzo-cli --json catalog specs/github
arazzo-cli --json validate specs/github/repository-activity.arazzo.yaml --strict
arazzo-cli --json run specs/github/repository-activity.arazzo.yaml repository-activity \
  --dry-run --strict-inputs --step resolve-repository \
  --input-json 'owner="cli"' --input-json 'repo="cli"' \
| jq -er -f views/github.repository-activity.summary.jq
```

## Contract And Limits

- Official sources checked 2026-10-26: [repository](https://docs.github.com/en/rest/repos/repos#get-a-repository),
  [releases](https://docs.github.com/en/rest/releases/releases#list-releases),
  [issues](https://docs.github.com/en/rest/issues/issues#list-repository-issues),
  and [rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
- Public resources only, no token or authorization header. The default User-Agent
  is `arazzo-spec-library (https://github.com/strefethen/arazzo-spec-library)`.
  The workflow pins API version `2022-11-28`, verified by the smoke below.
- `per_page` defaults to 5 and is capped at 30; `page` is 1-100. Both collections
  expose their `Link` headers; absent links are null. No page links are followed.
  The same requested page applies independently to both collections, not a joined
  timeline. Issues include PRs, identified by `pull_request` in jq. Releases are
  published releases, not all Git tags; no claim of semver ordering or completeness.
- Anonymous requests share a 60-request/hour IP limit. Rate headers from the final
  response are exposed. Status failures, including 403/429, stop the workflow;
  no retry or failure-to-success conversion is configured. Respect reset/retry
  instructions before running again.
- The local OpenAPI is a hand-maintained subset. CLI success criteria check status
  and required identity data, not the whole provider response schema. jq guards
  collection types and exits nonzero on error envelopes or malformed collections.
  Metadata is not a security or maintenance-quality verdict.

## Evidence

All JSON under `fixtures/responses/github/` and all inline scenario bodies are
synthetic contract examples, not captures. `tests/scenarios/github.repository-activity.yaml`
asserts request paths, queries, headers, output identity/types, pagination, empty
collections, missing identity, missing resources, and rate limiting. Fixture
execution is offline and does not establish current provider behavior.

Live smoke on 2026-10-26 using `arazzo-cli` 0.8.2: one attempt against `cli/cli`
with `per_page=2` succeeded, returning 2 releases and 2 issues/PRs with pagination
links. No retry used. This is one observation, not an availability guarantee.
