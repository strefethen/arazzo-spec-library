# Verification Tiers

Verification tiers describe how much proof the repository can provide without
surprising the user.

## `hermetic`

Hermetic specs run entirely from repository-local inputs.

Expected checks:

- validate the spec
- list workflows
- inspect listed workflows
- dry-run or test workflows without network access

## `dry-run`

Dry-run specs can be inspected and executed in dry-run mode, but may describe
operations that would require live services outside default checks.

Expected checks:

- validate the spec
- list workflows
- inspect listed workflows
- run workflows with `--dry-run`

## `live`

Live specs can execute against an external service under its provider policy.
Public read-only specs may need no credentials; authenticated providers require
the named environment/input values. Every tier remains default-safe.

Expected default checks:

- validate the spec
- list workflows
- inspect listed workflows
- dry-run workflows

Live execution is an explicit action, never part of default CI. Every registered
entry also has loopback fixture scenarios; the tier does not imply a live smoke
has passed. See provider READMEs for dated proof and unverified boundaries.
