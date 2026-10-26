# Docker Hub Tag Platforms

`repository-tag` makes three anonymous public metadata GET requests: repository,
one bounded tag page, then detail for the first returned tag. Repository identity
and selected tag identity feed later requests. The view reports platform image
digests; it does not log in, pull images, or contact registry endpoints.

Run from the repository root with installed `arazzo-cli` 0.8.2+ and jq:

```bash
set -o pipefail
arazzo-cli --json run specs/dockerhub/repository-tag.arazzo.yaml repository-tag \
  --strict-inputs --input-json 'namespace="library"' --input-json 'repository="alpine"' \
  --input-json 'page=1' --input-json 'page_size=5' \
  --http-timeout 10s --execution-timeout 30s --max-response-size 2097152 \
| jq -er -f views/dockerhub.repository-tag.summary.jq
```

No-network discovery, validation, and first-step request preview:

```bash
set -o pipefail
arazzo-cli --json catalog specs/dockerhub
arazzo-cli --json validate specs/dockerhub/repository-tag.arazzo.yaml --strict
arazzo-cli --json run specs/dockerhub/repository-tag.arazzo.yaml repository-tag \
  --dry-run --strict-inputs --step resolve-repository \
  --input-json 'namespace="library"' --input-json 'repository="alpine"' \
| jq -er -f views/dockerhub.repository-tag.summary.jq
```

## Contract And Limits

- Official sources checked 2026-10-26: [repository](https://docs.docker.com/reference/api/hub/latest/operations/GetRepository/),
  [tag pages](https://docs.docker.com/reference/api/hub/latest/operations/ListRepositoryTags/),
  [tag detail](https://docs.docker.com/reference/api/hub/latest/operations/GetRepositoryTag/),
  [image schema](https://docs.docker.com/reference/api/hub/latest/schemas/image/),
  and [API limits](https://docs.docker.com/reference/api/hub/latest/).
- Use the documented `/v2/namespaces/.../repositories/...` routes. Repository docs
  explicitly permit anonymous public reads; current tag operation docs advertise
  bearer auth. Anonymous tag access is an observed compatibility boundary, proven
  only for the public smoke below, not a promise for private or all repositories.
  An auth restriction fails visibly; there is no login or legacy-route fallback.
- Default User-Agent:
  `arazzo-spec-library (https://github.com/strefethen/arazzo-spec-library)`.
  `page_size` is 1-20 (default 5); `page` is 1-100. Selection is index zero in
  provider order, not necessarily `latest`, newest, semver-highest, or stable.
  Tag count, `next`, and `previous` are exposed; no pagination URLs are followed.
- Tag detail's image records are unpaginated. Raw output retains all records;
  jq shows at most 30 with total count. Digests identify platform image records,
  not a separately verified top-level multi-platform manifest digest. Unknown
  platform records can include attestations, not runnable targets. Later missing
  digests are shown as unavailable; the first record must have a SHA-256 digest.
- Empty tag pages, missing images/first digest, changed tag identity, 404, and
  429 fail with no retry. Tags can change between requests. API throttling uses
  rate headers and 429/`Retry-After`, separate from image pull limits. Respect it.
- The local OpenAPI is a hand-maintained subset; CLI criteria do not validate the
  full response schema. jq guards image-array shape and errors on failure
  envelopes. Neither platform nor digest metadata is a security verdict.

## Evidence

All JSON under `fixtures/responses/dockerhub/` and inline scenario bodies are
synthetic, including invented digests; none are live captures.
`tests/scenarios/dockerhub.repository-tag.yaml` asserts requests, selected-tag
dataflow, platform digests, pagination, empty pages/images, private and missing
repositories, throttling, and changed identity.

Live smoke on 2026-10-26 using `arazzo-cli` 0.8.2: one anonymous attempt for
`library/alpine`, `page_size=2`, selected `latest`, returned 16 image records and a
next-page URL, and succeeded. No retry used. No image was pulled. Offline fixtures
and this one live observation establish different evidence boundaries.
