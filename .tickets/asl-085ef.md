---
title: Add apple.testflight-build-inspection with exact iOS build selection
type: task
priority: 2
state: paused
created_at: 2026-10-29T15:40:33Z
last_changed: 2026-11-06T23:29:41Z
plan: investigation
files:
    ../arazzo-cli/crates/arazzo-cli/src/handlers.rs: r
    ../arazzo-cli/crates/arazzo-runtime/src/runtime_core/control.rs: r
    AGENTS.md: r
    docs/corpus/adding-specs.md: r
    fixtures/openapi/apple/app-store-connect.yaml: r
    fixtures/openapi/apple/testflight.yaml: c
    fixtures/responses/apple/README.md: m
    fixtures/responses/apple/testflight-build-inspection/apps.json: c
    fixtures/responses/apple/testflight-build-inspection/beta-detail.json: c
    fixtures/responses/apple/testflight-build-inspection/builds.json: c
    fixtures/responses/apple/testflight-build-inspection/groups.json: c
    fixtures/responses/apple/testflight-build-inspection/prerelease-versions.json: c
    fixtures/responses/apple/testflight-build-inspection/reviews.json: c
    manifest.yaml: m
    scripts/fixture_server.py: r
    scripts/verify.py: r
    specs/apple/README.md: m
    specs/apple/release-candidate-inspection.arazzo.yaml: r
    specs/apple/testflight-build-inspection.arazzo.yaml: c
    tests/README.md: r
    tests/scenarios/apple.release-candidate-inspection.yaml: r
    tests/scenarios/apple.testflight-build-inspection.yaml: c
    tests/test_apple_release_candidate_inspection.py: r
    tests/test_apple_testflight_build_inspection.py: c
    views/apple.release-candidate-inspection.summary.jq: r
    views/apple.testflight-build-inspection.summary.jq: c
assignee: codex
parent: asl-4af8c
---
# Add apple.testflight-build-inspection with exact iOS build selection

## Goal
Add `apple.testflight-build-inspection`: six sequential read-only GETs resolve an exact iOS app, marketing version and build number, then report provider beta states, visible review submission and a complete bounded associated-group page. Steve authorized this contained direction and separate later FaceDeck QA. The 2026-11-06 explicit body-redaction deferral replaces the old privacy prerequisite; preserve credential protection, selected-output correctness and no-fallback requirements. See current readiness below for the remaining expression feasibility check.

## Design
### Authority, evidence and explicit user decision

Source: Steve's 2026-10-29 instruction to author this ticket from `/tmp/testflight-workflow-assessment.md`, with no implementation, start or delegation in the authoring session. Baseline `main` is `b89ec44405bba8b21da0d54a3d0de8035a7434b2`. Open-backlog query `TestFlight|testflight|beta distribution` returned no overlap. Existing closed release-candidate work owns attached App Store builds, not this independent prerelease/build resolver; do not reopen its epic or change that workflow.

Explicit user decision, 2026-11-06: "I don't want to be doing redaction of bodies that gets too complicated. I think we should defer that for now." This explicitly replaces the agent-invented absolute provider-body privacy criterion and its tests; it is NOT a decided-by-recommendation weakening. General response-body redaction/sanitization is deferred here, with no additional ticket or sibling CLI prerequisite. The original authorization remains implementation through right-sized agents followed by separate parent FaceDeck read-only QA. This design pass does not implement, start, delegate, commit or push; ticket changes remain uncommitted until their implementation commit.

Retain the installed CLI's ordinary diagnostics, including response-body previews on errors. Raw success outputs, error previews and stdout/stderr are private operational data; do not publish or commit live payloads. There is no promise of general provider-body sanitization. The historical pause note below is superseded by this explicit decision, not evidence of an outstanding redaction gate. Actual Authorization credentials remain protected by the existing external-auth/redaction verification, safe argv handling and redirect policy. Arbitrary provider-body sentinels are not credentials and may appear in private error diagnostics.

Compatibility: installed `/Users/stevetrefethen/bin/arazzo-cli --version` reports `arazzo 0.8.2` on 2026-11-06. Use `arazzo-cli 0.8.2+`; no fixed-redaction release prerequisite. No wrapper, generic redactor, sanitizer, harness semantics or sibling CLI work is authorized.

