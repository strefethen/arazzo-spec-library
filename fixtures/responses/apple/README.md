# App Store Connect fixtures

All response bodies in `release-candidate-inspection/` are synthetic,
contract-shaped examples written for offline verification. They are not Apple
captures and do not establish live account visibility, authorization, or
provider behavior.

The local four-operation subset was checked against Apple's App Store Connect
OpenAPI archive, version 4.5.1. The archive SHA-256 is
`7b826ae9ca3e45b0e7df2643cbb811c9930632640944db11a8af4586fab9db46`; the
extracted `openapi.oas.json` SHA-256 is
`7518d3a94a8bd701ac25c1c601b95b8f53aad92091affb15a2a9d331713dac1a`:

- <https://developer.apple.com/sample-code/app-store-connect/app-store-connect-openapi-specification.zip>
- `paths./v1/apps.get` / `apps_getCollection`, `AppsResponse`, and `App`
- `paths./v1/apps/{id}/appStoreVersions.get` /
  `apps_appStoreVersions_getToManyRelated`, `AppStoreVersionsResponse`,
  `AppStoreVersion`, and `AppVersionState`
- `paths./v1/appStoreVersions/{id}/relationships/build.get` /
  `appStoreVersions_build_getToOneRelationship` and
  `AppStoreVersionBuildLinkageResponse`
- `paths./v1/builds/{id}.get` / `builds_getInstance` and `Build`

The happy-path files are deliberately small. Other responses are inline in the
registered scenario file so each failure is adjacent to the request it tests.
Malformed and null linkage responses are defensive failure cases; Apple 4.5.1
declares linkage `data` as a required object, and the malformed variants are
not claims about documented live response encoding.
# TestFlight synthetic fixtures (Apple 4.6)

All six bodies under `testflight-build-inspection/` are synthetic examples, not
live captures. IDs distinguish app, prerelease version, build and beta detail.
They prove workflow behavior, not current Apple account state.

Source: [official App Store Connect OpenAPI archive](https://developer.apple.com/sample-code/app-store-connect/app-store-connect-openapi-specification.zip),
version 4.6, refreshed 2026-11-06. Archive SHA-256:
`f41ed4489c78bf1488cd2291f23394565364fe37b402130f48c3e3c3f5ea1acd`.
Extracted `openapi.oas.json` SHA-256:
`74732362a91236dcb66eb1620f8be18c2b6060771269b483eab578473bb32763`.

The local `fixtures/openapi/apple/testflight.yaml` retains only GET operations
`apps_getCollection`, `preReleaseVersions_getCollection`, `builds_getCollection`,
`builds_buildBetaDetail_getToOneRelated`, `betaAppReviewSubmissions_getCollection`
and `betaGroups_getCollection`, their selected parameters and sparse schemas.
Defining resource anchors: `App`, `PrereleaseVersion`, `Build`, `BuildBetaDetail`,
`BetaAppReviewSubmission`, `BetaGroup`, their response schemas, `PagingInformation`,
`BuildAudienceType`, `InternalBetaState`, `ExternalBetaState`, `BetaReviewState`.
Filters retain form array encoding with `explode: false`. Required workflow
identity/state gates are intentionally stronger than provider-required `id,type`.
The groups route is `/v1/betaGroups` filtered by app and build, with `include=app`
and sparse app fields to request ownership linkage. There is no build-to-groups
GET route. Other relationship-bearing reads likewise use explicit sparse includes.
Existing release subset provenance is unchanged.
