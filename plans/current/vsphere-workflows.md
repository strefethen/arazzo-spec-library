---
status: accepted
epic: asl-41557
created: 2026-10-27
---

# Documented vSphere diagnostic workflows

**Seed:** The 2026-10-27 conversation in T3 thread
`ff1e4085-be33-4d10-8ba1-c9f42cdddaae`: Steve requested substantial workflows
that combine several APIs, include authentication, and are easy to run through
`arazzo-cli`. He then authorized right-sized subagents, implementation and push,
with clear wording that real-vSphere validation remains outstanding.

## Outcome and non-goals

Deliver three useful vSphere 8.0 U3 workflow reports: VM/guest diagnosis,
cluster infrastructure assessment, and OVF deployment preparation. Include
session creation, credential propagation and documented cleanup semantics.
Every report exposes its selected identities, source data and limits.

The work belongs entirely to the spec library. It does not modify the sibling
CLI, deploy VMs, alter infrastructure, accept licenses, provision test systems,
or claim real-vCenter validation. Credentials and generated endpoint-specific
copies never belong in Git. Do not add partial-success or substitute-inventory
paths to bypass missing data or unsupported contracts.

## User-visible workflows

### VM and guest diagnosis

Authenticate, resolve one VM within a supplied datacenter, retrieve configured
hardware and Tools status, then gather guest identity, networking, interfaces,
routes and filesystems. Connect reported telemetry to configured NIC and disk
identities where the API provides mappings. Distinguish configured resources
from observed guest state and optional unknown fields from empty collections.
No match, ambiguous selection or unavailable telemetry is an explicit failure.

### Cluster infrastructure assessment

Authenticate, resolve one cluster within a supplied datacenter, follow its root
resource-pool identity, inspect host and VM inventory, negotiate the release
contract and retrieve cluster configuration targets. Report HA/DRS, allocations,
host states, configured workload totals and supporting storage/network
candidates. Do not imply utilization, full VM-to-host topology, universal host
accessibility or placement readiness from inventory alone.

### OVF deployment preparation

Authenticate, inspect an explicitly identified content-library OVF item and
verify its library/type, resolve the target cluster and resource pool, inspect
explicit target resource identities and query OVF deployment requirements.
Expose required networks/storage groups, additional parameters, EULAs and
proposed mappings for operator review. Do not invoke deployment or describe
the report as proof that deployment will succeed.

## Decision-relevant facts

[The dated contract assessment](../assessments/vsphere-contracts-2026-10-27.md)
records versioned official API and SDK sources, exact response shapes and
remaining research gates. Automation `/api` responses must not be confused
with historical `/rest` wrappers. Name resolution uses explicit scope and
exactly one visible match. Provider collection caps are hard limits rather
than pagination controls.

The existing manifest and fixture harness own discovery and offline execution.
`scripts/verify.py::check_entry` requires local registered companions and
qualified operation targets; `run_case` rebases all companion server URLs to
loopback and asserts the complete request sequence. Those no-external-routing
protections remain intact.

## Architecture and order

Keep each workflow in the existing provider-oriented corpus boundaries:
one Arazzo specification, its local OpenAPI subset, labeled synthetic
responses, complete scenarios and a jq presentation. Shared session contracts
and provider pickup documentation belong to `specs/vsphere` and
`fixtures/openapi/vsphere`. Raw output remains the agent surface; views must
not hide business rules or turn a failed execution into success.

Session credentials enter through per-step `authorization` and
`session_token` names, with environment expansion and an explicit missing-value
guard. Never expose them as workflow outputs. Normal commands omit trace
capture and live single-step execution. Ordinary request failures attempt a
separate logout path and end nonzero; cancellation can skip cleanup and the
CLI does not preserve the original top-level error through cleanup.
Login has an explicit failure end action so error-body previews cannot reveal
a returned session token. Authenticated pickup commands always set
`--max-redirects 0`: CLI 0.8.2 does not reliably strip session credentials on
cross-host redirects, so following redirects is outside the supported contract.

A small configuration helper owns endpoint selection: validate an explicit
HTTPS origin, copy the provider bundle into ignored output and change only
the companions' top-level servers. It never stores credentials or disables
certificate verification. CLI 0.8.2 has no custom-CA option; document trust
limitations and any explicit operator-selected insecure-host invocation.

Implement and review the shared configuration/authentication verification
foundation first, then VM diagnosis, cluster assessment and OVF preparation.
Resolve configuration-target wire semantics before the cluster ticket starts.
One writer
owns the checkout; contract research and review remain read-only. Each ticket
must pass independent exact-candidate review before the next source slice.

## Verification and operational risks

Use the installed CLI's supported surfaces and versioned official contracts.
Prove session token propagation, scoped identity wiring and complete negative
paths using strict loopback requests. Test real CLI execution and jq output,
not a replacement expression evaluator. Check secret exposure using synthetic
sentinels and state any unsupported redaction/cleanup behavior accurately.
Verify that a redirect is refused without contacting its target, and that
unexpected login status with a token-shaped response exits nonzero without
printing the token or sending inventory requests.

The pickup guide must cover endpoint configuration, credentials, trust,
privileges, invocation, failure diagnostics and cleanup. Authentication creates
temporary sessions; inventory reads and OVF requirement inspection do not
authorize provisioning. A successful synthetic run does not prove live
certificate trust, authentication, permission sufficiency or response parity.

## System success condition

All three manifest entries validate, discover, preview and complete their
offline scenarios using the real CLI. The full verifier and its unit suite
pass with zero live provider calls. Every workflow has useful correlated
outputs, a runnable documented pickup path, official versioned sources and
a prominent live-unverified notice. Independent review covers each immutable
candidate and ticket contract. Reviewed changes and closure records are pushed
to `origin/main`; the three tickets and epic are completed. Git's unrelated
pre-existing untracked paths remain untouched.

---

**Disposition:** Accepted under Steve's 2026-10-27 direction to implement and
push the three workflows discussed in this thread. The bounded independent
plan review and its single correction recheck passed; the two findings are
addressed by redirect refusal and secret-safe login failure requirements.
The endpoint helper is decided by recommendation: CLI 0.8.2 lacks a server
override and a local credential-free copy keeps existing source contracts intact.
Decomposition starts with the settled foundation and VM slices. The cluster
ticket cannot start before its remaining wire-contract research gate is settled.
