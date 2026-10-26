# Adding Specs

Add specs in small, reviewable units: one provider, one protocol pattern, or one
workflow family at a time.

## Acceptance Bar

A new spec should include:

- A stable manifest `id`.
- A short description.
- The targeted Arazzo version.
- Required companion OpenAPI documents.
- A verification tier.
- The workflows default checks should exercise.
- Required environment variables, if any.
- Clear notes when live execution is possible but not part of default checks.
- A provider README and jq view producing concise, actionable results.
- A `tests` scenario file covering the complete happy path and a meaningful
  failure or empty-result path, with exact inter-step request assertions.
- Official provider sources, collection bounds, authentication/quota policy,
  and honest distinction between synthetic fixture and live proof.

## File Placement

Place valid specs under `specs/<category>/`.

Place companion OpenAPI documents under `fixtures/openapi/`.

Place static response fixtures under `fixtures/responses/`.

Place deliberately invalid specs under `invalid/`.

## Default-Safe First

Prefer hermetic or dry-run examples before live examples. A user should be able
to clone the repository and run default checks without credentials, network
access, or private services.

Live specs are allowed when useful, but they must be explicitly labeled and
gated behind environment variables.

Public read-only providers need no credentials, but running them is still an
explicit live action. Default checks never call any provider. Authenticated
writes, paid/quota-consuming calls, and cleanup policies need user approval.

Use `arazzo-cli --json` and `--strict-inputs`; use `--input-json` for numeric
inputs. Runtime expressions use explicit JSON Pointers (`$response.body#/...`).
Source descriptions point to local companion OpenAPI documents, and targets use
qualified operation IDs. Do not copy historical non-conformant syntax.

Run `python3 scripts/verify.py <manifest-id>` and the verifier unit suite before
acceptance. See [scenario format](../../tests/README.md). An HTTP 200 alone is
not a useful success criterion if required data is absent. Never call missing
vulnerability information a clean bill of health.

## Documentation

When a spec teaches a new pattern, add or update docs explaining:

- the workflow shape
- the required fixtures
- the verification commands
- the reason the example belongs in the corpus
