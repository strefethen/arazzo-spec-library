---
title: Add bounded read-only Apple release inspection
type: epic
priority: 2
state: open
created_at: 2026-10-28T22:59:06Z
last_changed: 2026-10-28T22:59:11Z
plan: investigation
tags:
    - apple
deps:
    - asl-5f73d
---
# Add bounded read-only Apple release inspection

## Goal
Deliver one exact-app, exact-IOS-version, attached-build inspection workflow with bounded offline proof. Steve authorized this read-only workflow direction on 2026-10-28.

## Design
Decided by recommendation: one contained member implements apple.release-candidate-inspection in the existing corpus. Scope is four authenticated GETs, external Bearer JWT, fail-closed selection and synthetic offline verification. No live Apple calls, writes, token signing or full submission-readiness claim. Existing public-API first-wave epic does not own this authenticated slice.

## Acceptance Criteria
- [ ] The member workflow meets its exact selection, attached-build, authentication and offline proof contract.

## Testing Obligations
Observe the member focused scenarios, full corpus verification and independent exact-candidate review. Retain live-unverified limitations; no authenticated Apple execution.
