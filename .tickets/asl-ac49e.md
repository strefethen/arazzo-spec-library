---
title: Implement authenticated vSphere OVF deployment preparation
type: task
priority: 1
state: paused
created_at: 2026-10-27T18:30:28Z
last_changed: 2026-10-27T19:58:55Z
plan: plans/current/vsphere-workflows.md
files:
    README.md: m
    docs/index.md: m
    fixtures/openapi/vsphere/ovf-deployment-preparation.yaml: c
    fixtures/openapi/vsphere/session.yaml: r
    fixtures/responses/vsphere/README.md: m
    fixtures/responses/vsphere/ovf-deployment-preparation/*.json: c
    manifest.yaml: m
    plans/assessments/vsphere-contracts-2026-10-27.md: r
    plans/current/vsphere-workflows.md: r
    scripts/configure_vsphere.py: r
    specs/vsphere/README.md: m
    specs/vsphere/ovf-deployment-preparation.arazzo.yaml: c
    tests/scenarios/vsphere.ovf-deployment-preparation.yaml: c
    views/vsphere.ovf-deployment-preparation.summary.jq: c
assignee: codex
deps:
    - asl-8ed61
    - asl-785d1
    - asl-d3ccf
---
# Implement authenticated vSphere OVF deployment preparation

## Goal
Deliver a multi-resource OVF deployment-preparation report with session authentication, official-source provenance and explicit unresolved placement/compatibility checks; never deploy or accept EULAs.

## Design
Follow plans/current/vsphere-workflows.md and official8.0.3 sources in assessment. Fixed chain: login -> resolve named datacenter uniquely -> resolve named cluster within returned datacenter uniquely -> cluster detail -> returned root resource-pool detail -> explicit content library item get -> expected library/type ovf guard -> inspect explicit target folder/datastore/network identities using documented datacenter-scoped list filters -> POST OVF library-item/{id}?action=filter with exact {"target":{"resource_pool_id":returned_pool,"folder_id":selected_folder}} -> success logout. The item input ID is retained because get omits id. Verify expected library_id/type and expose cache/version/size metadata; names needn't be unique. Target folder must be VIRTUAL_MACHINE folder in selected datacenter; datastore/network query include explicit supplied ID plus returned datacenter. No unverified EnvironmentBrowser request or implication that datacenter membership proves cluster accessibility.
Inspect OVF requirement networks/storage_groups/additional_params/EULAs and expose selected target network/datastore as candidates. Report required mapping names and unresolved operator work; do not promise complete compatibility, accept EULAs, synthesize deployment readiness or execute deploy. Can output supplied proposed mappings only if contract can verify them with fixed-length CLI0.8.2 expressions; otherwise expose explicit candidate and requirements honestly rather than invent dynamic mapping validation.
Reuse tested shared authentication failure/logout patterns from VM slice, exact-one/type/identity guards, per-step credentials and redirects0. Full raw output plus jq human report includes template provenance, cluster/pool allocations, folder, storage capacity, network identity, OVF requirements and explicit remaining placement/mapping/privilege checks. Require substantial multi-resource report. All outputs/description/header capitalization match pinned docs EULAs etc.
Provider guide includes complete runnable configure + env-based auth command with exact required IDs/names, discovery guidance (documented CLI full workflows; no live --step leaking session), privilege/TLS/cleanup limits, prominent contract-based/synthetic/live-unverified label. Register tier dry-run; fixture provenance and counts updated truthfully. No schema/runtime changes outside repository.
### File Impact
- Modify: manifest.yaml, specs/vsphere/README.md, README.md, docs/index.md, fixtures/responses/vsphere/README.md for registered workflow and accurate evidence.
- Create: specs/vsphere/ovf-deployment-preparation.arazzo.yaml, fixtures/openapi/vsphere/ovf-deployment-preparation.yaml, fixtures/responses/vsphere/ovf-deployment-preparation/*.json, tests/scenarios/vsphere.ovf-deployment-preparation.yaml, views/vsphere.ovf-deployment-preparation.summary.jq. Files within existing corpus boundaries own OVF contracts, synthetic tests and presentation.
- Must not grow: shared session.yaml no unrelated operations; scripts/verify.py no provider-specific logic; sibling CLI unchanged.

## Acceptance Criteria
- Complete real-CLI offline flow combines scoped cluster/resource-pool, library OVF metadata, folder/storage/network candidates and OVF filter requirements with auth/logout into an actionable report.
- Wrong library/type, empty/ambiguous/malformed resource identity, missing target, denied permission and inaccessible OVF errors stop subsequent work, attempt logout and exit nonzero; no deploy/license acceptance/retries exist.
- All invocation/discovery/docs preserve credential handling and redirect protections, expose exact selected identities and unresolved compatibility/mapping checks, and clearly label synthetic evidence and real-vCenter execution unverified.

## Testing Obligations
- Run python3 scripts/verify.py vsphere.ovf-deployment-preparation covering full metadata+requirements, optional omissions, empty requirement collections, wrong type/library, zero/duplicate/malformed target results, wrong-folder type, errors including OVF400/404/500 and logout failure; exact POST target wrapping/query/header assertions and useful jq output.
- Run python3 -m unittest discover -s tests -p 'test_*.py' and python3 scripts/verify.py (whole corpus), configure helper + strict validation/dry-run of configured spec. No live calls.
- Check official versioned content item/filter/folder/datastore/network contracts against companion; git diff --check and fresh independent exact-candidate ticket-code-review before push/closure.

## Note (2026-10-27 19:46 UTC)
Implementation complete for parent-owned exact-candidate review; keep in_progress per explicit handoff instruction. No push or closure performed.
AC1 PASS: fixed login -> unique scoped DC/cluster -> cluster/root pool -> explicit verified OVF item -> explicit DC-scoped folder/datastore/network candidates -> exact OVF filter target wrapper -> logout. Full raw provenance/settings/requirements plus jq report; mapping and placement checks remain explicit.
AC2 PASS: 120 real-CLI synthetic cases cover full/minimal/empty data, library/type/identity failures, actual string-container impostors, permissions at every work step, OVF400/404/500 and login/logout failures. Every request sequence asserts Basic only on login and session headers thereafter; OVF POST asserts Content-Type/query/body exactly. Failure cleanup remains nonzero; no deploy/license acceptance/retries.
AC3 PASS: secure complete pickup guide preserves private getpass/env setup, redirect refusal, strict inputs, raw/jq and preview. All 15 shell blocks parse; documented OVF helper/discovery/show/strict validation/login preview/full CLI/raw/jq blocks verified with synthetic loopback credentials. All source/spec/manifest/provenance notices say contract-based/synthetic/live-unverified.
Verification PASS: python3 scripts/verify.py vsphere.ovf-deployment-preparation (120); python3 -m unittest discover -s tests -p test_*.py (58); python3 scripts/verify.py (360); configured strict validation and first-login dry-run; official pinned8.0.3 operation/enum/optional-field checks; git diff --check. Corpus totals 12 workflows, 9 providers, 360 scenarios, 58 unit tests. No live vCenter/provider calls.
Evidence: .artifacts/vsphere-execution/asl-ac49e/ contains immutable show-before.json (revision 457e73940ad27a793c40bc8d6ad18a6d381dfb9fe2ee588ecd60fce56f019a65), start.json (revision 7afc1cb4c219b6f5e8161b64d355adbfaf08d30187d968390d175e8086182b41), files-before.json, Git baseline, retained official pages/hash ledger, logs, guide probes and tested-content-sha256.json. Base [7e92ea4](https://github.com/strefethen/arazzo-spec-library/commit/7e92ea4f94ccca0ff2fb10ca8356a59998a49592). Requirements unchanged; no forecast expansion; shared session/helper/harness/sibling untouched; preexisting unrelated untracked inventory preserved. Parent must perform fresh independent ticket-code-review against the final base/head and contract before push/closure; live-vCenter compatibility remains unverified.

## Note (2026-10-27 19:58 UTC)
Parent-authorized narrow remediation: P1 complete; P2 remains an explicit blocker, not an accepted malformed response. No push or closure.
P1 root cause: RFC9535 match(..., ".*") matches the entire string and rejects embedded line breaks. Replaced the OVF spec's string-type-only checks with search(..., ""), which CLI0.8.2 proves accepts multiline/empty/control-character strings while rejecting nonstrings. All such type-only checks in this spec use the same predicate; nonempty identity checks remain unchanged. Optional annotation already passed through; multiline and empty annotation now have complete raw/jq regression proof.
Five new bounded full-chain scenarios cover multiline description/EULA/annotation (plus existing string-only version/mapping fields), genuine empty strings, controls, description object rejection, and nonstring first EULA entry. Existing later nonstring and failure cleanup cases remain. Failures assert nonzero/logout/no subsequent work; successes assert exact raw data and jq output.
Verification PASS: focused 125 scenarios; full unit suite 58 tests; whole corpus 365 scenarios; configured strict validation and first-login dry-run; all 15 provider guide shell blocks plus exact documented synthetic full CLI/raw/jq commands; git diff --check. README count updated to 365. Passing corpus fixtures do not resolve the additional P2 negative probes.
P2 reproduced with stringified objects, scalar/null/boolean/array elements at first and later positions; all succeed in the unchanged original guard. A standard nonempty-object predicate rejects the scalar/nonempty-array cases but incorrectly permits [] elements, so it was not shipped. Open-extension success probe preserves {} and arbitrary unknown nested properties.
One additional parent-authorized sentinel avenue was probed, then stopped: defaulted internal object input with enum:[{}] is accepted; default injection and strict enum/type rejection of [], nonempty objects, strings and null work. Its named output is readable during logout. However aggregate $steps.filter-ovf.outputs context fails strict validation with "invalid Runtime Expression at bytes 17..25: invalid identifier". Literal {} output fails parsing with "missing field `context`". No sentinel, changed input, partial guard, arbitrary required type field, CLI/harness change or fallback is included in source.
Contract unchanged: retained Goal/Design/AC/Testing/files/dependencies/plan and original start closeout baseline remain authoritative. Inputs, public outputs, request chain, per-step auth, routing, cleanup, schema and deployment/EULA limits unchanged. All original snapshots remain immutable; only new remediation evidence under .artifacts/vsphere-execution/asl-ac49e/remediation/. Retained pinned8.0.3 official HTML hashes verified; live refresh through web failed, so do not claim a fresh provider lookup. No live provider calls.
Base [7e92ea4](https://github.com/strefethen/arazzo-spec-library/commit/7e92ea4f94ccca0ff2fb10ca8356a59998a49592); original candidate [dbec5bc](https://github.com/strefethen/arazzo-spec-library/commit/dbec5bc1ec8b9cbe4c7216f2250d3744c11f8d0a) (local; not pushed). New candidate identity and committed/tested-byte parity recorded in remediation/handoff.json after the explicit-path fix commit. Parent must review cumulative full base..newHEAD with both prior findings; no PASS is claimed for AC2/P2 or overall closure readiness.
Gate: approved CLI/spec-supported access to an aggregate validation context (or equivalent exact object-type validation) that distinguishes {} from [] without weakening open schemas, requiring extension fields, or adding work API requests. Parent will obtain Steve's decision on a concrete alternative. Requirements and tests are not weakened.

## Note (2026-10-27 19:58 UTC) — Paused
gate: approved supported validation context or exact object-type mechanism for every additional_params element, preserving {} and rejecting [] without schema weakening or additional work APIs; aggregate step outputs context is rejected by CLI0.8.2 — Steve clears via parent after a concrete alternative is proposed
