if .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
elif .kind != "success" then
  error("GitHub workflow failed: \(.code // "unknown"): \(.error // .message // "no details")")
else
  .outputs as $o |
  if ($o.releases | type) != "array" or ($o.issues | type) != "array" then
    error("GitHub collections must be arrays")
  else
    "Repository: \($o.repository)\n\($o.url)",
    "Branch: \($o.default_branch); archived: \($o.archived)",
    "Page \($o.page), at most \($o.per_page) items per collection; not exhaustive",
    "Releases: \($o.releases | length)",
    ($o.releases[] | "  \(.tag_name) prerelease=\(.prerelease) \(.html_url)"),
    "Releases pagination: \($o.releases_link // "no Link header")",
    "Recent issues/PRs: \($o.issues | length)",
    ($o.issues[] | "  \(if has("pull_request") then "PR" else "Issue" end) #\(.number) [\(.state)] \(.title) \(.html_url)"),
    "Issues pagination: \($o.issues_link // "no Link header")",
    "Rate remaining: \($o.rate_remaining // "not supplied"); reset epoch: \($o.rate_reset // "not supplied")"
  end
end
