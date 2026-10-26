# Repository Structure

The repository separates specifications, fixtures, invalid cases, and docs so
renderers and verification tools can consume each surface directly.

```text
.
├── docs/
│   ├── _sidebar.json
│   └── index.md
├── fixtures/
│   ├── openapi/
│   └── responses/
├── invalid/
├── manifest.yaml
├── specs/
└── views/
```

## `specs/`

Valid specs live under `specs/`, grouped by provider or reusable workflow
pattern. New top-level directories should represent durable categories, not
one-off experiments.

Example future paths:

```text
specs/generic-crud/basic.arazzo.yaml
specs/github/issues.arazzo.yaml
specs/oauth/client-credentials.arazzo.yaml
```

## `fixtures/`

Fixtures provide local data needed by specs.

- `fixtures/openapi/` stores companion OpenAPI documents.
- `fixtures/responses/` stores static responses or response envelopes used for
  hermetic examples.

Default verification should be able to use fixtures without calling external
services.

## `views/`

Reusable jq projections live under `views/`. These keep `arazzo-cli --json` as the
primary automation contract while giving humans and agents readable summaries
without retyping fragile jq programs in every command example.

## `invalid/`

Invalid specs live under `invalid/`. Each invalid example should be intentional,
documented, and useful as a validation case.

## `manifest.yaml`

The manifest is the corpus index. It declares each spec, its verification tier,
required fixtures, workflows, environment requirements, and compatibility
expectations.

See the [Manifest](../reference/manifest.md) reference for the expected shape.
