if .kind == "success" then
  .outputs as $o |
  if ($o.results | type) != "array" then error("package result collection missing") else
  "Socket risk metadata, not a security verdict",
  "Quota before lookup: \($o.quota_remaining)/\($o.quota_max)",
  ($o.results[] | select(has("name")) |
    "\(.name)@\(.version): alerts=\(if has("alerts") then (.alerts | length) else "not reported" end)",
    (.alerts[]? | "  \(.type): \(.severity // "severity not reported")")),
  ($o.results[] | select(has("summary")) | "Lookup summary: \(.summary | tojson)") end
elif .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
else
  error(.error // "unexpected CLI result")
end
