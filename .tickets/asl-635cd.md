---
title: Establish the vSphere cluster backing discovery release wire contract
type: task
priority: 2
state: paused
created_at: 2026-10-27T18:34:04Z
last_changed: 2026-10-27T18:34:23Z
---
# Establish the vSphere cluster backing discovery release wire contract

## Goal
Enable future cluster storage/network enrichment only after official contract evidence or explicitly authorized live validation establishes ConfigTargets api_release wire placement. Official8.0.3 API page requires it but inspected Python/Java bindings omit the parameter metadata; never guess query/header placement.

## Design
Follow-up outside the approved documented-cluster delivery. Keep no-live-validation status explicit. Do not replace cluster backings with datacenter-wide resources. See plans/assessments/vsphere-contracts-2026-10-27.md and official ConfigTargets operation.

## Note (2026-10-27 18:34 UTC) — Paused
gate: official api_release wire-placement evidence or separately authorized live confirmation — future contract research clears
