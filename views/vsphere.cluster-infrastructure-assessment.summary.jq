def shown: if . == null then "unknown" elif type == "string" then . else tojson end;
def allocation($pool; $key; $unit):
  if ($pool | has($key)) then $pool[$key] as $a |
    "reservation=\($a.reservation) \($unit); limit=\(if $a.limit == -1 then "unlimited (-1)" else "\($a.limit) \($unit)" end); expandable=\($a.expandable_reservation); shares level=\($a.shares.level); shares=\($a.shares.shares | shown) (relative, relevant only for CUSTOM)"
  else "unknown (not reported)" end;
def configured($vms; $key; $unit):
  [$vms[] | select(has($key)) | .[$key]] as $known |
  ($vms | length) - ($known | length) as $missing |
  "\(if ($known | length) == 0 then 0 else ($known | add) end) \($unit) known across \($known | length)/\($vms | length) VMs; unknown for \($missing)" +
  (if $missing > 0 then "; total unknown" else "; complete configured total" end);
if .kind != "success" then error("Cluster assessment failed; no partial report") else
  .outputs as $o |
  "vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.",
  "Datacenter: \($o.datacenter.name) (\($o.datacenter.datacenter))",
  "Cluster: \($o.selected_cluster.name) (\($o.selected_cluster.cluster))",
  "HA enabled: \($o.selected_cluster.ha_enabled); DRS enabled: \($o.selected_cluster.drs_enabled)",
  "Root resource pool: \($o.resource_pool.name) (\($o.resource_pool_id), requested identity)",
  "Pool CPU allocation: \(allocation($o.resource_pool; "cpu_allocation"; "MHz"))",
  "Pool memory allocation: \(allocation($o.resource_pool; "memory_allocation"; "MB (provider units)"))",
  "Child resource pools: \($o.resource_pool.resource_pools | length) (identifiers only, not recursively inspected)",
  ($o.resource_pool.resource_pools[] | "  Child pool: \(.)"),
  "Hosts: \($o.hosts | length) (cluster-filtered visible inventory)",
  ($o.hosts | group_by(.connection_state)[] | "  Host connection \(.[0].connection_state): \(length)"),
  ($o.hosts[] | "  Host \(.name) (\(.host)): connection=\(.connection_state); power=\(.power_state | shown)"),
  "VMs: \($o.vms | length) (cluster-filtered visible inventory)",
  ($o.vms | group_by(.power_state)[] | "  VM power \(.[0].power_state): \(length)"),
  "Configured CPU: \(configured($o.vms; "cpu_count"; "vCPUs"))",
  "Configured memory: \(configured($o.vms; "memory_size_MiB"; "MiB"))",
  ($o.vms[] | "  VM \(.name) (\(.vm)): power=\(.power_state); configured CPU=\(.cpu_count | shown); memory=\(.memory_size_MiB | shown) MiB"),
  "Configured allocations are not utilization or available capacity. Inventory does not establish VM-to-host placement, storage/network backings or placement readiness. Raw output preserves every host/VM field; absent optional values are unknown."
end
