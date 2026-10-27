---
title: Reject stringified containers in vSphere VM telemetry
type: bug
priority: 1
resolution: completed
close_reason: '[fce4c00](https://github.com/strefethen/arazzo-spec-library/commit/fce4c00026993b9783f5892c4df1aa2a5c13685e) enforce actual VM telemetry containers with failure cleanup'
created_at: 2026-10-27T19:18:45Z
last_changed: 2026-10-27T19:35:38Z
plan: investigation
files:
    README.md: m
    fixtures/responses/vsphere/README.md: m
    specs/vsphere/README.md: m
    specs/vsphere/cluster-infrastructure-assessment.arazzo.yaml: r
    specs/vsphere/vm-guest-diagnosis.arazzo.yaml: m
    tests/scenarios/vsphere.vm-guest-diagnosis.yaml: m
changes:
    - at: 2026-10-27T19:35:38.52981Z
      action: close
      from: in_progress
      to: closed
      resolution: completed
      reason: '[fce4c00](https://github.com/strefethen/arazzo-spec-library/commit/fce4c00026993b9783f5892c4df1aa2a5c13685e) enforce actual VM telemetry containers with failure cleanup'
assignee: codex
deps:
    - asl-785d1
---
# Reject stringified containers in vSphere VM telemetry

## Goal
Correct the same decoded-string container guard defect found during cluster review in the already published VM diagnosis. A2026-10-27 synthetic probe confirmed interfaces response JSON string '[]' returns CLI success with guest_interfaces string. Preserve the existing diagnosis outcome and strengthen its promised malformed-data boundary.

## Design
Investigation-backed repair within the existing VM workflow. Existing specs/vsphere/vm-guest-diagnosis.arazzo.yaml uses regex contexts to guard object/array shape; CLI0.8.2 regex treats JSON strings as decoded text, so strings like '[]'/'{}' can impersonate containers. Review cluster ticket asl-785d1 remediation for a proven actual-container guard pattern and reuse only supported Arazzo/CLI criteria. Reject stringified and wrong-container values for configuration nics/disks maps, guest identity full_name object, guest networking object, interfaces/routes arrays and filesystems map where the existing guard intends a container. Keep valid empty collections/optional omissions and all raw mappings unchanged. Do not introduce full response schema validation, fallback data, retries, or alter infrastructure.
Add bounded exact-request scenarios that demonstrate malformed work stops at the affected endpoint then performs failure logout and exits nonzero, with no later work requests. Assert valid empty actual containers continue and jq still works. Update truthful scenario counts/provenance if needed. Do not widen fixture routing or change sibling CLI. Existing shared auth/secret/redirect/TLS/pickup contract remains unchanged.
Grounding: confirmed on HEAD91db004 with scripts/verify.py::run_case against a copied first VM happy case, replacing interfaces response with JSON string[] and asserting successful guest_interfaces[] string; no source edits or live requests. Cluster independent review independently reproduced analogous host/VM/pool string-array acceptance. This is a repair of a required boundary, not new desired scope.
### File Impact
- Modify: specs/vsphere/vm-guest-diagnosis.arazzo.yaml (actual container guards), tests/scenarios/vsphere.vm-guest-diagnosis.yaml (regressions), README.md (accurate aggregate counts), fixtures/responses/vsphere/README.md and specs/vsphere/README.md only if evidence/guard wording needs correction.
- Must not grow: scripts/verify.py/fixture_server.py no provider-specific logic or weakened routing; sibling CLI unchanged.

## Acceptance Criteria
- All intended VM container guards reject stringified/wrong JSON containers, attempt failure logout, exit nonzero and prevent later work requests.
- Genuine empty/populated containers, optional MAC/mapping omissions, raw absence and existing correlations remain valid; credential handling and official API contracts are unchanged.

## Testing Obligations
- Run python3 scripts/verify.py vsphere.vm-guest-diagnosis with bounded new cases for affected arrays/maps/object contexts and genuine empty controls; verify CLI error, exact cleanup sequence and jq outputs.
- Run python3 -m unittest discover -s tests -p 'test_*.py' and python3 scripts/verify.py whole corpus; configured strict validation/login dryrun, diff checks and independent exact-candidate ticket-code-review. No live calls.

### Evidence
AC1 PASS: all ten intended VM container guards require actual object/array typed access;22 added malformed-response scenarios exit nonzero, attempt failure logout and prevent later work. AC2 PASS: genuine empty/populated containers, optional MAC/mapping absence and arbitrary map-key collisions preserved;44 original cases unchanged, auth/outputs/contracts unchanged.
Testing PASS:68 VM scenarios,240 whole-corpus scenarios,58 unit tests, configured strict validation/login dryrun, cumulative diff and committed-byte parity. Independent reviewer reran68 VM plus configured/diff/parity checks and inspected240corpus/58unit evidence. Zero live calls.
Fresh independent T3 vsphere-vm-guards-review-1 gpt-6-astra/high PASS f199e7dd0dbeb272e438de8580f3ca05a982247a..fce4c00026993b9783f5892c4df1aa2a5c13685e. No findings.
Retained baseline8728fc03730fbae3566ce437c0c16c80c073161b115344043f01c2da23c46dbf/start1a8e14a461be43aede8f8e0fc03e69c91376ea74debabd73ef63952543cdbea1, file/Git preflight, evidence.md/logs/hash parity under.artifacts/vsphere-execution/asl-d3ccf/. Requirements/files/dependencies unchanged before evidence-only append. Live vCenter behavior remains unverified.

## Note (2026-10-27 19:35 UTC)
[fce4c00](https://github.com/strefethen/arazzo-spec-library/commit/fce4c00026993b9783f5892c4df1aa2a5c13685e) pushed after independent PASS; published VM container guard defect repaired.

## Note (2026-10-27 19:35 UTC) — Closed
[fce4c00](https://github.com/strefethen/arazzo-spec-library/commit/fce4c00026993b9783f5892c4df1aa2a5c13685e) enforce actual VM telemetry containers with failure cleanup
