# Arazzo Spec Library

A curated, executable corpus of Arazzo workflow specifications.

This doc set is designed for the fullstack-starter docs engine. It is plain
Markdown plus a `_sidebar.json` manifest, so another project can register this
repository's `docs/` folder and render it without changing the corpus itself.

## Quick Navigation

- [Overview](getting-started/overview.md) - What this repository is for.
- [Repository Structure](corpus/repository-structure.md) - Where specs,
  fixtures, invalid cases, and docs live.
- [Adding Specs](corpus/adding-specs.md) - The acceptance bar for new entries.
- [Candidate APIs](corpus/candidate-apis.md) - Implemented domains and the next-wave queue.
- [NWS Public-Live Slice](corpus/nws.md) - The first repeatable public-live
  workflow pattern.
- [Socket.dev First Slice](corpus/socket-dev.md) - The first live-gated
  provider workflow pattern.
- [Verification Model](verification/model.md) - How specs should be checked.
- [Manifest](reference/manifest.md) - The machine-readable corpus contract.

## Rendering This Doc Set

In a fullstack-starter app, register a doc set with:

| Field | Value |
|-------|-------|
| ID | `arazzo-spec-library` |
| Title | `Arazzo Spec Library` |
| Content Path | Absolute path to this checkout's `docs/` folder |
| Merge Plugin Docs | `false` |

Relative content paths also work when the renderer is checked out next to this
repository, for example `../arazzo-spec-library/docs`.

## Current Status

The corpus has eleven workflows across NWS, Socket, GitHub, PyPI, Docker Hub,
Open Library, Crossref, crates.io and vSphere. The manifest records runnable entries and
their test scenarios; provider READMEs record live evidence and limitations.

- NWS address-to-forecast as the canonical public-live reference workflow.
- Socket.dev package-risk triage as the quota-sensitive authenticated workflow.
- GitHub, PyPI, Docker Hub and Crossref with bounded public read-only live proof.
- Open Library and crates.io with complete fixture execution but explicit
  identified-client/pacing gates before live use.
- [vSphere VM/guest diagnosis and cluster assessment](../specs/vsphere/README.md) with integrated session
  lifecycle and a configured private endpoint pickup path: **vSphere 8.0 U3
  contract-based; synthetic fixtures; live execution unverified.** Authentication
  creates/deletes a temporary session; no live vCenter access was used.
  Cluster assessment covers HA/DRS, the returned root pool's allocations and
  children, and cluster-filtered host/VM inventory. Configured totals do not
  establish utilization, storage/network backings or placement readiness.

Run `python3 scripts/verify.py` from the repository root for offline proof.
