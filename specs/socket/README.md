# Socket.dev Package Risk Triage

**Manual-live, quota-sensitive. Do not run this workflow without explicit
approval of its quota cost.** Normal verification uses only synthetic fixtures.

The flow checks remaining token quota, requires at least 100 units, then
performs one organization-scoped PURL lookup with alerts and a summary. Results
include raw package records and summary metadata; HTTP 200 is not a security
verdict. `poll=false` returns currently known information and can include
pending-scan/not-found alerts. Missing analysis must never be called safe.

Offline proof, with no token or quota consumption:

```bash
python3 scripts/verify.py socket.package-risk-triage
```

Only after approval, from the repo root:

```bash
set -o pipefail
arazzo-cli --json run specs/socket/package-risk-triage.arazzo.yaml package-risk-triage \
  --strict-inputs \
  --input socket_token="${SOCKET_TOKEN:?SOCKET_TOKEN is required}" \
  --input org_slug="${SOCKET_ORG_SLUG:?SOCKET_ORG_SLUG is required}" \
  --input purl=pkg:npm/express@4.19.2 \
| jq -er -f views/socket.package-risk-triage.summary.jq
```

The token needs `packages:list` permission. Be aware that CLI input flags can
appear in local process listings; use only a dedicated, narrowly scoped token.
Do not add credentials to files, traces, screenshots or Git. The quota check is
not a reservation: concurrent token users can spend it before the lookup.

Sources: [quota endpoint](https://docs.socket.dev/reference/getquota),
[organization PURL lookup](https://docs.socket.dev/reference/batchpackagefetchbyorg),
[PURL options and pending-analysis semantics](https://docs.socket.dev/reference/batchpackagefetch).
The documented lookup cost is 100 units, quota reads cost zero; recheck provider
terms before a manual run. No live Socket proof was attempted for this wave.
