---
title: Enforce documented JSON Schema input bounds in the CLI before HTTP execution
type: bug
priority: 2
state: paused
created_at: 2026-10-26T18:52:07Z
last_changed: 2026-10-26T18:52:37Z
---
# Enforce documented JSON Schema input bounds in the CLI before HTTP execution

## Goal
Observed installed arazzo-cli 0.8.2 accepts --input-json per_page=999 with --strict-inputs despite a maximum of 30. Corpus specs now stop after the first small identity request before any oversized collection query. Full pre-request schema validation needs a separately approved CLI change; no CLI files changed here.

## Note (2026-10-26 18:52 UTC) — Paused
gate: separate CLI input-validation scope and approval — Steve clears it; corpus collection guards are already in place
