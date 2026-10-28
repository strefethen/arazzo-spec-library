# App Store Connect fixtures

All response bodies in `release-candidate-inspection/` are synthetic,
contract-shaped examples written for offline verification. They are not Apple
captures and do not establish live account visibility, authorization, or
provider behavior.

The local four-operation subset was checked against Apple's App Store Connect
OpenAPI archive, version 4.5.1, SHA-256
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
