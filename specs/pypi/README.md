# PyPI Release Metadata

`package-release` makes two anonymous GET requests: resolve the project's current
version from `info.version`, then fetch metadata for that exact returned name and
version. It reports release files, SHA-256 values, per-file yanking, and known
version-specific vulnerability records. No packages are downloaded or executed.

Run from the repository root with installed `arazzo-cli` 0.8.2+ and jq:

```bash
set -o pipefail
arazzo-cli --json run specs/pypi/package-release.arazzo.yaml package-release \
  --strict-inputs --input-json 'package="sampleproject"' \
  --http-timeout 10s --execution-timeout 30s --max-response-size 2097152 \
| jq -er -f views/pypi.package-release.summary.jq
```

No-network discovery, validation, and first-step request preview:

```bash
set -o pipefail
arazzo-cli --json catalog specs/pypi
arazzo-cli --json validate specs/pypi/package-release.arazzo.yaml --strict
arazzo-cli --json run specs/pypi/package-release.arazzo.yaml package-release \
  --dry-run --strict-inputs --step resolve-project \
  --input-json 'package="sampleproject"' \
| jq -er -f views/pypi.package-release.summary.jq
```

## Contract And Limits

- Official source checked 2026-10-26: [PyPI JSON API](https://docs.pypi.org/api/json/).
  Project metadata supplies the reported current version, not a locally computed
  highest compatible version. The second endpoint binds files and vulnerability
  data to that version; the deprecated historical `releases` map is not consumed.
- The default User-Agent is
  `arazzo-spec-library (https://github.com/strefethen/arazzo-spec-library)`.
  No authentication, artifact download, hash verification, or installation occurs.
- These JSON endpoints do not offer pagination. Work is bounded to two requests
  and one version; raw outputs retain its complete file/advisory arrays. The jq
  view shows at most 20 files and 20 advisories, with full counts. The command
  caps each HTTP response at 2 MiB; large project metadata fails explicitly,
  without silently truncating or substituting another endpoint.
- Empty file/advisory arrays are valid and shown explicitly. A missing version,
  different release identity, 404, or 429 fails; no automatic retry is configured.
  Do not poll aggressively. The JSON API documentation does not promise a fixed
  anonymous request allowance; honor any provider throttling and `Retry-After`.
- This local OpenAPI is a hand-maintained subset. Criteria check status and
  required data, not the entire response schema; jq independently guards array
  types and errors nonzero for failures or malformed collections.
- No reported vulnerability does not mean safe. Hashes are upstream metadata,
  not an authenticity verdict, and yanked flags are reported without overriding
  them. Advisories may be incomplete or withdrawn.

## Evidence

All JSON under `fixtures/responses/pypi/` and inline scenario bodies are synthetic,
including deliberately invented hashes and advisory IDs. They are not live
captures or real vulnerability claims. `tests/scenarios/pypi.package-release.yaml`
checks name/version request dataflow, files/hashes/yanking/advisories, empty
arrays, absent version/hash, 404, 429, and mismatched release identity.

Live smoke on 2026-10-26 using `arazzo-cli` 0.8.2: one attempt for `sampleproject`
resolved `4.0.0`, returned 2 files and 0 vulnerability records, and succeeded.
No retry used. Live data is separate from deterministic offline scenario proof.