### Provider source and six-GET contract

Public-contract refresh on 2026-11-06 fetched https://developer.apple.com/sample-code/app-store-connect/app-store-connect-openapi-specification.zip without authentication: version 4.6, archive SHA-256 `f41ed4489c78bf1488cd2291f23394565364fe37b402130f48c3e3c3f5ea1acd`, extracted `openapi.oas.json` SHA-256 `74732362a91236dcb66eb1620f8be18c2b6060771269b483eab578473bb32763`. The six operation IDs, selected sparse fields and filter encodings below were rechecked against that archive. This refresh supersedes the old 4.5.1 provenance for the new TestFlight subset only; do not modify the existing release subset. Durable provenance must include the URL/hashes and schema/operation anchors, not depend on `/tmp/asl-design-apple.zip`.

Use Arazzo 1.0.0, local source `apple`, qualified operation IDs, explicit JSON Pointers, fixed `https://api.appstoreconnect.apple.com`, and the existing sequential end-on-failure pattern. The OpenAPI `paths` anchors below define the exact operation/filter/sparse-field contract; filters are form arrays with `explode:false`, serialized as single scalar selections. Only the explicit includes in the live-QA correction below are used; no extra collection/relationship requests.

1. `resolve-app`: GET `/v1/apps`, `apps_getCollection`; `filter[bundleId]=bundle_id`, `limit=2`, `fields[apps]=name,bundleId`. Exactly one app, exact case-sensitive bundle ID.
2. `resolve-prerelease-version`: GET `/v1/preReleaseVersions`, `preReleaseVersions_getCollection`; `filter[app]=resolved app ID`, `filter[platform]=IOS`, `filter[version]=marketing_version`, `limit=2`, `fields[preReleaseVersions]=version,platform,app`. Exactly one `preReleaseVersions` resource with exact version, IOS and `relationships.app.data` matching the app.
3. `resolve-build`: GET `/v1/builds`, `builds_getCollection`; `filter[app]=app ID`, `filter[preReleaseVersion]=prerelease ID`, `filter[version]=build_number`, `limit=2`, `fields[builds]=version,processingState,expired,expirationDate,uploadedDate,buildAudienceType,usesNonExemptEncryption,app,preReleaseVersion`. Exactly one build with exact STRING build number and matching app/prerelease relationship types and IDs. Never use highest/latest build number, App Store version attachment, or another platform/marketing version.
4. `inspect-beta-detail`: GET `/v1/builds/{id}/buildBetaDetail`, `builds_buildBetaDetail_getToOneRelated`; path id is selected build ID, `fields[buildBetaDetails]=autoNotifyEnabled,internalBuildState,externalBuildState,build`. Require one `buildBetaDetails` object with its own ID and selected-build linkage; do not equate detail ID with build ID.
5. `inspect-beta-review`: GET `/v1/betaAppReviewSubmissions`, `betaAppReviewSubmissions_getCollection`; required `filter[build]=selected build ID`, `limit=2`, `fields[betaAppReviewSubmissions]=betaReviewState,submittedDate,build`. Accept zero or one resource; validate any build linkage. Empty means only “no visible submission returned.” Do not use the singular route or turn 404/null/errors into absence.
6. `inspect-beta-groups`: GET `/v1/betaGroups`, `betaGroups_getCollection`; `filter[app]=app ID`, `filter[builds]=build ID`, `limit=25`, `sort=name`, `fields[betaGroups]=name,isInternalGroup,hasAccessToAllBuilds,publicLinkEnabled,publicLinkLimitEnabled,publicLinkLimit,feedbackEnabled,app`. Accept 0..25 correctly typed resources with selected-app linkage and a complete page. Report exactly the returned order; no deduplication or extra sort/selection policy. Apple 4.6 has no GET `/v1/builds/{id}/betaGroups`. Do not request builds/testers relationships to infer audience.

