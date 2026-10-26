# Crossref: DOI Provenance

`doi-provenance` resolves a Crossref DOI, follows its `member` identifier to the
depositing organization, then fetches one bounded cursor page of that member's
recently indexed publication metadata. All three requests are unauthenticated GETs with
no request body. A non-Crossref DOI can return 404.

The workflow deliberately does not require ISSN, journal title, or any other
journal-only field. The view distinguishes publisher metadata from depositing
member provenance. Related means **same depositor**, not topic similarity,
citations, or current ownership. The seed DOI can appear among the results.

## Run

From the repository root, with installed `arazzo-cli` 0.8.2 and jq:

```bash
set -o pipefail
arazzo-cli --json run specs/crossref/doi-provenance.arazzo.yaml doi-provenance \
  --strict-inputs --max-redirects 0 \
  --input doi=10.1038/nphys1170 --input-json rows=5 \
  --input user_agent=arazzo-spec-library/1.0 \
| jq -er -f views/crossref.doi-provenance.summary.jq
```

Only 1-10 works are requested. `cursor` defaults to `*`; the workflow exposes
`next_cursor`, total result count, and requested row count. To inspect a later
page, pass `--input cursor='THE_RETURNED_CURSOR'`. No cursor is automatically
followed. Ordering is by indexing time, not publication date: Crossref rejects
`sort=published` together with a cursor. A short or empty page is the end of the cursor result set, even if
the API still returns a next cursor. DOIs are case-insensitive; identity checks
use Arazzo's case-insensitive comparison and verify the member linkage.

## Limits and Provenance

The public pool currently advertises 5 requests per second and concurrency 1;
the polite pool advertises 10 and concurrency 3. This workflow is serial and
does not opt into a paid pool or require a token. Inspect provider rate and
concurrency headers for current limits. A descriptive contact User-Agent is
recommended for real use; override `user_agent` with your application identity.
Do not run with `--parallel`, loop aggressively, or retry a 429 automatically.
Errors propagate and the jq view uses `error()` so `pipefail` preserves failure.

## Offline Verification

```bash
python3 scripts/verify.py crossref.doi-provenance
arazzo-cli --json validate --strict specs/crossref/doi-provenance.arazzo.yaml
set -o pipefail
arazzo-cli --json run specs/crossref/doi-provenance.arazzo.yaml doi-provenance \
  --dry-run --step get-doi --strict-inputs --input doi=10.1038/nphys1170 \
| jq -er -f views/crossref.doi-provenance.summary.jq
```

The files in `fixtures/responses/crossref/` and inline scenario bodies are
synthetic, not provider captures. The suite includes missing journal fields,
empty cursor pages, wrong DOI/member identity, 404 and 429, with no retries.

## Sources

- [Official REST API documentation and cursor behavior](https://github.com/CrossRef/rest-api-doc)
- [API access pools and rate limits](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/)
- [Response formats](https://github.com/CrossRef/rest-api-doc/blob/master/api_format.md)

Documentation checked 2026-10-26. Local companion:
`fixtures/openapi/crossref/metadata.yaml`. Live proof is reported separately from
fixture verification; fixtures never establish current service availability.

## Verification Record

2026-10-26, installed CLI 0.8.2: strict validation, list/show discovery,
first-step dry-run, and all 8 loopback fixture scenarios passed, including jq
projection. One live attempt resolved DOI and member but got HTTP 400 for the
cursor/publication-sort combination. After switching to `sort=indexed`, the one
permitted diagnostic retry passed end to end, including jq with `pipefail`:
`10.1038/nphys1170` -> member `297` -> 2 member works and a next cursor. No more
live attempts were made and no automatic retry handlers exist in the workflow.
