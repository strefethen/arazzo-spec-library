# vSphere workflow delivery verification — 2026-10-27

Delivered three session-authenticated, multi-resource workflows:

- `vsphere.vm-guest-diagnosis`: scoped VM configuration, Tools and guest
  identity/network/interface/route/filesystem relationships.
- `vsphere.cluster-infrastructure-assessment`: scoped cluster HA/DRS, returned
  root-pool allocations and children, host states and VM inventory.
- `vsphere.ovf-deployment-preparation`: explicit OVF-item provenance, scoped
  compute and target candidates, and OVF requirements with mapping and placement
  checks left explicit. It does not deploy or accept EULAs.

The [pickup guide](../../specs/vsphere/README.md) covers endpoint configuration,
private credential preparation, full CLI invocations, raw output and jq views,
preview, privilege/TLS limits and session cleanup limits. Every specification,
manifest description and provider guide carries the documentation-based,
synthetic-fixture and live-unverified boundary.

## Evidence and review

Final reviewed source:
[e90cb39](https://github.com/strefethen/arazzo-spec-library/commit/e90cb39f49ce7a07557c181ff3b4efcfb42ce169).
The implementation's complete offline run passed **396 workflow scenarios**
and **58 unit tests**, with zero live provider requests. The last independent
review reran all 156 OVF cases and 58 units, inspected the complete corpus run,
and matched all 18 final source/documentation hashes to committed bytes.

Each slice passed a fresh-context exact-candidate review before publication:

- Foundation: [asl-b4622](https://tkt.stevetrefethen.com/docs/asl-tickets/asl-b4622),
  final source [1ec8d3b](https://github.com/strefethen/arazzo-spec-library/commit/1ec8d3b3537d00bfc04b199c3fe131a1729859d2).
- VM diagnosis: [asl-8ed61](https://tkt.stevetrefethen.com/docs/asl-tickets/asl-8ed61),
  final source [12c8a87](https://github.com/strefethen/arazzo-spec-library/commit/12c8a87e75d42dfa2156b3cf65afa2905b04dc86).
- Cluster assessment: [asl-785d1](https://tkt.stevetrefethen.com/docs/asl-tickets/asl-785d1),
  final source [3d8b039](https://github.com/strefethen/arazzo-spec-library/commit/3d8b0391c46ab0505723f90a50e79d6ddd70bd5b).
- Corrective VM container guards: [asl-d3ccf](https://tkt.stevetrefethen.com/docs/asl-tickets/asl-d3ccf),
  final source [fce4c00](https://github.com/strefethen/arazzo-spec-library/commit/fce4c00026993b9783f5892c4df1aa2a5c13685e).
- OVF preparation: [asl-ac49e](https://tkt.stevetrefethen.com/docs/asl-tickets/asl-ac49e),
  final source [e90cb39](https://github.com/strefethen/arazzo-spec-library/commit/e90cb39f49ce7a07557c181ff3b4efcfb42ce169).

The orchestrator then observed the three workflows together after ticket
closure: one configured bundle, unchanged Arazzo bytes, OpenAPI parity except
server URLs, three catalog/show entries, strict validation and configured
first-login dry-runs. All passed without external requests. Local retained
proof is `.artifacts/vsphere-execution/system-proof.json`; per-ticket folders
retain immutable contracts, preflight state, command logs and review bindings.
Generated endpoint bundles and execution artifacts remain ignored.

All five members and [epic:asl-41557](https://tkt.stevetrefethen.com/docs/asl-tickets/asl-41557) completed. Pre-existing untracked work
was preserved. Final lifecycle/plan bookkeeping changes only documentation and
tracker metadata; it does not change reviewed behavior or require another
source review.

## Explicit limits

**No real vCenter execution has occurred.** Official vSphere 8.0 U3 contracts
and pinned SDK semantics informed the workflows; synthetic fixtures prove
chaining and declared failures, not live authentication, certificate trust,
privilege sufficiency, response parity or operational usefulness.

Steve approved the narrower documented cluster outcome. Storage/network backing
enrichment remains paused in [asl-635cd](https://tkt.stevetrefethen.com/docs/asl-tickets/asl-635cd) until its required API-release wire
contract can be established; it is outside this completed delivery. Cancellation
can skip session cleanup, cleanup can replace the original top-level error,
and normal commands refuse redirects and omit potentially sensitive traces.
