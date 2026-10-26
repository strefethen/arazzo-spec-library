# crates.io: Release Dependencies

`release-dependencies` gets one crate's metadata, selects `crate.default_version`,
fetches that exact version, and retrieves its direct dependency requirements.
Features come from the selected version. It does not choose the newest
publication, the first `versions` item, or a hardcoded version. A missing default
or a yanked/mismatched exact version fails instead of selecting a substitute.

Every request is an unauthenticated GET with no request body. No package archive
is requested, installed, built or executed. The output is registry metadata,
not a resolved lockfile, transitive dependency graph, or package-safety verdict.
Dependencies include normal/build/dev kind, target, optional status, default
feature flag, explicit features, and version requirements.

## Offline Verification

Run from the repository root with installed `arazzo-cli` 0.8.2 and jq:

```bash
python3 scripts/verify.py crates.release-dependencies
arazzo-cli --json validate --strict specs/crates/release-dependencies.arazzo.yaml
set -o pipefail
arazzo-cli --json run specs/crates/release-dependencies.arazzo.yaml release-dependencies \
  --dry-run --step get-crate --strict-inputs --input crate=itoa \
  --input user_agent="corpus-fixture/1.0 (fixtures@example.invalid)" \
| jq -er -f views/crates.release-dependencies.summary.jq
```

`fixtures/responses/crates/` and inline scenario bodies are labeled synthetic
data, not live captures. In particular, the synthetic newest prerelease differs
from the selected default. Empty feature maps and dependency arrays are valid.

## Live Limitation

The official API policy requires **at most 1 request/second** and an identifying
User-Agent, preferably with a real contact. This workflow requires an explicit
`user_agent` input; never send the fixture identity to the public API.
Arazzo 1.0.0 has no success delay, and CLI 0.8.2 has no request pacing switch.
`retryAfter` only delays retries after failures; deliberately failing a step
is not a conformant pacing mechanism. Therefore this slice is **fixture-only**
for the current checkpoint; **zero live workflow attempts** were made. Do not
remove `--dry-run` in the command below until a conformant client can enforce
one-second spacing; an identifying User-Agent alone does not raise the limit.

```bash
set -o pipefail
: "${CRATES_USER_AGENT:?Set your application identity and real contact}"
arazzo-cli --json run specs/crates/release-dependencies.arazzo.yaml release-dependencies \
  --dry-run --step get-crate --strict-inputs --max-redirects 0 \
  --input crate=itoa --input user_agent="$CRATES_USER_AGENT" \
| jq -er -f views/crates.release-dependencies.summary.jq
```

There are exactly three logical requests, no retry handlers or pagination
loops. `include=default_version` bounds the metadata version expansion instead
of fetching every release. The dependencies endpoint returns a complete direct
list for that one version and has no page/cursor parameters; the view labels it
unpaginated. It may still be large for a complex crate; this is not a bulk
metadata harvester. crates.io recommends the sparse index or database dumps
where those meet the use case. This slice specifically exercises registry
default-version selection and a JSON dependency response, so it does not
silently substitute another source or invent a resolved dependency set.

## Sources

- [Data access policy](https://crates.io/data-access)
- [Policy source, including 1 request/second](https://github.com/rust-lang/crates.io/blob/main/svelte/src/routes/data-access/+page.svelte)
- [Official experimental OpenAPI](https://crates.io/api/openapi.json)
- [Crate metadata endpoint and include options](https://github.com/rust-lang/crates.io/blob/main/src/controllers/krate/metadata.rs)
- [Arazzo 1.0.0 action fields](https://spec.openapis.org/arazzo/v1.0.0.html#success-action-object)

Documentation checked 2026-10-26. The website API is experimental and may change.
Local companion: `fixtures/openapi/crates/registry.yaml`.

## Verification Record

2026-10-26, installed CLI 0.8.2: strict validation, list/show discovery,
first-step dry-run, and all 8 loopback fixture scenarios passed. Successful jq
projection was asserted, including explicit dependency feature arrays aligned
with the official OpenAPI. Live workflow attempts: 0, by policy.
