if .kind == "success" then
  .outputs as $o |
  if ($o.alerts | type) != "array" then error("alerts collection was not reported") else
  "Forecast for \($o.location), \($o.state)",
  "\($o.first_period_name): \($o.first_temperature) deg\($o.first_temperature_unit), \($o.first_short_forecast)",
  "Active alerts: \($o.alerts | length)",
  ($o.alerts[] | "\(.properties.event) [\(.properties.severity)]: \(.properties.headline)") end
elif .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
else
  error(.error // "unexpected CLI result")
end
