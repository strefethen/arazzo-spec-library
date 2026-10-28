if .kind != "success" then error("release-candidate inspection did not succeed") else
  .outputs as $o |
  "App: \($o.selected_app.attributes.bundleId) (\($o.selected_app.id))" ,
  "Version: iOS \($o.selected_version.attributes.versionString) (\($o.selected_version.id)); state \($o.selected_version.attributes.appVersionState)",
  "Attached build: \($o.attached_build_id); build number \($o.build.attributes.version); processing \($o.build.attributes.processingState)",
  "Expired: \(if ($o.build.attributes | has("expired")) then ($o.build.attributes.expired | tostring) else "unknown" end); uploaded: \($o.build.attributes.uploadedDate // "unknown"); expires: \($o.build.attributes.expirationDate // "unknown")",
  "Uses non-exempt encryption: \(if ($o.build.attributes | has("usesNonExemptEncryption")) then ($o.build.attributes.usesNonExemptEncryption | tostring) else "unknown" end)",
  "Inspection only; this result does not establish App Store submission readiness."
end
