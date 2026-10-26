if .kind == "success" then
  .outputs as $o |
  if ($o.editions | type) != "array" then error("editions collection was not reported") else
  "Selected: \($o.work.title) [\($o.work.key)]",
  "Search: first relevance match of \($o.total_matches); not an exhaustive search",
  "Authors: \(($o.selected_match.author_name // []) | join(", "))",
  "Source: https://openlibrary.org\($o.work.key)",
  "Editions: \($o.editions | length), limit \($o.edition_limit), offset \($o.edition_offset); total unavailable",
  ($o.editions[] | "  \(.title) [\(.key)] | \(.publish_date // "date unavailable") | ISBN13: \((.isbn_13 // []) | join(", "))"),
  (if ($o.editions | length) == $o.edition_limit
   then "Page full; more may exist. Next offset: \($o.edition_offset + $o.edition_limit)"
   else "Page shorter than requested limit; no further page requested."
   end) end
elif .kind == "dryRun" then
  .requests[] | "\(.method) \(.url)"
else
  error("Open Library workflow failed: \(.code // .error // .kind)")
end