Official route documentation: https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps ; https://developer.apple.com/documentation/appstoreconnectapi/get-v1-prereleaseversions ; https://developer.apple.com/documentation/appstoreconnectapi/get-v1-builds ; https://developer.apple.com/documentation/appstoreconnectapi/get-v1-builds-_id_-buildbetadetail ; https://developer.apple.com/documentation/appstoreconnectapi/get-v1-betaappreviewsubmissions ; https://developer.apple.com/documentation/appstoreconnectapi/get-v1-betagroups . Archive schemas `App`, `PrereleaseVersion`, `Build`, `BuildBetaDetail`, `BetaAppReviewSubmission`, `BetaGroup`, the six response schemas and `PagingInformation` are the defining field/type/relationship sources. Workflow-required identity/state fields are intentionally stronger than Apple's resource-level required `[id,type]`; distinguish that policy in docs.

### Input, response and output gates

Inputs: externally supplied complete `authorization` Bearer string (`format:password`, `writeOnly:true`), `bundle_id`, `marketing_version`, `build_number`, all required strings. No platform/limit inputs. `--strict-inputs` enforces types; regex gates reject empty/blank, leading/trailing whitespace and ANY comma, including `,value`, `value,`, and comma-only values. Apply all selector gates at the first capped app request before any downstream request; no trimming or numeric coercion. Required pattern reference: existing release workflow `resolve-app` uses `^[^,\s](?:[^,]*[^,\s])?$`.

Required identities: object containers, exact resource `type`, nonempty string IDs safe for one path/filter (`[A-Za-z0-9_-]+`), typed required relationship `data` objects with exact types/IDs; no truthiness or stringification substitutes. App requires bundleId; prerelease requires version and platform; build requires version and processingState; beta detail requires internalBuildState and externalBuildState; a present review requires betaReviewState; groups require nonempty name and boolean isInternalGroup. Missing/null/wrong-type required fields fail. Other requested attributes are optional: omission is retained as omission/unknown; present null or wrong type fails. Optional app name must be nonempty string. Booleans remain booleans. `publicLinkLimit`, when present, must be a JSON integer, not numeric text, boolean or fraction. Dates are nonempty strings with the provider's date-time schema retained; do not perform date arithmetic or claim calendar validation from a nonempty-string check.

Use pinned enum sets, not just nonempty strings: Build processing `PROCESSING,FAILED,INVALID,VALID`; BuildAudienceType `INTERNAL_ONLY,APP_STORE_ELIGIBLE`; BetaReviewState `WAITING_FOR_REVIEW,IN_REVIEW,REJECTED,APPROVED`; InternalBetaState `PROCESSING,PROCESSING_EXCEPTION,MISSING_EXPORT_COMPLIANCE,READY_FOR_BETA_TESTING,IN_BETA_TESTING,EXPIRED,IN_EXPORT_COMPLIANCE_REVIEW`; ExternalBetaState adds `READY_FOR_BETA_SUBMISSION,WAITING_FOR_BETA_REVIEW,IN_BETA_REVIEW,BETA_REJECTED,BETA_APPROVED,NOT_APPLICABLE` to that internal set. Unknown enum values fail visibly. VALID/APPROVED are not mandatory: failed, expired, rejected, processing and internal-only builds are valid inspection observations.

Every collection must have array `data`, required object `links` with nonempty string `self`, absent/null `links.next`, absent/null `meta.paging.nextCursor`, and no total exceeding or differing from returned row count. Absent meta is valid; present meta/paging must be correctly shaped, with integer limit 1..request cap and, if present, integer total exactly equal to row count; null/string/boolean/fractional metadata fails. Returned count must not exceed declared page limit or cap. Selectors require exactly one result; review permits 0/1; groups permit 0..25. No page traversal. Tiny limits can use explicit numeric equality enumeration; a range alone is insufficient (prior 1.5 regression). Preserve absent vs malformed; do not borrow the older workflow's permissive `!meta` shortcut.

Selected-output correctness owns the bounded key checks: validate only the six copied resource subtrees, with unknown fields rejected before success outputs are evaluated. Allowed resource keys are type,id,attributes,relationships and optional standard links; attributes are the selected sparse fields, relationships only those requested, linkage data only type/id, and standard links only self/related as appropriate. Retain fixed-origin API metadata URLs only, never fetch them. This finite shape validation preserves the selected raw objects and omissions; it is not a generic recursive sanitizer. Do not walk arbitrary envelopes/included resources or inspect arbitrary error-body fields for privacy. Envelope links/meta are checked only for page correctness and neither envelopes nor included resources are success outputs. Extra publicLink/publicLinkId/tester/contact/demo fields in copied resources fail selected-output shape checks, with no subsequent requests and no success outputs; their values may remain in private CLI diagnostics. Uncopied envelope extras need no privacy rejection. Sparse requests exclude invitation links, testers, contact and demo metadata but are not a provider-body confidentiality guarantee.

