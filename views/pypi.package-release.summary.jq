if .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
elif .kind != "success" then
  error("PyPI workflow failed: \(.code // "unknown"): \(.error // .message // "no details")")
else
  .outputs as $o |
  if ($o.files | type) != "array" or ($o.vulnerabilities | type) != "array" then
    error("PyPI files and vulnerabilities must be arrays")
  else
    "PyPI: \($o.package)==\($o.version)",
    "\($o.summary)\n\($o.project_url)",
    "Requires Python: \($o.requires_python // "not supplied"); release yanked: \($o.yanked); reason: \($o.yanked_reason // "none supplied")",
    "Files: \($o.files | length) (showing at most 20; unpaginated version-specific snapshot)",
    ($o.files[:20][] | "  \(.filename) [\(.packagetype)] \(.size) bytes; yanked=\(.yanked); reason=\(.yanked_reason // "none supplied")\n    sha256=\(.digests.sha256)\n    \(.url)"),
    "Vulnerability records: \($o.vulnerabilities | length) (showing at most 20)",
    ($o.vulnerabilities[:20][] | "  \(.id) aliases=\((.aliases // []) | join(",")) fixed_in=\((.fixed_in // []) | join(",")) withdrawn=\(.withdrawn // "no") \(.link)"),
    "Metadata is not a security verdict; no package was downloaded or hash verified."
  end
end
