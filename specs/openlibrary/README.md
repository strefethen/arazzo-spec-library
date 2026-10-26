# Open Library: Book Editions

`book-editions` searches for one relevance-ranked match, resolves that work, then
requests a bounded edition page. It exposes the selected match, work key, search
total, edition limit and offset. It does not claim an exhaustive search. Every
operation is an unauthenticated GET with no request body.

The documented Query API accepts complete `/works/OL...W` keys through `key` and
`works` query parameters. The workflow passes those keys unchanged: no hardcoded
substring extraction, double `/works` prefix, or encoded slash path ambiguity.
An empty search or unresolved work fails before later requests. An empty edition
page is valid and still returns the selected work metadata.

## Offline Verification

Run from the repository root with installed `arazzo-cli` 0.8.2 and jq:

```bash
python3 scripts/verify.py openlibrary.book-editions
arazzo-cli --json validate --strict specs/openlibrary/book-editions.arazzo.yaml
set -o pipefail
arazzo-cli --json run specs/openlibrary/book-editions.arazzo.yaml book-editions \
  --dry-run --step search-books --strict-inputs \
  --input query="The Wonderful Wizard of Oz" \
  --input user_agent="corpus-fixture/1.0 (fixtures@example.invalid)" \
| jq -er -f views/openlibrary.book-editions.summary.jq
```

`fixtures/responses/openlibrary/` and the scenario inline responses are synthetic
test data, not live captures. Scenarios assert exact queries, header subsets,
empty HTTP request bodies, success outputs and failed-criteria error codes.

## Live Limitation

Open Library allows **1 request/second** for unidentified clients, or **3/second**
with an application name and operator contact email in `User-Agent`. The input
has no anonymous default. Do not send the fixture identity to a public service.

Arazzo 1.0.0 success actions support `goto` and `end`, but no pause. `retryAfter`
belongs to failure retry actions; it cannot pace successful steps. CLI 0.8.2
also has no inter-request throttle. There are no artificial failures, extra
requests, external delay endpoints, or undocumented delay extensions here.
This slice is therefore fixture-only for this checkpoint; **zero live workflow
attempts** were made. Main owns the decision to enable later live proof.

Future identified, opt-in command (three serial requests, no retries):

```bash
set -o pipefail
: "${OPENLIBRARY_USER_AGENT:?Set an application name and real contact email}"
arazzo-cli --json run specs/openlibrary/book-editions.arazzo.yaml book-editions \
  --strict-inputs --max-redirects 0 \
  --input query="The Wonderful Wizard of Oz" \
  --input user_agent="$OPENLIBRARY_USER_AGENT" \
  --input-json edition_limit=5 --input-json edition_offset=0 \
| jq -er -f views/openlibrary.book-editions.summary.jq
```

Reserve the entire identified 3-request budget for this run; do not overlap or
loop it. Stop on 429. The Query API exposes no total or next link. The jq view
reports returned count and offset, and suggests the next offset only for a full
page. A full page is not proof of another page; the search edition count is not
an exact count for this Query API snapshot. The workflow caps each page at 10
editions and never follows pagination automatically.

## Sources

- [API policy and limits](https://openlibrary.org/developers/api)
- [Search API, fields and pagination](https://openlibrary.org/dev/docs/api/search)
- [RESTful Query API, field projection, limit and offset](https://openlibrary.org/dev/docs/restful_api)
- [Works and editions](https://openlibrary.org/dev/docs/api/books)
- [Arazzo 1.0.0 success and failure actions](https://spec.openapis.org/arazzo/v1.0.0.html#success-action-object)

Documentation checked 2026-10-26. Local companion:
`fixtures/openapi/openlibrary/catalog.yaml`.

## Verification Record

2026-10-26, installed CLI 0.8.2: strict validation, list/show discovery,
first-step dry-run, and all 7 loopback fixture scenarios passed. Successful jq
projection was asserted by the harness. Live workflow attempts: 0, by policy.
