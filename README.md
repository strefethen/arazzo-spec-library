# arazzo-spec-library

A curated, executable corpus of useful real-world Arazzo API workflows.

This repository exists to collect known-good Arazzo specs, reusable companion
fixtures, and deliberately invalid edge cases that can be validated by tooling.
It is intentionally separate from `arazzo-cli`: the CLI repository should stay
focused on runtime and product code, while this repository can grow as ecosystem
material, examples, conformance data, and documentation.

## Goals

- Build a high-quality library of Arazzo workflow specifications.
- Keep every accepted spec executable or at least machine-checkable.
- Provide examples that teach real workflow patterns instead of toy YAML only.
- Maintain a regression corpus that can be used by `arazzo-cli` and other Arazzo
  tools.
- Separate hermetic examples from live API examples so default checks never
  depend on external services.

## Non-Goals

- This is not a code generator repository.
- This is not a replacement for `arazzo-cli` examples or test fixtures.
- This is not a place for product-specific workflow logic that cannot be reused.
- This is not a dumping ground for unverified specs.

## Repository Layout

```text
.
├── fixtures/
│   ├── openapi/       # Companion OpenAPI documents used by specs.
│   └── responses/     # Static response fixtures for hermetic examples.
├── docs/              # Fullstack-starter-compatible Markdown doc set.
├── invalid/           # Specs that should fail validation for clear reasons.
├── manifest.yaml      # Machine-readable index of specs and verification tiers.
├── specs/             # Curated valid specs, grouped by provider or pattern.
└── views/             # Reusable jq projections for readable command output.
```

Add new top-level directories under `specs/` only when they represent a durable
provider, protocol pattern, or reusable workflow category.

## Canonical Quickstart

Run these commands from the repository root with `arazzo-cli` 0.8.2+ and jq
installed. The executable is named `arazzo-cli`, not `arazzo`.

`nws.address-forecast` is the canonical reference workflow. It starts from
Apple's corporate address, geocodes it, resolves the NWS gridpoint, fetches the
forecast, and checks active alerts.

```bash
set -o pipefail
arazzo-cli --json run specs/nws/address-forecast.arazzo.yaml address-forecast \
  --strict-inputs \
  --input address="One Apple Park Way, Cupertino, CA 95014" \
  --input user_agent="${NWS_USER_AGENT:-arazzo-spec-library-example}" \
| jq -er -f views/nws.address-forecast.summary.jq
```

Safe dry-run verification does not call external APIs:

```bash
set -o pipefail
arazzo-cli --json run specs/nws/address-forecast.arazzo.yaml address-forecast \
  --dry-run \
  --strict-inputs \
  --step geocode-address \
  --input address="One Apple Park Way, Cupertino, CA 95014" \
| jq -er -f views/nws.address-forecast.summary.jq
```

Dry-run prints planned requests, not weather. The first command makes live API
calls; observe the [NWS/Nominatim usage notes](specs/nws/README.md). This is not
an emergency alerting or life-safety system.

## Explore With An Agent

Point your agent at [AGENTS.md](AGENTS.md), then ask a concrete question:

- "Show me the forecast and active alerts for Apple Headquarters."
- "Inspect the latest release files for a Python package without installing it."
- "Show the image platforms and digests behind a public Docker tag."
- "Find a book and show which work matched and a few editions."

Discover available workflows and inspect one before running:

```bash
arazzo-cli --json catalog specs/nws
arazzo-cli --json show address-forecast --dir specs/nws
```

Use [manifest.yaml](manifest.yaml) for provider paths, workflow IDs, verification
scenarios and jq views. Each provider folder has a README with input/output
semantics, limits and runnable commands. The [candidate catalog](docs/corpus/candidate-apis.md)
keeps the original shortlist and next-wave prerequisites visible.
CLI 0.8.2 catalogs one provider directory at a time, not the entire nested tree.

## Offline Verification

Contributor tools: Python 3.10+, PyYAML 6.0.3, CLI 0.8.2+, jq. PyYAML is used
with `safe_load`; there is no custom YAML or Arazzo expression parser. Install
contributor dependencies before going offline, for example in a local venv.

