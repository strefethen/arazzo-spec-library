# Verification Model

`arazzo-cli` is the first verification engine for this corpus. The repository
should remain tool-agnostic, but every practical claim should be checkable with
commands.

## Baseline Checks

A typical default-safe spec should support:

```bash
arazzo-cli --json validate specs/generic-crud/basic.arazzo.yaml
arazzo-cli --json list specs/generic-crud/basic.arazzo.yaml
arazzo-cli --json show createResource --dir specs/generic-crud
arazzo-cli --json run specs/generic-crud/basic.arazzo.yaml createResource --dry-run
```

`python3 scripts/verify.py` drives these checks from `manifest.yaml` and executes
every declared fixture scenario through the real CLI. Contributor requirements
and the scenario contract are in [tests/README.md](../../tests/README.md).

## CI Rule

No spec should enter the accepted corpus without meaningful offline execution
proof. Fixture verification and opt-in live-provider proof are separate claims.

For most specs, that proof should include validation, workflow listing, workflow
inspection, and dry-run execution. Live execution should be opt-in and excluded
from default CI unless credentials are explicitly provided.

## Failure Behavior

Verification should fail closed. Missing files, missing environment variables,
or invalid manifest references should produce a clear failure instead of being
silently skipped.
