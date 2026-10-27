# vSphere fixture provenance

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**

Every JSON body under `vm-guest-diagnosis/`,
`cluster-infrastructure-assessment/` and `ovf-deployment-preparation/` is a hand-authored synthetic example,
not a captured vCenter response. Names, IDs, UUIDs, documentation IP ranges and
`.invalid` domains are fictional. Scenarios add synthetic auth/session sentinels,
optional omissions, valid empty collections and deliberate malformed/error bodies.
Tests prove CLI 0.8.2 wiring and declared failure behavior only. They do not prove
real authentication, TLS trust, privileges, response parity or operational value.
VM container regressions include encoded empty/populated JSON strings and wrong
container types, with exact failure-logout request sequences. Genuine empty
containers and populated maps whose keys overlap the typed probes remain valid.

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

## OVF preparation contract

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**
The nine OVF JSON bodies are synthetic, including fictional library/item IDs,
target candidates, mapping names, EULA text and an illustrative open parameter
object. They are not a real appliance or an accepted license. Checked against
official **8.0.3** sources on 2026-10-27:

- Session, datacenter, cluster and resource-pool operations reuse the exact
  contracts above; the OVF subset links each operation's official page. Pool
  detail omits a mandatory ID, so its requested identity comes from cluster GET.
- [Item GET](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/content/api/content/library/item/library_item_id/get/)
  documents `id` as absent on GET/list. Retain the explicit requested identity,
  verify `library_id` and `type=ovf`, and expose name, `content_version`,
  `metadata_version`, `version`, `cached`, creation/modification times and
  description. Those fields are documented as always present for GET; `size`,
  `last_sync_time`, `source_id` and certificate information may be absent.
  Names need not be unique. Size is bytes and can be zero when uncached.
- [Folder list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/folder/get/)
  uses plural `folders`, `datacenters`, singular `type`; uppercase
  [VIRTUAL_MACHINE](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/Folder_Type/)
  is the required folder kind. Exact supplied ID plus returned datacenter scope
  must yield one matching folder. The provider cap is 1000.
- [Datastore list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/datastore/get/)
  uses `datastores` and `datacenters`, with a 2500 hard cap.
  [Summary](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/Datastore_Summary/)
  requires datastore/name/type; capacity/free_space are optional bytes, periodically
  updated. Supported types are VMFS, NFS, NFS41, CIFS, VSAN, VFFS and VVOL.
- [Network list](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/network/get/)
  uses `networks` and `datacenters`, with a 1000 hard cap.
  [Summary](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/Network_Summary/)
  requires network/name/type; types are STANDARD_PORTGROUP,
  DISTRIBUTED_PORTGROUP and OPAQUE_NETWORK. Neither list proves cluster access.
- [OVF filter](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/api/vcenter/ovf/library-item/ovf_library_item_id__action=filter/post/)
  is POST with `action=filter`, JSON `target` wrapper, required
  `resource_pool_id` and optional `folder_id`/`host_id`. This workflow supplies
  the returned pool and selected folder only. The
  [target](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/vcenter/data-structures/Ovf_LibraryItem_DeploymentTarget/)
  documents the VM-folder requirement and conditional automatic host selection.
  Response `EULAs` is required (capitalization matters); `name`, `annotation`,
  `networks`, `storage_groups`, `additional_params` are optional. Empty requirement
  arrays are valid. Additional parameters are open objects preserved without
  guessed subtype schemas; their complete validation remains operator work.

Scenarios assert every path, exact query/body and per-step header, Basic only
on login, retained request item identity, returned pool wiring, valid omissions
and empty arrays. Bounded negative cases reject zero/duplicate/malformed identity
results, JSON-string container impostors, wrong library/type/folder kind,
permissions and OVF 400/404/500, with exact nonzero failure cleanup. Successful
and failure logout errors and secret-safe login failures are also exercised.
No ConfigTargets, deployment, license acceptance, live calls or retries occur.
Datastore/network selections remain datacenter-scoped candidates, with mapping,
placement, policy, capacity and compatibility checks explicitly unresolved.
The report makes no storage/network, VM-to-host, placement or utilization claim.
