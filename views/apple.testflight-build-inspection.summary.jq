if .kind != "success" then error("TestFlight inspection did not succeed") else
  .outputs as $o |
  "App: \($o.selected_app.attributes.bundleId) (\($o.selected_app.id))",
  "Version: iOS \($o.selected_prerelease_version.attributes.version) (\($o.selected_prerelease_version.id))",
  "Build: \($o.build.attributes.version) (\($o.build.id)); processing: \($o.build.attributes.processingState); audience type: \($o.build.attributes.buildAudienceType // "unknown")",
  "Expired: \(if ($o.build.attributes | has("expired")) then ($o.build.attributes.expired | tostring) else "unknown" end)",
  "Beta detail: \($o.beta_detail.id); internal: \($o.beta_detail.attributes.internalBuildState); external: \($o.beta_detail.attributes.externalBuildState)",
  (if ($o.review_submissions | length) == 0 then "Review: no visible submission returned" else "Review: \($o.review_submissions[0].attributes.betaReviewState); submitted: \($o.review_submissions[0].attributes.submittedDate // "unknown")" end),
  (if ($o.beta_groups | length) == 0 then "Groups: no associated groups returned" else "Groups: \($o.beta_groups | length) returned in this complete filtered page", ($o.beta_groups[] | "Group: \(.attributes.name) (\(.id)); internal: \(.attributes.isInternalGroup)") end),
  "Inspection only: six non-atomic observations visible to this token; no installation, effective audience, notification delivery or readiness conclusion. All-build groups and individual assignments are not fully audited."
end
