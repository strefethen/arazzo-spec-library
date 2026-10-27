---
title: Implement authenticated vSphere OVF deployment preparation
type: task
priority: 1
state: open
created_at: 2026-10-27T18:30:28Z
last_changed: 2026-10-27T19:18:57Z
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
