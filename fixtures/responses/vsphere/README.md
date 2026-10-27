# vSphere fixture provenance

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**

Every JSON body under `vm-guest-diagnosis/` is a hand-authored synthetic example,
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
