# vSphere fixture provenance

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**

Every JSON body under `vm-guest-diagnosis/` and
`cluster-infrastructure-assessment/` is a hand-authored synthetic example,
not a captured vCenter response. Names, IDs, UUIDs, documentation IP ranges and
`.invalid` domains are fictional. Scenarios add synthetic auth/session sentinels,
optional omissions, valid empty collections and deliberate malformed/error bodies.
Tests prove CLI 0.8.2 wiring and declared failure behavior only. They do not prove
real authentication, TLS trust, privileges, response parity or operational value.

Contracts checked on 2026-10-27 against the exact official **8.0.3** pages:

- [Session create](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/cis/api/session/post/)
  and [delete](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/cis/api/session/delete/):
  201 JSON scalar token; session header thereafter; 204 logout with no wire body.
- [Datacenter list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/datacenter/get/)
  and [VM list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/get/):
  unwrapped arrays, `names` and VM `datacenters` query filters, 1000/4000 hard caps.
- [VM get](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/get/):
  `guest_OS`, `memory.size_MiB`, keyed device maps; list uses `memory_size_MiB`.
- [Tools](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/tools/get/)
  and [guest identity](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/guest/identity/get/):
  separate configured vs reported state; unavailable guest data fails with 503.
- [Networking](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/guest/networking/get/),
  [interfaces](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/guest/networking/interfaces/get/)
  and [routes](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/guest/networking/routes/get/):
  optional DNS/IP fields, ordered interface array, optional `nic` and route
  `interface_index` references; do not sort interfaces before correlating.
- [Local filesystem](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/vm/guest/local-filesystem/get/):
  filesystem capacity/free bytes and optional `mappings[].disk` IDs. The API
  page's displayed object illustrates a map value, not the complete response.
  The [official 8.0.3.0 SDK LocalFilesystem.get return type](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/8.0.3.0/com.vmware.vcenter.vm.html#com.vmware.vcenter.vm.guest_client.LocalFilesystem.get)
  confirms a dictionary keyed by filesystem path, with `LocalFilesystem.Info`
  values. Its optional `mappings` and the
  [guest networking bindings](https://vmware.github.io/vsphere-automation-sdk-python/vsphere/8.0.3.0/com.vmware.vcenter.vm.guest.html)
  establish absent-as-unknown semantics.

Only reported mappings join the layers. Disk allocation need not equal guest
filesystem capacity; multiple disks/filesystems or unmapped temporary filesystems
are possible. CPU/memory/disk configuration is allocation, not utilization or
evidence of deployment capacity. No historical `/rest` `value` wrapper is used.

## Cluster assessment contract

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**
The six cluster JSON files describe a fictional datacenter/cluster, its returned
root pool with two child IDs, two hosts and three VMs. They were authored against
these official **8.0.3** contracts checked on 2026-10-27, not captured live:

- [Cluster list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/cluster/get/)
  accepts `names` and `datacenters`, with a 1000-result hard cap.
  [Cluster summary](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/Cluster_Summary/)
  requires `cluster`, `name`, `ha_enabled` and `drs_enabled`.
- [Cluster get](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/cluster/cluster/get/)
  returns `name` and `resource_pool`, without a mandatory cluster ID.
- [Resource-pool get](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/resource-pool/resource_pool/get/)
  requires `name` and `resource_pools` (child IDs); `cpu_allocation` and
  `memory_allocation` are optional. It supplies no mandatory pool ID, so the
  report retains the exact requested identity from cluster detail. Scenarios
  assert that exact path, including an alternate returned root-pool ID; they
  do not invent a wrong-response-ID requirement on an absent field.
- [Resource allocation](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/ResourcePool_ResourceAllocationInfo/)
  requires `reservation`, `expandable_reservation`, `limit` and `shares` when
  present. Reservation/limit units are MHz for CPU and MB for memory; `-1` is
  unlimited. [Shares](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/ResourcePool_SharesInfo/)
  requires `level`; the optional relative shares count is relevant for `CUSTOM`.
- [Host list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/host/get/)
  accepts `clusters`, with a 2500-result hard cap.
  [Host summary](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/Host_Summary/)
  requires `host`, `name` and `connection_state`; `power_state` is optional.
- [VM list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/vm/get/)
  accepts `clusters`, with a 4000-result hard cap.
  [VM summary](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/VM_Summary/)
  requires `vm`, `name`, `power_state`; `cpu_count` and `memory_size_MiB` are
  optional if configuration is unavailable. The cluster subset preserves this
  optionality and its summary explicitly labels known subtotals and missing
  contributions. Host power omission is likewise unknown, never powered off.

All inventory lists are unwrapped arrays. An empty pool-child/host/VM list is
valid and differs from missing/null/malformed data. Scenarios add optional
omissions, malformed later entries, unique-selection failures, incorrect
cluster names, invalid pool references, permissions/not-found/provider-limit
errors, login failure and both logout failure paths. They enforce Basic only
on login and the exact session header thereafter, with synthetic sentinels
forbidden in captured output. These are contract/wiring tests, not live proof.
The report makes no storage/network, VM-to-host, placement or utilization claim.
