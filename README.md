# arazzo-spec-library

[![Offline Corpus Verification](https://github.com/strefethen/arazzo-spec-library/actions/workflows/verify.yml/badge.svg)](https://github.com/strefethen/arazzo-spec-library/actions/workflows/verify.yml)

A curated, executable corpus of useful real-world Arazzo API workflows.

Run these specifications with **[arazzo-cli](https://github.com/strefethen/arazzo-cli)**,
the workflow executor, MCP server, and VS Code debugger. This repository owns
the reusable API workflows, local OpenAPI companions, response fixtures, and
readable output views; the CLI repository owns the execution engine and tooling.

## Available Workflows

The current corpus contains **11 workflows across 9 providers**. Every workflow
has complete offline fixture tests; that is separate from live-provider proof.

| Provider | Workflow | Live Use |
|---|---|---|
| [NWS](specs/nws/README.md) | Address -> coordinates -> grid -> forecast and all active alerts; coordinates-only alternative | Public APIs; canonical reference; observe geocoding policy |
| [GitHub](specs/github/README.md) | Public repository -> releases -> recent issues and PRs | Anonymous read-only; live smoke passed |
| [PyPI](specs/pypi/README.md) | Project -> exact release -> files, hashes, yanked flags, advisory metadata | Public read-only; live smoke passed; no package installation |
| [Docker Hub](specs/dockerhub/README.md) | Repository -> bounded tag page -> image platforms and digests | Public read-only; live smoke passed; no image pull |
| [Crossref](specs/crossref/README.md) | DOI -> depositing member -> bounded cursor page of related works | Public read-only; live smoke passed |
| [Open Library](specs/openlibrary/README.md) | Book search -> selected work -> bounded edition page | Fixture-tested; real contact identity and rate budget required before live use |
| [crates.io](specs/crates/README.md) | Crate -> registry default version -> features and direct dependency requirements | Fixture-tested; live use blocked until client request pacing is available |
| [Socket.dev](specs/socket/README.md) | Quota check -> organization-scoped PURL risk metadata | Manual approval and quota required; no live verification calls |
| [vSphere](specs/vsphere/README.md) | Login -> unique scoped VM -> configuration, Tools and guest diagnosis -> logout | vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified. Private endpoint/credentials required; session side effects |
| [vSphere](specs/vsphere/README.md#cluster-configuration-and-inventory-assessment) | Login -> unique scoped cluster -> HA/DRS, returned root pool allocations/children, scoped host/VM inventory -> logout | vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified. Configured allocations, not utilization or storage/network/placement proof; session side effects |

Provider READMEs document inputs, limits, copy-paste commands, and dated live
observations. Package metadata and an absence of advisory records are **not a
security verdict**.

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
├── .github/workflows/     # Offline corpus verification CI.
├── fixtures/
│   ├── openapi/           # Companion OpenAPI documents used by specs.
│   └── responses/         # Static response fixtures for offline verification.
├── docs/                  # Fullstack-starter-compatible Markdown doc set.
├── manifest.yaml          # Machine-readable index of specs and verification tiers.
├── requirements-dev.txt   # Pinned contributor dependency.
├── scripts/               # Manifest-driven verifier and loopback fixture server.
├── specs/                 # Curated valid specs, grouped by provider or pattern.
├── tests/                 # Request/output scenarios and verifier regression tests.
└── views/                 # Reusable jq projections for readable command output.
```

Add new top-level directories under `specs/` only when they represent a durable
provider, protocol pattern, or reusable workflow category.

## Canonical Quickstart

Install [arazzo-cli](https://github.com/strefethen/arazzo-cli#quick-start) or use
its [release binaries](https://github.com/strefethen/arazzo-cli/releases), and
install jq. Ensure the executable is on your `PATH` as `arazzo-cli`, not
`arazzo`. This corpus and CI are currently verified with CLI **0.8.2**.

```bash
git clone https://github.com/strefethen/arazzo-spec-library.git
cd arazzo-spec-library
arazzo-cli --version
jq --version
```

Run all commands below from this repository's root so the spec and view paths
resolve consistently. Python is only needed for contributor verification, not
for running live workflows.

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
- "Preview the book-to-editions workflow and explain its live-use prerequisites."

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
python3 -m venv .venv
source .venv/bin/activate
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
The current baseline is **216 passing workflow scenarios and 58 verifier unit
tests**. See [CI results](https://github.com/strefethen/arazzo-spec-library/actions/workflows/verify.yml)
for the latest run. Dependency installation uses the network; the checks
themselves do not call live provider APIs.

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
are absent. Default verification must not call live provider APIs.

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
- Label live examples clearly, document provider policy, and gate credentials
  or quota-sensitive operations explicitly. Public read-only examples need no
  API token unless their provider requires one.
- Add invalid examples only when the failure mode is intentional and documented.
- Keep examples generic enough to teach Arazzo behavior beyond a single private
  system.

## Relationship to arazzo-cli

[arazzo-cli](https://github.com/strefethen/arazzo-cli) provides validation,
execution, tracing/replay, MCP integration, and a
[VS Code debugger](https://github.com/strefethen/arazzo-cli#vs-code-debugger).
Its own examples and fixtures test that tool. This library can grow more broadly:

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