No mutations, token creation/refresh, retries, pagination, arbitrary returned URL fetches, private tester enumeration, public invitation links, contact/demo metadata, feedback/log reads, automatic notification, installation/effective-audience/readiness judgments. Group results describe only the complete returned filtered page visible to this token, not all access paths. All six reads are non-atomic observations; all-build groups and individual assignments are not fully audited.

### File Impact

Placement decided by recommendation under `file-structure`: new files in the existing Apple provider/corpus unit, no new package. A dedicated TestFlight subset isolates prerelease/beta ownership from existing App Store release inspection.

- Modify `manifest.yaml`: register this one workflow, subset, scenario suite, jq view, external env dependency, dry-run/default-offline verification and manual-authenticated-read-only policy; use verified installed CLI compatibility `arazzo-cli 0.8.2+`.
- Modify `specs/apple/README.md`: add TestFlight selection/privacy/absence semantics and correct numeric-looking STRING invocation; retain existing release behavior.
- Modify `fixtures/responses/apple/README.md`: add TestFlight synthetic provenance and official pin/anchors.
- Create `specs/apple/testflight-build-inspection.arazzo.yaml`: owns six-step selection, gates and outputs.
- Create `fixtures/openapi/apple/testflight.yaml`: owns only the six GET contracts and necessary local schemas.
- Create `fixtures/responses/apple/testflight-build-inspection/{apps,prerelease-versions,builds,beta-detail,reviews,groups}.json`: six small synthetic baseline responses; malformed cases inline in scenarios.
- Create `tests/scenarios/apple.testflight-build-inspection.yaml`: owns exact requests, whole-output assertions and suppression cases.
- Create `tests/test_apple_testflight_build_inspection.py`: owns real CLI external-auth, quoting, credential-redaction and redirect integration probes, following `AppleAuthorizationTests` without changing that existing test's ownership.
- Create `views/apple.testflight-build-inspection.summary.jq`: presentation only, fail on error envelope, explicit unknown/empty labels and inspection limitation.
- Must not grow: existing release workflow/subset/scenarios/view/auth tests; `scripts/verify.py`, `scripts/fixture_server.py` (no routing or evaluator changes); sibling CLI (separate authorization/ownership); unrelated `.vscode/`, `invalid/` and `.gitkeep` paths. No deletions.

### Inputs / Outputs

Public addition is the manifest entry and workflow `testflight-build-inspection`, with the four typed inputs above. Raw success outputs have exactly six keys: `selected_app`, `selected_prerelease_version`, `build`, `beta_detail`, `review_submissions`, `beta_groups`. First four are the validated allowlisted resource objects from `/data/0` (first three) or `/data` (detail); last two are validated `/data` arrays, including real empty arrays. Keep provider attributes and optional-field omissions intact. Step-only scalar IDs drive subsequent requests but do not expand the workflow's six-key output contract. Retain standard API resource/relationship links only under the stated allowlist; top-level document envelopes and included resources are excluded. Error envelopes must have no success outputs; ordinary private diagnostics may include arbitrary provider-body values. Actual Authorization credential protection remains required.

Document the operator command with literal environment reference, `--strict-inputs --max-redirects 0`, `--input bundle_id=com.example.corpus`, `--input-json 'marketing_version="1.0"'`, and `--input-json 'build_number="126"'`. `--input marketing_version=1.0` and integer-looking build values undergo CLI numeric coercion (`../arazzo-cli/crates/arazzo-cli/src/handlers.rs::parse_input_value`, `run.rs` input parsing); they are not safe string examples. `--input 'authorization=${APP_STORE_CONNECT_AUTHORIZATION}'` keeps the expanded JWT out of argv. Use `set -o pipefail` with `jq -er -f`; no live trace/verbose/export. Quickstart previews only `resolve-app` with synthetic authorization and sends no request.

