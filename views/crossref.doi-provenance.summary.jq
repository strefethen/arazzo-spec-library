if .kind == "success" then
  .outputs as $o |
  "DOI: \($o.work.DOI) | \(($o.work.title // ["title unavailable"]) | join("; "))",
  "Source: \($o.work.URL // ("https://doi.org/" + $o.work.DOI))",
  "Publisher metadata: \($o.work.publisher // "unavailable")",
  "Depositing member: \($o.member["primary-name"]) [\($o.member.id)]",
  "Provenance: https://api.crossref.org/members/\($o.member.id)",
  "Related by depositor, not citations: \($o.related_works | length) of \($o.total_related), requested \($o.rows)",
  ($o.related_works[] | "  \(.DOI) | \((.title // ["title unavailable"]) | join("; ")) | \(.type // "type unavailable")"),
  (if ($o.related_works | length) < $o.rows
   then "End of this cursor result set."
   else "Next cursor (not fetched): \($o.next_cursor)"
   end)
elif .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
else
  error("Crossref workflow failed: \(.code // .error // .kind)")
end
