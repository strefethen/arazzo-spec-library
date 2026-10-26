# Manifest

`manifest.yaml` is the source of truth for the corpus. Tools should use it to
discover specs, verification tiers, companion fixtures, and workflows.

## Root Shape

The manifest has a version and a list of entries:

```yaml
version: 1
specs: []
```

## Spec Entry

A future entry should use this shape:

```yaml
specs:
  - id: generic-crud.basic
    path: specs/generic-crud/basic.arazzo.yaml
    description: Basic create, read, update, delete workflow set.
    arazzo: "1.0.x"
    tier: hermetic
    openapi:
      - fixtures/openapi/generic-crud.yaml
    workflows:
      - createResource
      - readResource
    env: []
    verification:
      default:
        - arazzo-cli --json validate specs/generic-crud/basic.arazzo.yaml
    examples:
      quickstart:
        description: Run the default demo workflow.
        command: arazzo-cli --json run specs/generic-crud/basic.arazzo.yaml createResource --dry-run
        jq: views/generic-crud.basic.summary.jq
        highlights:
          - id
```

## Field Reference

| Field | Purpose |
|-------|---------|
| `id` | Stable corpus identifier. |
| `path` | Path to the Arazzo spec, relative to the repository root. |
| `description` | Short human-readable summary. |
| `arazzo` | Target Arazzo version or compatibility range. |
| `tier` | Verification tier: `hermetic`, `dry-run`, or `live`. |
| `openapi` | Companion OpenAPI documents needed by the spec. |
| `workflows` | Workflows default verification should exercise. |
| `env` | Required environment variables. Empty for default-safe specs. |
| `verification` | Optional command lists for default-safe and live-gated checks. |
| `examples` | Optional runnable examples, jq views, and output highlights for humans and agents. |
| `tests` | Required repository-relative scenario file for offline fixture execution. |
| `provider` | Optional provider name for discovery. |
| `category` | Optional workflow family or domain. |
| `read_only` | Whether live requests avoid mutating provider resources. |
| `live_policy` | Explicit policy such as `public-read-only` or `manual-quota-sensitive`. |
| `compatibility` | CLI version used for current proof; not a guarantee for untested releases. |

## Tooling Expectations

`scripts/verify.py` checks referenced files, exact workflow registration, local
source companions, validation, discovery, first-step dry-run, and all declared
scenarios. It rejects external sources, URL-based targets and server overrides
before fixture execution. Live policy is informational for agents, not a
network permission grant. Verification never evaluates `verification` or
`examples` shell strings. Those are human documentation only.