### Approved numeric representation and readiness

Explicit user approval, 2026-11-06: integer validation uses the installed CLI parsed JSON numeric representation. Existing floating-point precision behavior is accepted; arbitrary-precision classification of original wire decimals is not required. Ordinary fractions such as 1.5, numeric strings, booleans and null remain rejected. The body-redaction deferral also remains in force. Feasibility evidence: /tmp/testflight-integer-evidence/README.md, criteria.yaml and results.json (598 ordinary probes passed); precision-results.json records the approved precision boundary.

The bounded expression feasibility check is resolved under this approved contract. Apply the proven JSONPath numeric-type checks and array regex criteria from /tmp/testflight-integer-evidence/criteria.yaml against finite selected group shapes. Reassess ordinary execution readiness, file preflight and reservations before guarded resume; no further design or CLI prerequisite remains. Prior pause/readiness notes are historical and superseded.

### Live-QA request correction

Decided by recommendation after live FaceDeck QA: sparse fields alone return relationship links without linkage data. Request documented include values app for prerelease/groups, app,preReleaseVersion for builds, and build for beta detail/reviews, with sparse included-resource fields name,bundleId for apps, version,platform for preReleaseVersions, and version for builds. Preserve six GETs, required identity linkage checks, output shapes, and no traversal of returned URLs. Included envelopes are not success outputs. This corrects request construction without weakening acceptance. Synthetic fixtures must cover included envelopes and omission of required linkage still fails.

## Acceptance Criteria
1. The registered workflow performs exactly the six GETs and sparse queries in Design, using response IDs and exact iOS marketing/build strings; reused build numbers across marketing versions/platforms cannot select the wrong identity.
2. Typed identities, linkages, enum/optional fields and complete-page bounds are enforced. Zero reviews/groups succeed as limited observations; malformed, ambiguous, truncated and HTTP-error responses fail immediately and suppress all later requests without retry/fallback.
3. Raw success outputs match the six-key selected-resource contract, preserve optional omissions and empty arrays, and exclude unselected resource fields. Copied-subtree shape failures stop downstream requests; all errors contain no success outputs. Actual Authorization credentials remain absent from argv/stdout/stderr and synthetic exports under the existing redaction verification. Ordinary CLI diagnostics are retained and may contain arbitrary provider-body values; document raw outputs/error previews as private with no general body-sanitization promise, per Steve's explicit deferral.
4. External-auth handling and redirects preserve the existing Apple security posture; fixed-origin read-only execution, safe numeric-string examples, synthetic provenance and presentation-only jq output are documented and verified. Neither raw output nor summary claims audience, installation, notification delivery or readiness.
5. Required offline verification and independent exact-candidate source review pass without changes to the harness, existing release workflow or sibling CLI. Live FaceDeck QA is separate parent work and not a condition of this implementation ticket's offline acceptance.
Integer requirements throughout this contract refer to the CLI parsed numeric representation per the explicit approval above.

