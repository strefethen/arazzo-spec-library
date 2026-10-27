# vSphere workflow contract assessment

Documentation research on 2026-10-27 targets **vSphere Automation API 8.0.3**.
No vCenter deployment, account or live API access was available. This assessment
does not establish runtime compatibility or grant permission to change infrastructure.

## Intended outcomes

The 2026-10-27 conversation authorized implementing and pushing substantial
multi-resource workflows, including authentication and clear live-validation
limitations. Three outcomes were discussed: VM/guest diagnosis, cluster
infrastructure assessment, and template deployment preparation. OVF library
items are the documented scope for the third outcome; native VM templates use
a different contract.

## Contract findings

- [Session creation](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/cis/api/session/post/)
  uses POST with HTTP Basic authentication and returns HTTP 201 with a JSON
  string. Subsequent requests use `vmware-api-session-id`.
  [Deletion](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/cis/api/session/delete/)
  returns HTTP 204. These are authentication side effects, even for inventory reads.
- [VM discovery](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/get/)
  accepts `names` and `datacenters`. Require exactly one visible scoped match.
  [VM detail](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/get/)
  uses `guest_OS`, `memory.size_MiB` and device-ID-keyed maps. Inventory results
  expose `memory_size_MiB`; these spellings differ deliberately.
- Guest identity, networking, interfaces, routes and filesystem APIs provide
  related telemetry. Interface `nic` references configuration NICs; route
  `interface_index` indexes the ordered interfaces array. Filesystem `mappings`
  can reference virtual disk IDs. Optional absence is unknown, not an empty
  collection. See the [pinned guest SDK contract](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/8.0.3.0/com.vmware.vcenter.vm.html).
- [Cluster detail](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/cluster/cluster/get/)
  supplies the root resource-pool identity, not a complete topology graph.
  Cluster-scoped host and VM lists provide inventory, not runtime utilization.
- [Configuration targets](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/environment-browser/config-targets/get/)
  supplies supporting cluster infrastructure and requires an additional
  `api_release` parameter. Its exact wire placement is a research gate.
  [Hello negotiation](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/system__action=hello/post/)
  exchanges `api_releases` for `api_release`. An empty result must fail.
- Ordinary datastore/network discovery cannot stand in for cluster backing
  relationships: the documented filters lack cluster and host selectors.
- [Content item get](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/content/api/content/library/item/library_item_id/get/)
  supplies library, type, cache/version metadata; `id` is absent on this read.
  Retain the requested item identity and verify expected library/type.
- [OVF filter](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/ovf/library-item/ovf_library_item_id__action=filter/post/)
  accepts `target.resource_pool_id` plus optional host/folder identities and
  returns networks, storage groups, additional parameters and `EULAs`.
  This inspects requirements; it does not deploy, accept EULAs or prove readiness.

## Verification boundary and remaining gates

Use local OpenAPI companions, qualified operations, explicit JSON Pointers,
strict scoped identity checks and complete real-CLI loopback scenarios. Provider
limits are hard result caps, not pagination. Synthetic fixtures establish
request wiring and declared failure behavior only.

CLI 0.8.2 was checked with 43 synthetic probes and four TLS controls. It can
pass a scalar login token into per-step headers and run separate success and
failure logout paths. Failure cleanup must deliberately end nonzero: a goto
to an ordinarily successful logout would otherwise report success. A separate
logout step with a false success criterion prevents that. Original top-level
errors are replaced by the cleanup error; cancellation/whole-workflow timeout
can skip cleanup. No guaranteed finally/rethrow mechanism was established.

Use a credential named `authorization`, supplied as a complete env reference
through a single-quoted `--input`, with an explicit shell missing-value guard.
Do not use global Authorization headers. Name the intermediate token
`session_token`; never expose credentials as final workflow outputs. Default
traces can include the scalar session response. Normal pickup commands must
omit traces and live single-step execution; the latter can omit logout.
Every authenticated pickup command must set `--max-redirects 0`, because the
pinned CLI's cross-host redirect stripping omits `vmware-api-session-id`.
Login must explicitly end on failure: otherwise an unexpected status can
expose the scalar session response in the ordinary error-body preview.

There is no runtime server override flag or custom-CA option in CLI 0.8.2.
Use a cohesive configuration helper to validate an explicit HTTPS origin and
copy/rebase the local bundle's top-level OpenAPI server URLs into ignored
output. Reject userinfo, paths, queries, fragments, placeholders and server
overrides. Do not silently disable TLS verification. A documented explicit
`--insecure-host` choice disables verification; it is not a trust-store fix.

Research evidence is retained outside tracked source under
`/private/tmp/vsphere-cli-research-results.jsonl`,
`/private/tmp/vsphere-cli-tls-results.jsonl` and
`/private/tmp/vsphere_cli_research.py`. Only synthetic credentials were used.
The installed binary was checked against sibling source at tag `v0.8.2`,
because sibling main has newer behavior.

Any future configuration-target enrichment requires settling its release wire
contract first. Preserve failed operations as failures; do not silently return
partial reports or substitute wider inventory.

### Cluster scope disposition

Focused follow-up inspected the official 8.0 U3 Python and Java bindings as
well as the API page. None established the placement of `api_release` for
configuration targets. `8.0.3.0` is an actual API release identifier; that does
not establish how this particular operation accepts it. Do not guess either
a query parameter or a header.

Steve approved shipping cluster configuration, resource-pool allocations,
hosts and VM inventory on 2026-10-27, with storage/network enrichment gated as
a follow-up. The accepted cluster workflow therefore does not need the
unresolved endpoint and must not imply that it inspected cluster backings.
OVF preparation inspects explicit datacenter-scoped candidates and reports
remaining placement checks; it does not relabel those candidates as proven
cluster-accessible resources.

Publish a prominent statement in each workflow and its documentation:
**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**
Explain that a real deployment still needs to confirm authentication, TLS,
privileges, response compatibility and operational usefulness.
