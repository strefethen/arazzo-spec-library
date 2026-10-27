def shown: if . == null then "unknown" elif type == "string" then . else tojson end;
def niclink($o; $id):
  if $id == null then "unknown"
  elif $o.configuration.nics[$id] == null then "\($id) -> unknown configured NIC"
  else "\($id) -> \($o.configuration.nics[$id].label | shown)" end;
def disklink($o; $id):
  if $id == null then "unknown"
  elif $o.configuration.disks[$id] == null then "\($id) -> unknown configured disk"
  else "\($id) -> \($o.configuration.disks[$id].label | shown)" end;
if .kind != "success" then error("VM diagnosis failed; no partial report") else
  .outputs as $o |
  "vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.",
  "Datacenter: \($o.datacenter.name) (\($o.datacenter.datacenter))",
  "VM: \($o.selected_vm.name) (\($o.selected_vm.vm))",
  "Power: \($o.configuration.power_state | shown)",
  "Configured OS: \($o.configuration.guest_OS | shown); reported OS: \($o.guest_identity.name | shown) / \($o.guest_identity.family | shown)",
  "Configured CPU: \($o.configuration.cpu.count | shown); memory: \($o.configuration.memory.size_MiB | shown) MiB (configured allocation, not utilization)",
  "Hardware: \($o.configuration.hardware.version | shown); BIOS UUID: \($o.configuration.identity.bios_uuid | shown)",
  "Tools: \($o.tools.run_state | shown); upgrade policy: \($o.tools.upgrade_policy | shown)",
  "Tools version: \($o.tools.version | shown); status: \($o.tools.version_status | shown)",
  "Reported host: \($o.guest_identity.host_name | shown); primary IP: \($o.guest_identity.ip_address | shown)",
  "DNS: \($o.guest_networking.dns | shown); assigned values: \($o.guest_networking.dns_values | shown)",
  "Configured NICs: \($o.configuration.nics | length)",
  ($o.configuration.nics | to_entries[] | "  NIC \(.key): \(.value.label | shown); backing: \(.value.backing | shown); state: \(.value.state | shown)"),
  "Guest interfaces: \($o.guest_interfaces | length) (provider order)",
  ($o.guest_interfaces | to_entries[] |
    "  interface[\(.key)] MAC: \(.value.mac_address | shown); Mapping: \(niclink($o; .value.nic)); IP: \(.value.ip | shown)"),
  "Guest routes: \($o.guest_routes | length)",
  ($o.guest_routes[] | . as $route |
    "  Route \(.network)/\(.prefix_length) via \(.gateway_address | shown); " +
    (if .interface_index == null then "Mapping: unknown"
     elif .interface_index < 0 or .interface_index >= ($o.guest_interfaces | length) then "Mapping: interface[\(.interface_index)] unavailable"
     else "interface[\(.interface_index)] -> \(niclink($o; $o.guest_interfaces[$route.interface_index].nic))" end)),
  "Configured disks: \($o.configuration.disks | length)",
  ($o.configuration.disks | to_entries[] | "  Disk \(.key): \(.value.label | shown); capacity: \(.value.capacity | shown) bytes (configured allocation)"),
  "Guest filesystems: \($o.guest_filesystems | length)",
  ($o.guest_filesystems | to_entries[] |
    "  Filesystem \(.key): \(.value.filesystem | shown); capacity: \(.value.capacity | shown) bytes; free: \(.value.free_space | shown) bytes; Mapping: " +
    (if .value.mappings == null then "unknown"
     elif (.value.mappings | length) == 0 then "[] (reported empty)"
     else [.value.mappings[] | disklink($o; .disk)] | join(", ") end)),
  "Mappings use only reported device IDs and interface indices; missing mappings are unknown. Filesystem capacity need not equal virtual disk capacity. Guest telemetry is not a utilization or placement guarantee."
end