## Testing Obligations
- Verify the installed CLI version and execute the existing credential-redaction checks; no runtime body-redaction prerequisite or forbidden-provider-body regression is required. Use synthetic loopback only for default verification.
- AC1: real CLI loopback scenarios assert every GET path, exact query including sparse fields, empty body, Accept and synthetic Authorization headers in order. Happy path uses marketing `"1.0"`, build `"126"` and different IDs for app/prerelease/build/detail. Add same-build-number fixtures under another marketing version and platform, ensuring wrong filter/linkage responses fail before detail/review/groups. Verify exact raw `.outputs` equality, not only subset assertions.
- AC2: cover zero/duplicate app/prerelease/build; wrong resource type; missing/null/number/blank/unsafe IDs; missing/null/object-vs-array containers; wrong relationship types/IDs; missing required state and unknown enums; omitted optional attributes, present null/wrong-typed optionals, boolean false, numeric-string/fractional publicLinkLimit; all valid processing/audience/review/beta enum values using bounded parameterization. Include expired, INTERNAL_ONLY, FAILED/INVALID and rejected/pending successful inspections. Empty reviews, empty groups and both empty are independent positives. Zero review does not skip the group GET.
- AC2 regressions: comma-only, leading comma, trailing comma and embedded comma for EACH input, plus blank/edge whitespace, numeric JSON version/build and quoted strings. At most the initial capped lookup may occur for lexical failures; strict input type failures make no requests. Every collection gets absent-meta positive, valid limit/total, continuation links/cursor negatives, total less/greater than count, fraction `1.5`, string/boolean/null limit/total, malformed meta/paging and over-cap data. Groups include exactly 25 complete rows and 26/continuation failures. Include non-array empty object and scalar data, not just null.
- AC2/3: 401,403,404,429 and representative 5xx at EACH step; exact request-prefix expectations prove no later requests/retries. Null/missing detail and null/missing review data fail, never “no submission.” Every negative asserts the specific CLI error code and absence of success outputs. Summary rejects a handcrafted error envelope.
- AC3: use synthetic provider values in unexpected copied-resource publicLink/publicLinkId, tester/contact/demo and unknown nested keys to verify shape rejection, exact request prefixes and no success outputs. Check whole-output equality and optional omissions independently; unselected envelope/included extras do not enter success outputs. Arbitrary provider values in private error previews/stdout/stderr are allowed: do not add them to `expect.forbidden_output` or require their redaction. Reserve forbidden-output sentinels for actual synthetic Authorization credentials and retain the existing credential checks, including synthetic exports. No real credentials or private live payloads in files/tickets.
- AC4: focused `tests/test_apple_testflight_build_inspection.py` follows `tests/test_apple_release_candidate_inspection.py::AppleAuthorizationTests`: literal whole-value env reference, full Bearer only in Authorization, no secret in argv/stdout/stderr or synthetic export; authentication/rate errors; first and downstream redirect tests with a second server proving zero target requests/credentials. Include a full six-GET run using the documented `--input-json 'marketing_version="1.0"' --input-json 'build_number="126"'` arguments, exact string filters/outputs, and unquoted numeric control failures. Temporary synthetic exports are test-only; production examples forbid them.
- AC1-5 commands: `arazzo-cli --json catalog specs/apple`; `arazzo-cli --json show testflight-build-inspection --dir specs/apple`; `arazzo-cli --json validate specs/apple/testflight-build-inspection.arazzo.yaml --strict`; documented first-step synthetic dry-run; `python3 scripts/verify.py apple.testflight-build-inspection`; `python3 -m unittest discover -s tests -p 'test_*.py'`; `python3 scripts/verify.py`; `git diff --check`. Harness anchors `scripts/verify.py::run_case` and `scripts/fixture_server.py::match_request/assert_consumed` already support exact queries/order, JSON-typed inputs, forbidden output and jq assertions. No harness change is justified by this six-GET shape. These are required implementation checks, not claims that authoring ran the future suite.
- Audit local subset operation/filter/sparse-field/relationship schemas against the pinned official archive; no extra methods, remote references, server overrides, includes or returned-URL targets. Keep required workflow constraints distinct from provider schema requirements. Use the proven optional-integer criteria and retain ordinary type/fraction regressions against the CLI parsed representation; do not add a numeric range, make the field mandatory, remove its typing test, substitute jq workflow semantics, or change the harness/CLI to hide a feasibility gap. General provider-body privacy is deferred and is not a readiness gate.
- Parent QA after implementation: independently reverify FaceDeck target identity and then read-only inspect it under the user's separate authorization. Previously observed app `6821549653`, bundle `com.stevetrefethen.facedeck`, version `1.0`, build `126` are hints, not current proof. Do not store its token or private payloads. Source publication after review and automated checks follows the latest AGENTS rule independently of pending manual QA unless a publication gate is explicitly designated; this authoring session does not push or authorize live execution itself.

## Note (2026-10-29 15:40 UTC) — Paused
gate: CLI 0.8.2 ordinary error JSON exposes unexpected private response fields; separately authorize and verify a CLI privacy fix, then reassess this Tier 2 draft without weakening acceptance — Steve clears scope authorization, parent verifies prerequisite

