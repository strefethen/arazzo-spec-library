# Overview

`arazzo-spec-library` is a curated collection of Arazzo workflow specifications
plus the fixtures and metadata needed to verify them.

The goal is not to collect every possible YAML file. The goal is to collect
specs that are useful to users, examples, test suites, and other Arazzo tooling.

## What Belongs Here

- Valid Arazzo specs that demonstrate reusable workflow patterns.
- Provider-oriented examples such as GitHub, Stripe, or other public APIs.
- Protocol-oriented examples such as OAuth, pagination, polling, retries, or
  multi-step CRUD.
- Hermetic examples backed by local OpenAPI and response fixtures.
- Invalid examples that document a specific validation failure.

## What Does Not Belong Here

- Unverified specs.
- Private product workflows that cannot teach a reusable pattern.
- Specs that require network access during default checks.
- Examples that only work with undocumented local state.

## Design Principle

Every accepted spec should be executable or machine-checkable. If a future
reader cannot validate, list, inspect, or dry-run the spec from the repository,
the example is not ready for the corpus.
