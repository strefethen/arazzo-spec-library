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