## Note (2026-11-06 22:11 UTC)
Explicit user decision supersedes the 2026-10-29 Paused note: general provider-body redaction is deferred, CLI diagnostics retained as private, and no CLI privacy fix is required. Credential protection and existing redaction verification remain. Current remaining readiness uncertainty is optional-integer expression feasibility, not body privacy. No implementation/start/commit/push/delegation performed; leave these ticket edits for the implementation commit.

## Note (2026-11-06 22:38 UTC)
Explicit user approval, 2026-11-06: integer validation uses the installed CLI parsed JSON numeric representation. Existing floating-point precision behavior is accepted; arbitrary-precision classification of original wire decimals is not required. Ordinary fractions such as 1.5, numeric strings, booleans and null remain rejected. The body-redaction deferral also remains in force. Feasibility evidence: /tmp/testflight-integer-evidence/README.md, criteria.yaml and results.json (598 ordinary probes passed); precision-results.json records the approved precision boundary.

## Note (2026-11-06 22:40 UTC) — Paused
gate: complete the six-step implementation and required verification — next implementation agent

## Note (2026-11-06 23:05 UTC)
Implementation delivered under the explicitly adopted current contract: preflight revision 08961f2da7fc2e3679b8de5c80deadacb81134af3857d820bf6abc4bb39c83fc, guarded start d9ffdc480fa7018a16d0eed85783e2a1be5611d5f0204d8b0bf0e2455e29f5e6. Retained snapshot/start packet, file preflight, source hashes, official Apple 4.6 subset audit and AC/testing map: /tmp/testflight-inspection-evidence. Six chained GETs, typed identities/linkages, bounded complete pages, sparse resource shape gates, raw six-key outputs, summary, docs and synthetic fixtures implemented. Offline checks PASS: 815 focused scenarios, 1358 full corpus scenarios, 67 Python tests including credential/export protection, quoted numeric strings, redirects and summary semantics; catalog/show/strict validation/first-step dry-run and diff checks pass. A final build_number description correction is recorded separately with parsed-document equivalence and strict validation; runtime fields unchanged. Existing release workflow, harness and sibling CLI unchanged. No live Apple calls, self-review, delegation, push or closure. Parent owns independent exact-candidate source review, publication and separately authorized FaceDeck live QA. Commit includes the two parent-authorized ticket design/lifecycle edits with implementation.

## Note (2026-11-06 23:05 UTC) — Paused
gate: independent exact-candidate source review of completed implementation — parent clears; publication and separate FaceDeck live QA remain parent-owned

## Note (2026-11-06 23:11 UTC)
Decided by recommendation after live FaceDeck QA: sparse fields alone return relationship links without linkage data. Request documented include values app for prerelease/groups, app,preReleaseVersion for builds, and build for beta detail/reviews, with sparse included-resource fields name,bundleId for apps, version,platform for preReleaseVersions, and version for builds. Preserve six GETs, required identity linkage checks, output shapes, and no traversal of returned URLs. Included envelopes are not success outputs. This corrects request construction without weakening acceptance. Synthetic fixtures must cover included envelopes and omission of required linkage still fails.

## Note (2026-11-06 23:13 UTC)
Live FaceDeck QA on 2026-11-06: explicit sparse includes corrected missing prerelease/build linkage. Selected build126 beta-detail GET returns internal IN_BETA_TESTING, external READY_FOR_BETA_SUBMISSION and autoNotifyEnabled=true, but relationships.build.data=null even with include=build; included=[] despite documented object schema. Current required backlink check correctly fails. No Apple settings changed. Any replacement of required backlink identity proof with selected-route/forward-link proof requires explicit contract approval; no fallback applied. Private raw results remain outside repository.

## Note (2026-11-06 23:13 UTC) — Paused
gate: live Apple beta-detail has null build backlink; approve alternative identity proof or provider correction — Steve clears contract decision

## Note (2026-11-06 23:29 UTC)
Include correction verification PASS: 816 focused scenarios, 1359 full-corpus scenarios, 67 Python tests, strict validation, Apple4.6 include-parameter audit and diff check. Artifacts /tmp/testflight-inspection-evidence/includes-{focused,full,unit}.log and includes-audit.json. No identity criteria weakened; required null beta-detail backlink remains a live FaceDeck QA gate. Fresh cumulative review pending.