```bash
python3 -m pip install --only-binary=:all: -r requirements-dev.txt
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/verify.py
python3 scripts/verify.py nws.address-forecast
```

The verifier validates/discovers every registered workflow, previews the first
step, and executes complete scenarios with the actual CLI against a strict
loopback server. It asserts requests, final outputs, errors, and jq summaries.
It never executes shell commands from the manifest or falls back to a live API.
See [the scenario contract](tests/README.md). Offline fixture proof is not a
claim of live provider compatibility. Socket receives **zero live test calls**.
The GitHub Actions workflow installs tools, then runs the same offline checks.

## Spec Acceptance Bar

A spec belongs here only when it has enough metadata and verification surface to
be useful to users and tools.

Each accepted spec should declare:

- A stable name and short description.
- The Arazzo version it targets.
- Required companion OpenAPI documents.
- Whether it is `hermetic`, `dry-run`, or `live`.
- Required environment variables, if any.
- The workflows that default verification should exercise.
- The tested `arazzo-cli` version or compatibility range.

Every accepted spec should pass the strongest practical verification tier:

- `hermetic`: validation, workflow listing, workflow details, and dry-run or test
  execution without network access.
- `dry-run`: validation, workflow listing, workflow details, and dry-run output.
- `live`: offline fixture checks by default; deliberate live execution observes
  provider policy and requires credentials only where the provider needs them.

Live specs must fail closed when credentials or required environment variables
are absent. Default CI must not call external APIs.

## Manifest

`manifest.yaml` is the source of truth for the corpus. Tooling should read the
manifest instead of discovering behavior from filenames alone.

Example entry:

```yaml
specs:
  - id: pypi.package-release
    path: specs/pypi/package-release.arazzo.yaml
    description: Resolve a project version and inspect its exact release metadata.
    arazzo: "1.0.x"
    tier: live
    openapi:
      - fixtures/openapi/pypi/json-api.yaml
    workflows:
      - package-release
    env: []
    tests: tests/scenarios/pypi.package-release.yaml
```

## Verification Model

`arazzo-cli` is the first verification engine for this corpus. The repository
should stay tool-agnostic in posture, but every practical claim in this library
should be checkable with CLI commands.

Typical checks for a single spec should look like:

```bash
arazzo-cli --json validate specs/pypi/package-release.arazzo.yaml
arazzo-cli --json list specs/pypi/package-release.arazzo.yaml
arazzo-cli --json show package-release --dir specs/pypi
arazzo-cli --json run specs/pypi/package-release.arazzo.yaml package-release --dry-run --strict-inputs --step resolve-project --input package=sampleproject
```

`python3 scripts/verify.py` drives these checks from the manifest and adds
end-to-end fixture execution. A spec must have meaningful offline proof before
being described as accepted; validation alone is insufficient.

## Contribution Rules

- Prefer small, reviewable additions: one provider or workflow family at a time.
- Include companion OpenAPI files or fixtures needed for local verification.
- Do not require network access for default checks.
- Label live examples clearly and gate them behind explicit environment
  variables.
- Add invalid examples only when the failure mode is intentional and documented.
- Keep examples generic enough to teach Arazzo behavior beyond a single private
  system.

## Relationship to arazzo-cli

`arazzo-cli` should keep only the examples and fixtures needed to test the tool
itself. This repository can grow more broadly:

- real provider examples
- conformance cases
- invalid specs
- reusable OpenAPI companions
- workflow pattern examples
- release compatibility checks across CLI versions

The two repositories should reinforce each other without becoming coupled. The
spec library can use `arazzo-cli` as its first verifier, and `arazzo-cli` can use
selected library cases as a broader compatibility signal when useful.

## Documentation

The `docs/` directory is a fullstack-starter-compatible doc set: plain Markdown,
`docs/index.md`, and `docs/_sidebar.json`. This repository does not need to host
the rendered site itself; another fullstack-starter app can register the docs
folder as a doc set and serve it.

Suggested doc set registration:

| Field | Value |
|-------|-------|
| ID | `arazzo-spec-library` |
| Title | `Arazzo Spec Library` |
| Content Path | Absolute path to this checkout's `docs/` folder |
| Merge Plugin Docs | `false` |
