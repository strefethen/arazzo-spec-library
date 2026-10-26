if .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
elif .kind != "success" then
  error("Docker Hub workflow failed: \(.code // "unknown"): \(.error // .message // "no details")")
else
  .outputs as $o |
  if ($o.images | type) != "array" or ($o.images | length) == 0 then
    error("Docker Hub tag has no image platform metadata")
  else
    "Docker Hub: \($o.namespace)/\($o.repository):\($o.tag) (tag id \($o.tag_id))",
    "Selected first tag on page \($o.page), page size \($o.page_size), provider order; not necessarily latest",
    "Tag count: \($o.tag_count); next: \($o.next // "none"); previous: \($o.previous // "none")",
    "Updated: \($o.last_updated); compressed bytes: \($o.full_size)",
    "Image records: \($o.images | length) (showing at most 30; unpaginated tag detail)",
    ($o.images[:30][] | "  \(.os)/\(.architecture)\(if .variant then "/" + .variant else "" end) \(.digest // "digest unavailable") \(.size) bytes"),
    "Platform and digest metadata is not a security verdict or proof of runnable image support; no image was pulled."
  end
end
