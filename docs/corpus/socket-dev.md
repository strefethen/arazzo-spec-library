# Socket.dev First Slice

Socket.dev is the first live-gated provider in the corpus. It establishes the
pattern for APIs that are useful only with credentials, but still need
default-safe validation and dry-run coverage.

## Workflow

`socket.package-risk-triage` lives at
`specs/socket/package-risk-triage.arazzo.yaml`.

It models a small but real supply-chain triage flow:

1. Check Socket API quota with `GET /quota`.
2. Fetch package metadata and alert summaries with
   `POST /orgs/{org_slug}/purl`.
3. Return quota, lookup status, raw package records and summary metadata.

The workflow accepts:

| Input | Purpose |
|-------|---------|
| `socket_token` | Socket API token, normally passed from `SOCKET_TOKEN`. |
| `org_slug` | Socket organization slug, normally passed from `SOCKET_ORG_SLUG`. |
| `purl` | Package URL to triage, such as `pkg:npm/express@4.19.2`. |

## Files

| Path | Purpose |
|------|---------|
| `specs/socket/package-risk-triage.arazzo.yaml` | Arazzo workflow. |
| `fixtures/openapi/socket/socket-api.yaml` | Local OpenAPI subset for exercised endpoints. |
| `fixtures/responses/socket/package-risk-triage/` | Example response envelopes for docs and future replay fixtures. |

## Verification

Default verification must not call Socket. Use dry-run with placeholder values:

```bash
arazzo-cli --json validate specs/socket/package-risk-triage.arazzo.yaml
arazzo-cli --json list specs/socket/package-risk-triage.arazzo.yaml
arazzo-cli --json show package-risk-triage --dir specs/socket
arazzo-cli --json run specs/socket/package-risk-triage.arazzo.yaml package-risk-triage --dry-run --strict-inputs --input socket_token=redacted --input org_slug=example-org --input purl=pkg:npm/express@4.19.2
```

Live execution is quota-sensitive and explicitly gated:

```bash
arazzo-cli --json run specs/socket/package-risk-triage.arazzo.yaml package-risk-triage --strict-inputs --input socket_token="${SOCKET_TOKEN:?SOCKET_TOKEN is required}" --input org_slug="${SOCKET_ORG_SLUG:?SOCKET_ORG_SLUG is required}" --input purl=pkg:npm/express@4.19.2
```

Do not run the live workflow repeatedly on free Socket accounts. Keep normal
verification on dry-run and use captured fixtures or replay traces for
regression checks.

The full offline scenarios now run with `python3 scripts/verify.py
socket.package-risk-triage`. They prove low quota and rejected authentication
stop before the PURL request. See the [provider README](../../specs/socket/README.md)
for the readable jq view, permissions, pending-analysis semantics and current
quota references. No live Socket calls are part of verification.

## Adoption Pattern

Use this slice as the template for future provider specs:

- Keep the first workflow small enough to audit manually.
- Use a repository-local OpenAPI subset for the endpoints actually exercised.
- Include sample responses even when default checks use dry-run only.
- Declare live environment variables in `manifest.yaml`.
- Document the dry-run command beside the live command.
