def shown: if . == null then "unknown" elif type == "string" then . else tojson end;
def allocation($pool; $key; $unit):
  if ($pool | has($key)) then $pool[$key] as $a |
    "reservation=\($a.reservation) \($unit); limit=\(if $a.limit == -1 then "unlimited (-1)" else "\($a.limit) \($unit)" end); expandable=\($a.expandable_reservation); shares level=\($a.shares.level); shares=\($a.shares.shares | shown) (relative, relevant only for CUSTOM)"
  else "unknown (not reported)" end;
if .kind != "success" then error("OVF preparation failed; no partial report") else
  .outputs as $o |
  "vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.",
  "Datacenter: \($o.datacenter.name) (\($o.datacenter.datacenter))",
  "Cluster: \($o.selected_cluster.name) (\($o.selected_cluster.cluster)); HA=\($o.selected_cluster.ha_enabled); DRS=\($o.selected_cluster.drs_enabled)",
  "Root pool: \($o.resource_pool.name) (\($o.resource_pool_id), returned by cluster; requested pool identity)",
  "Pool CPU allocation: \(allocation($o.resource_pool; "cpu_allocation"; "MHz"))",
  "Pool memory allocation: \(allocation($o.resource_pool; "memory_allocation"; "MB (provider units)"))",
  "Child pool IDs (not inspected): \($o.resource_pool.resource_pools | tojson)",
  "OVF item: \($o.item.name) (\($o.item_id), requested identity; GET omits id); library=\($o.item.library_id); type=\($o.item.type)",
  "Template versions: content=\($o.item.content_version); metadata=\($o.item.metadata_version); version=\($o.item.version)",
  "Cache: cached=\($o.item.cached); size=\($o.item.size | shown) bytes; created=\($o.item.creation_time); modified=\($o.item.last_modified_time); last sync=\($o.item.last_sync_time | shown); source item=\($o.item.source_id | shown)",
  "Item description: \($o.item.description)",
  "Security metadata (not a deployment safety conclusion): compliance=\($o.item.security_compliance | shown); certificate=\($o.item.certificate_verification_info | shown)",
  "Target VM folder: \($o.folder.name) (\($o.folder.folder)); type=\($o.folder.type)",
  "Datastore candidate: \($o.datastore_candidate.name) (\($o.datastore_candidate.datastore)); type=\($o.datastore_candidate.type); capacity=\($o.datastore_candidate.capacity | shown) bytes; free=\($o.datastore_candidate.free_space | shown) bytes (periodically updated, not reserved)",
  "Network candidate: \($o.network_candidate.name) (\($o.network_candidate.network)); type=\($o.network_candidate.type)",
  "OVF default name=\($o.requirements.name | shown); annotation=\($o.requirements.annotation | shown)",
  (if $o.requirements | has("networks") then "Required network mapping names: \($o.requirements.networks | tojson)" else "No network section reported (networks absent)" end),
  (if $o.requirements | has("storage_groups") then "Required storage mapping names: \($o.requirements.storage_groups | tojson)" else "No storage-group section reported (storage_groups absent)" end),
  "EULAs (not accepted): \($o.requirements.EULAs | tojson)",
  (if $o.requirements | has("additional_params") then "Additional parameters (unmodified; inspect complete objects): \($o.requirements.additional_params | tojson)" else "No additional parameters reported for this target (additional_params absent)" end),
  "Unresolved: assign every required network/storage mapping and default storage choice; validate parameter subtypes/values and review EULAs. Candidates are datacenter-scoped, not proven cluster-accessible. Confirm host placement (including DRS/explicit-host needs), storage/network access, capacity, policies, compatibility, privileges and TLS. Configured pool allocations are not utilization or available capacity. Filter inspection does not deploy, accept licenses, reserve resources or prove deployment readiness."
end
