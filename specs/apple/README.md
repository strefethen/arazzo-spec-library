# App Store Connect release candidate inspection

`release-candidate-inspection` resolves one exact, case-sensitive bundle ID,
selects one exact iOS marketing version under that app, follows that version's
build relationship, and reads only the attached build. It makes at most four
sequential `GET` requests to the fixed `https://api.appstoreconnect.apple.com`
origin. App and version lookups each request at most two records, reject
duplicates and every continuation marker, and never follow a page cursor.
Selection inputs are checked before downstream work: malformed values may cause
the first capped app lookup, but cannot trigger a version, linkage, or build
request.

This is a point-in-time inspection, not an atomic snapshot. Uniqueness is only
within the caller's token-visible filtered page. Build processing state,
expiration, encryption attributes, and version state are reported as returned;
they do not establish full submission readiness.

## Discover and inspect

Run commands from the repository root:

```sh
arazzo-cli --json catalog specs/apple
arazzo-cli --json show release-candidate-inspection --dir specs/apple
arazzo-cli --json validate specs/apple/release-candidate-inspection.arazzo.yaml --strict
```

The registered quickstart previews only `resolve-app` with synthetic inputs.
The dry run plans its first capped GET and sends no request. It cannot show
version, linkage, or build results.

## Authenticated operator run

The operator supplies a complete signed App Store Connect JWT Bearer value in
the environment. The workflow does not mint, store, refresh, or read signing
keys. The caller's Apple account must already be authorized for all four
requests; a 401 or 403 stops normally. No authenticated Apple call is part of
repository verification.

```sh
: "${APP_STORE_CONNECT_AUTHORIZATION:?set a complete Bearer JWT outside shell history}"
set -o pipefail
arazzo-cli --json run specs/apple/release-candidate-inspection.arazzo.yaml release-candidate-inspection \
  --strict-inputs --max-redirects 0 \
  --input 'authorization=${APP_STORE_CONNECT_AUTHORIZATION}' \
  --input bundle_id=com.example.corpus \
  --input marketing_version=1.2.3 \
  | jq -er -f views/apple.release-candidate-inspection.summary.jq
```

Keep any raw JSON output in a private, ignored location. Do not add `--trace`,
`--verbose`, export the run, or print the expanded credential. The literal
whole-value environment reference keeps the secret out of shell argv; the CLI
places it only in the `Authorization` header. The workflow disables redirects,
does not retry 429 responses, and never uses response-provided URLs. Do not
parallelize its dependent requests.

Synthetic fixtures and registered scenarios verify workflow wiring through
loopback only. They are not live Apple captures. The local OpenAPI subset and
its version, hash, and operation anchors are recorded in
`../../fixtures/responses/apple/README.md`.

## Sources

- [App Store Connect API overview](https://developer.apple.com/app-store-connect/api/)
- [List apps](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps)
- [List app store versions](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps-_id_-appstoreversions)
- [Get the build ID attached to a version](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-appstoreversions-_id_-relationships-build)
- [Read build information](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-builds-_id_)
- [Generate tokens for API requests](https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests)

These sources and the pinned 4.5.1 OpenAPI subset describe the contract used to
author the workflow. Offline fixtures prove CLI wiring and failure gates; live
authenticated Apple behavior remains unverified.
# TestFlight build inspection

`testflight-build-inspection` resolves an exact bundle ID, iOS marketing version,
and string build number through six sequential GETs: app, prerelease version,
build, beta detail, review submissions, and associated beta groups. Each selected
relationship must match the preceding identity. Reused build numbers on another
platform or marketing version cannot satisfy those checks.

Preview only the first lookup without credentials or network calls:

```bash
arazzo-cli --json run specs/apple/testflight-build-inspection.arazzo.yaml testflight-build-inspection --dry-run --strict-inputs --max-redirects 0 --step resolve-app --input authorization='Bearer SYNTHETIC-APPLE-PREVIEW' --input bundle_id=com.example.corpus --input-json 'marketing_version="1.0"' --input-json 'build_number="126"'
```

After explicit authorization for a live read, supply a complete Bearer JWT in
`APP_STORE_CONNECT_AUTHORIZATION` outside the command line:

```bash
set -o pipefail
arazzo-cli --json run specs/apple/testflight-build-inspection.arazzo.yaml testflight-build-inspection --strict-inputs --max-redirects 0 --input 'authorization=${APP_STORE_CONNECT_AUTHORIZATION}' --input bundle_id=com.example.corpus --input-json 'marketing_version="1.0"' --input-json 'build_number="126"' | jq -er -f views/apple.testflight-build-inspection.summary.jq
```

The JSON quotes preserve numeric-looking strings. Plain `--input` would coerce
`1.0` and `126` to numbers and strict validation rejects them. All three selectors
reject commas and edge whitespace. The first capped lookup may precede lexical
rejection. The token is expanded from the literal environment reference; never
put its expanded value in argv. Do not use live trace, verbose or export options.

Selection pages and the review collection are capped at two; groups are capped
at 25 and retain Apple's returned name order. Continuations, malformed metadata,
ambiguous selections and incomplete pages fail without retries or pagination.
Zero reviews means only no visible submission returned, and still requests
groups. Zero groups means no associated groups returned in this filtered page.
Absent optional attributes remain absent/unknown; false remains false. Failed,
invalid, expired, rejected, pending and internal-only states are observations.
Six reads are non-atomic and cannot establish installation, effective audience,
notification delivery or readiness. All-build groups and individual assignments
are not fully audited.

Raw outputs contain exactly the four selected resources and the review/group
arrays. Sparse requests and finite selected-resource shape checks exclude
unrequested fields. This is not general body sanitization: raw outputs, error
previews and stdout/stderr are private operational data. Ordinary CLI diagnostics
may retain arbitrary provider-body values. Never publish live payloads. Returned
API metadata URLs are retained only at the fixed Apple origin and never fetched.
No testers, invitation URLs, contact/demo data, feedback or logs are requested.

The local subset is pinned to Apple OpenAPI 4.6; provenance and schema anchors
are in [fixture provenance](../../fixtures/responses/apple/README.md). Provider
schemas require fewer fields than this workflow's identity/state policy.
Date strings are checked as nonempty, without calendar validation. Optional
integer validation uses the CLI's parsed numeric representation, accepting its
floating-point precision behavior; ordinary fractions, strings, booleans and null
fail. Default verification uses only synthetic loopback responses:

```bash
python3 scripts/verify.py apple.testflight-build-inspection
python3 -m unittest discover -s tests -p 'test_apple_testflight_build_inspection.py'
```
