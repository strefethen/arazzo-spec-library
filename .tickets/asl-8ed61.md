---
title: Implement authenticated vSphere VM and guest diagnosis
type: task
priority: 1
state: open
created_at: 2026-10-27T18:30:28Z
last_changed: 2026-10-27T18:30:34Z
plan: plans/current/vsphere-workflows.md
files:
    README.md: m
    docs/index.md: m
    fixtures/openapi/vsphere/session.yaml: r
    fixtures/openapi/vsphere/vm-guest-diagnosis.yaml: c
    fixtures/responses/vsphere/README.md: c
    fixtures/responses/vsphere/vm-guest-diagnosis/*.json: c
    manifest.yaml: m
    plans/assessments/vsphere-contracts-2026-10-27.md: r
    plans/current/vsphere-workflows.md: r
    scripts/configure_vsphere.py: r
    specs/vsphere/README.md: m
    specs/vsphere/vm-guest-diagnosis.arazzo.yaml: c
    tests/scenarios/vsphere.vm-guest-diagnosis.yaml: c
    tests/test_vsphere_auth.py: c
    views/vsphere.vm-guest-diagnosis.summary.jq: c
deps:
    - asl-b4622
---
# Implement authenticated vSphere VM and guest diagnosis

## Goal
Deliver the in-depth VM configuration/guest diagnosis authorized in the 2026-10-27 conversation: correlate scoped identity, configured hardware and reported guest telemetry, with integrated session lifecycle and a real CLI pickup path.

## Design
Follow accepted plans/current/vsphere-workflows.md and version8.0.3 official source URLs in plans/assessments/vsphere-contracts-2026-10-27.md. Create a fixed chain: login POST /api/session -> uniquely resolve named datacenter using GET /api/vcenter/datacenter?names -> uniquely resolve VM using names and returned datacenter ID -> VM config -> Tools -> guest identity -> guest networking -> guest interfaces -> guest routes -> guest local-filesystem -> success logout. On each authenticated work failure goto separate failure logout then end nonzero; login explicit onFailure:end; normal logout explicitly ends success to avoid fallthrough. Failure logout204 plus false criterion deliberately retains failure; document lost original top-level error/cancellation cleanup limits. No partial-success paths, retries, or live execution.
Use CLI-proven exact-one JSONPath criterion '$[?length($) == 1 && count($[0]) == 1]' plus /0 identity guard; empty/ambiguous/object-shaped results fail before downstream queries. Tools503 is explicit error. Preserve optional unknown values without fabricating empty telemetry. Read raw configuration maps keyed by device IDs, guest_OS and memory.size_MiB, ordered interfaces, routes interface_index and filesystem map with mappings.disk. Require useful identities/schema shape and gate numeric bounds before collection if any; hard provider result caps are not pagination.
Outputs include datacenter and selected VM identities, full config and Tools, full guest identity/network/interface/route/filesystem structures. jq view presents configured-vs-reported state and links mapped NICs/disks/routes where reported, without guessing missing mappings or calling configured allocation utilization. No credentials as final outputs.
All authenticated requests include vmware-api-session-id only; Basic only login. Safe .invalid companions; use shared session.yaml and configure_vsphere helper. Include forbidden_output sentinel assertions, absent_headers Basic checks, success204 and failed cleanup. Add tests/test_vsphere_auth.py for real CLI approved env-based pickup behavior, redirect refused and target never contacted (two loopback servers; don't relax scenario redirect preflight), unexpected login status token never printed/nonzero/no inventory, and no sentinel in approved export-run/stdout/stderr surfaces. No traces in normal commands, no live --step, redirects0 mandatory.
Provider README documents setup, copy/paste env guard and single-quoted credential input, unique-name semantics, privileges/TLS limitations, raw JSON vs jq, cleanup limitations, full vs preview commands and prominence of 'vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.' Same notice in spec description/manifest/fixture provenance. Register one entry tier dry-run and tests; README/docs counts reflect actual additions. Explicit paths below own provider responsibilities; no sibling changes.
### File Impact
- Modify: manifest.yaml (entry), specs/vsphere/README.md (VM guide), README.md and docs/index.md (accurate inventory and notice).
- Create: specs/vsphere/vm-guest-diagnosis.arazzo.yaml, fixtures/openapi/vsphere/vm-guest-diagnosis.yaml, fixtures/responses/vsphere/vm-guest-diagnosis/*.json, fixtures/responses/vsphere/README.md, tests/scenarios/vsphere.vm-guest-diagnosis.yaml, views/vsphere.vm-guest-diagnosis.summary.jq, tests/test_vsphere_auth.py. New files within existing corpus/scripts testing boundaries own this diagnosis contract, synthetic evidence, presentation and authentication regression proof respectively.
- Must not grow: scripts/verify.py must not gain provider business rules; shared session.yaml must not grow unrelated operations; sibling CLI must not change.

## Acceptance Criteria
- A complete real-CLI offline run authenticates, resolves scoped unique identities, retrieves all documented configuration/guest resources and logs out, producing a correlated in-depth report and raw structures.
- Empty/ambiguous/malformed identity results, authentication/authorization/resource errors, Tools no-data503 and logout failures fail closed with exact request ordering and no subsequent work requests.
- Supported invocation refuses redirects and prevents synthetic credential disclosure in stdout/stderr/export; Basic is never sent downstream; cleanup and trace/TLS limitations are accurately documented.
- Manifest, provider guide, workflow description, fixture provenance and discovery clearly expose documentation-based/offline-tested/live-unverified status and executable configure/full-run/preview commands.

## Testing Obligations
- Run python3 scripts/verify.py vsphere.vm-guest-diagnosis with cases for complete mapped telemetry, optional omissions/empty valid collections, zero/duplicate/malformed selection, auth401, unexpected login status with scalar token, work403/404/503, provider collection-limit failure, normal/failure logout and cleanup failure; assert IDs, headers, outputs and jq content.
- Run python3 -m unittest discover -s tests -p 'test_*.py', including real CLI redirect target-not-contacted, env credential expansion and sentinel redaction/export probes.
- Run python3 scripts/verify.py for whole corpus, plus configure helper from repo root with synthetic HTTPS origin then CLI strict validation and first-login dry-run of configured spec; no live calls.
- Run git diff --check; independently check official pinned schemas and README commands. Fresh independent ticket-code-review must pass exact final candidate before push/closure.
