if .kind == "success" then
  .outputs as $o |
  "Crate: \($o.crate.name) @ \($o.version.num) (registry default, version id \($o.version.id))",
  "Source: https://crates.io/crates/\($o.crate.name)/\($o.version.num)",
  "Newest publication: \($o.crate.newest_version // "unavailable"); selected default: \($o.crate.default_version)",
  "License: \($o.version.license // "unavailable") | Rust: \($o.version.rust_version // "unspecified") | yanked: \($o.version.yanked)",
  "Features:",
  (if ($o.features | length) == 0 then "  none declared"
   else ($o.features | to_entries[] | "  \(.key): \(.value | join(", "))") end),
  "Direct dependency requirements: \($o.dependencies | length) (unpaginated; not a resolved lockfile)",
  ($o.dependencies[] | "  \(.crate_id) \(.req) | \(.kind) | optional=\(.optional) default_features=\(.default_features) | features=\(.features | join(", ")) | target=\(.target // "all")"),
  "Metadata only; no package downloaded or executed."
elif .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
else
  error("crates.io workflow failed: \(.code // .error // .kind)")
end
