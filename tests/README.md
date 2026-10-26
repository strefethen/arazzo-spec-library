# Corpus Scenarios

Run `python3 scripts/verify.py` with Python 3.10+, PyYAML 6.0.3,
`arazzo-cli` 0.8.2+, and jq installed. Verification never calls live providers.
The CLI itself evaluates all Arazzo expressions; this harness is only HTTP
transport plus assertions. Synthetic responses are contract-shaped examples,
not live captures or evidence of current provider behavior.

Every manifest entry names one scenario file in `tests`. Its format is:

```yaml
cases:
  - name: resolved-version
    workflow: package-release
    inputs: {package: sampleproject}
    requests:
      - method: GET
        path: /pypi/sampleproject/json
        query: {}
        headers: {accept: application/json}
        response:
          status: 200
          fixture: fixtures/responses/pypi/package-release/project.json
      - method: GET
        path: /pypi/sampleproject/4.0.0/json
        query: {}
        response:
          status: 200
          body: {info: {name: sampleproject, version: 4.0.0}, urls: []}
    expect:
      kind: success
      outputs: {package: sampleproject, version: 4.0.0}
```

`response` has exactly one of `fixture` (repository-relative JSON body) or
`body` (inline JSON-compatible value). `headers` asserts a case-insensitive
subset; query parameters and JSON request `body` are exact, not subsets.
Absent request `body` requires an empty HTTP request body. Every expectation
must be consumed in order. Unexpected HTTP methods, paths, requests, redirects,
and missing expectations fail the case.

`expect.kind: error` also requires a specific CLI `code`, such as
`RUNTIME_SUCCESS_CRITERIA_FAILED`. Successful scenarios require an `outputs`
subset assertion; arrays in that subset compare exactly. Optional `assert`
is a jq boolean expression evaluated against the CLI envelope, for collection
invariants. Optional `view_contains` lists strings required in the jq summary.
All paths are repository-relative and must stay inside the repository.

Only local `sourceDescriptions` are supported. Temporary copies rebase OpenAPI
server URLs to a loopback fixture server; the original specifications are never
edited. Remote sources, operation-level server overrides, URL-based targets,
and unregistered source files fail preflight rather than reaching live services.
