# vSphere diagnostic reports

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**
No real vCenter has verified authentication, TLS trust, privileges, response
compatibility or operational usefulness. Synthetic tests prove request wiring
and declared failures only. `vm-guest-diagnosis` correlates one uniquely scoped
VM's configured hardware with Tools and all documented guest telemetry. It
creates a temporary session, reads inventory/guest information, then deletes
the session. `cluster-infrastructure-assessment` combines cluster configuration,
root-pool allocations and cluster-filtered host/VM inventory. Both reports
perform inventory reads plus session creation/deletion. OVF preparation remains
a separate future slice.

## VM selection and report

Provide an exact datacenter name and an exact VM name. The workflow requires
exactly one visible datacenter match, then exactly one VM match filtered by
that returned datacenter ID and VM name. Zero or multiple matches, object-shaped
responses, missing IDs and mismatched names fail before the next work request.
Uniqueness is relative to the account's visible inventory, not proof of global
uniqueness. Datacenter and VM result caps (1000 and 4000 respectively) are hard
provider limits, not pagination; a provider limit error fails the run.

The fixed sequence is login → datacenter → scoped VM → VM configuration →
Tools → guest identity → guest networking → ordered interfaces → routes →
local filesystems → logout. Every work operation must succeed. HTTP 503 for
Tools/guest data is an error, including unavailable or not-yet-reported data.
There is no partial/degraded report or automatic retry.

Raw outputs retain selected identities and full configuration, Tools, guest
identity/networking, interfaces, routes and filesystem structures. Configuration
uses `guest_OS`, `memory.size_MiB`, and device-ID-keyed `nics`/`disks` maps;
the VM list instead uses `memory_size_MiB`. The jq summary links guest `nic`
IDs to configured NICs, route `interface_index` to the ordered interfaces array,
and filesystem `mappings[].disk` to configured disks. It does not guess missing
mappings or assume one filesystem per disk. Unknown optional fields remain
absent in raw structures and display as unknown; empty reported collections
remain empty. Virtual disk allocation, guest filesystem capacity/free space and
CPU/memory configuration measure different things. None establishes runtime
utilization, storage backing accessibility or deployment capacity.

## Endpoint configuration

Run from the repository root with Python 3.10+ and PyYAML 6.0.3 installed.
Create a new local bundle:

```bash
python3 scripts/configure_vsphere.py \
  --server https://vcenter.example.invalid \
  --output-dir .artifacts/vsphere-configured
```

Use your deployment's HTTPS origin and optional port. Userinfo, URL paths
(except a root slash), queries, fragments and placeholders are rejected.
The `.invalid` value above is deliberately unusable. Replace it with an origin
you are authorized to inspect before a deliberate live run.

The helper reads only registered vSphere specifications and their registered
local companions. It preserves repository-relative layout, copies Arazzo
source bytes, changes only top-level OpenAPI server URLs, and emits JSON
`specs` records containing manifest `id` and configured `path`. It does not
execute workflows, contact any server, take credentials, disable TLS checks,
or modify tracked sources. Output must be a new directory beneath the ignored
repository `.artifacts/` directory. Existing files/directories, symlinks,
parent traversal, remote or escaping sources, external references, and
path/operation server overrides are rejected. Choose a fresh output path to
regenerate; existing output is never overwritten. Do not commit generated
endpoint bundles. Unregistered neighboring files are not copied.

## Credentials, TLS and invocation boundary

The shared [session contract](../../fixtures/openapi/vsphere/session.yaml)
targets the versioned official [session creation](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/cis/api/session/post/)
and [session deletion](https://developer.broadcom.com/xapis/vsphere-automation-api/8.0.3/cis/api/session/delete/)
operations. POST `/api/session` uses HTTP Basic and returns HTTP 201 with a
JSON string. Later operations, including DELETE `/api/session`, use
`vmware-api-session-id`; deletion returns HTTP 204 without a body. These
authentication side effects create and delete temporary sessions.

Construct the complete `Basic ...` header locally with Python's hidden terminal
prompts. Run this in your own interactive Bash/zsh terminal, with shell tracing
disabled. The header is captured directly into the environment; neither the
username/password nor the completed header is entered into history or command
arguments. This documentation/test work uses only synthetic credentials; do not
provide real credentials to an agent.

```bash
set +x
VSPHERE_AUTHORIZATION="$(python3 -c '
import base64, getpass
user = getpass.getpass("vCenter username (hidden): ")
password = getpass.getpass("vCenter password (hidden): ")
if not user or ":" in user or not password:
    raise SystemExit("Nonempty username without colon and password required")
print("Basic " + base64.b64encode((user + ":" + password).encode("utf-8")).decode("ascii"))
')"
export VSPHERE_AUTHORIZATION
: "${VSPHERE_AUTHORIZATION:?VSPHERE_AUTHORIZATION must contain a complete Basic header}"
```

Base64 is not encryption. Never echo the variable, enable shell tracing, or put
credentials in URLs, files, workflow outputs or Git. Environment variables are
accessible to processes with appropriate local privileges. Before **each**
authenticated invocation, keep the missing-value guard:

```bash
: "${VSPHERE_AUTHORIZATION:?VSPHERE_AUTHORIZATION must contain a complete Basic header}"
```

Workflow commands must pass the complete env reference as the
single-quoted argument `--input 'authorization=${VSPHERE_AUTHORIZATION}'`.
This lets CLI environment expansion resolve the value without putting the
expanded secret in the command arguments. Do not configure a global
Authorization header: Basic belongs only on login. The intermediate token
is named `session_token` and must never appear in final outputs.

Every authenticated invocation must use `--strict-inputs --max-redirects 0`.
CLI 0.8.2 does not reliably strip the session header on cross-host redirects;
a redirect must fail without contacting its target. Do not enable trace
capture: traces can include the scalar session response. Do not use live
single-step commands, which can skip logout. Preview uses synthetic input only.

Use trusted HTTPS with hostname validation. CLI 0.8.2 has no custom-CA option
or runtime server override. The configuration helper solves endpoint selection
only. It does not install a CA or repair certificate trust. An operator who
explicitly chooses `--insecure-host <hostname>` disables certificate verification
for that host; this is not a trust-store fix and is outside normal pickup.
Do not silently weaken TLS. Have the vCenter administrator confirm account
permissions for this workflow's datacenter/VM inventory, VM configuration,
Tools and guest-information APIs (including System.Read where required);
successful authentication alone does not establish sufficient privileges.

## Discover, preview and full execution

Use CLI 0.8.2 and jq from the repository root. Discovery and preview need no
credentials and make no vCenter calls:

```bash
arazzo-cli --json catalog specs/vsphere
arazzo-cli --json show vm-guest-diagnosis --dir specs/vsphere
arazzo-cli --json validate .artifacts/vsphere-configured/specs/vsphere/vm-guest-diagnosis.arazzo.yaml --strict
arazzo-cli --json run .artifacts/vsphere-configured/specs/vsphere/vm-guest-diagnosis.arazzo.yaml vm-guest-diagnosis \
  --dry-run --strict-inputs --max-redirects 0 --step login \
  --input authorization=synthetic-preview \
  --input datacenter_name='Lab DC' --input vm_name=app-01
```

Preview prints only the first login request plan. It does not resolve the VM,
retrieve telemetry, authenticate, or prove trust/permissions.

After configuring a real origin, privately setting the header, and obtaining
permission to inspect that deployment, execute the **whole** workflow. Change
the two nonsecret names to the account-visible exact names. This command
captures raw agent-readable JSON in an ignored local artifact and prints the
summary only after the CLI succeeds:

```bash
set -o pipefail
umask 077
: "${VSPHERE_AUTHORIZATION:?VSPHERE_AUTHORIZATION must contain a complete Basic header}"
arazzo-cli --json run .artifacts/vsphere-configured/specs/vsphere/vm-guest-diagnosis.arazzo.yaml vm-guest-diagnosis \
  --strict-inputs --max-redirects 0 \
  --input 'authorization=${VSPHERE_AUTHORIZATION}' \
  --input datacenter_name='Lab DC' --input vm_name=app-01 \
  > .artifacts/vsphere-vm-diagnosis.json && \
  jq -er -f views/vsphere.vm-guest-diagnosis.summary.jq .artifacts/vsphere-vm-diagnosis.json
```

Agents consume `.artifacts/vsphere-vm-diagnosis.json` directly; the jq view is
presentation, not alternate selection logic. It refuses an error envelope.
For an approved export, add `--export-run .artifacts/vsphere-vm-run.json` to the
same full invocation. Synthetic tests check stdout, stderr and this export
surface for both Basic and session sentinels. This is not a guarantee of general
secret redaction for arbitrary provider bodies. Inventory/guest data can itself
be sensitive; inspect before sharing. Do not add `--trace` or `--verbose` to the
normal command. Clear credentials after use:

```bash
unset VSPHERE_AUTHORIZATION
```

## Failure and cleanup limits

The workflow ends explicitly on login failure, preventing an
unexpected token-shaped response from appearing in ordinary error previews.
After successful login, ordinary request failures attempt a separate logout
path that still ends nonzero. Success also requires logout. The CLI has no
established guaranteed finally/rethrow mechanism: cleanup can replace the
original top-level error, and cancellation or whole-workflow timeout can skip
logout. A logout failure is a failure, not a successful partial report.

If a run fails, inspect the nonsecret status/code and configured origin, then
check TLS, account permissions and API-version compatibility with the
administrator. Avoid sharing raw output until checked for secrets; no general
redaction guarantee exists. If cleanup was skipped or failed, use your
administrator's approved session revocation process or session-expiry policy.
Never rerun login steps alone to diagnose a live session. Inventory reads and
OVF requirement inspection do not authorize provisioning, EULA acceptance or
infrastructure changes. See the [contract assessment](../../plans/assessments/vsphere-contracts-2026-10-27.md)
for the research and evidence boundary.

## Sources and offline proof

The local [VM/guest OpenAPI subset](../../fixtures/openapi/vsphere/vm-guest-diagnosis.yaml)
links each operation to the exact official 8.0.3 page. The
[fixture provenance](../../fixtures/responses/vsphere/README.md) records wire
shapes and the pinned SDK source used to disambiguate filesystem maps and
optional fields. Subset schemas and runtime shape/identity guards do not claim
full JSON Schema response validation.

```bash
python3 scripts/verify.py vsphere.vm-guest-diagnosis
python3 -m unittest discover -s tests -p 'test_vsphere_auth.py'
```

No live compatibility is established by those commands. A real deployment still
needs to confirm TLS, Basic authentication, least-privilege account access,
version/response compatibility and usefulness of its reported telemetry.

## Cluster configuration and inventory assessment

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**
The approved documented scope is configuration/HA/DRS, the returned root resource
pool's allocations and child IDs, and cluster-filtered host/VM inventory. This
workflow does not call ConfigTargets or negotiate a release, substitute
datacenter-wide resources, inspect storage/network backings, map VMs to hosts,
or establish utilization, available capacity or placement readiness.

Provide exact `datacenter_name` and `cluster_name` strings. The chain is login →
unique visible named datacenter → unique cluster filtered by that datacenter ID
and name → cluster detail → the returned root resource pool → hosts filtered by
the selected cluster ID → VMs filtered by the same cluster ID → logout. The
cluster detail name must agree with selection. Neither cluster get nor pool get
supplies a mandatory ID in its response; `selected_cluster.cluster` and
`resource_pool_id` preserve the identities used in the requests. Child pool IDs
are reported without recursive reads. The exact fixture request path proves
the returned pool is followed, including a different synthetic root-pool ID.
There is no separate pool response-ID comparison or invented name constraint.

Datacenter/cluster list limits are 1000 each, host lists 2500, and VM lists 4000.
These are hard provider failure caps, not pagination. No whole-estate query or
automatic retry follows a limit error. All lists are account-visible inventory;
the two scoped lists are separate reads, not an atomic snapshot. Normal commands
below explicitly bound each response to 10 MiB, each HTTP request to 30 seconds
and the whole run to 5 minutes. A response-size or workflow-timeout failure is
not a partial report; whole-run timeout can skip cleanup.

Raw output includes datacenter and cluster selection, full cluster detail,
requested pool identity, complete pool data and every field of every host/VM
entry. Root `resource_pools`, hosts and VMs are required arrays; an empty array
is valid, while a missing/null/object-shaped array fails. Runtime guards check
every inventory entry, including later entries, before the next work request;
malformed entries route to failure logout. Required names/IDs/states and
booleans must have their documented types/values. Optional host `power_state`,
VM `cpu_count`/`memory_size_MiB`, pool allocations and shares counts remain absent
when not reported. Present allocation objects need their required fields;
malformed/null optional data fails rather than becoming a default value.
These guards are a scoped response check, not complete JSON Schema validation.

The jq report shows HA/DRS, pool reservation/limit/expandability/shares, child
pool IDs, per-host states, per-VM state/configuration, state counts and configured
CPU and memory sums. VM memory is **MiB**; resource-pool memory reservation/limit
uses the provider's **MB** wording, and pool CPU uses **MHz**. A limit of `-1`
means unlimited; shares are relative and their count is relevant only for
`CUSTOM`. Missing allocation objects display as unknown. VM totals show the
known subtotal and how many VMs supplied each field; any omitted value makes
the full total unknown. Empty inventories have complete zero configured totals.
None of these configured allocations measures utilization.

Use the shared endpoint helper, credential setup and TLS/cleanup guidance
above. The helper includes both registered vSphere workflows; if an older bundle
exists, choose a new output directory. Have the administrator confirm privileges
for datacenter/cluster lists, cluster and resource-pool get, and scoped host/VM
lists, including `System.Read` where required. Login alone proves no read access.
Discovery, strict validation and first-login preview make no vCenter calls:

```bash
python3 scripts/configure_vsphere.py \
  --server https://vcenter.example.invalid \
  --output-dir .artifacts/vsphere-cluster-configured
arazzo-cli --json catalog specs/vsphere
arazzo-cli --json show cluster-infrastructure-assessment --dir specs/vsphere
arazzo-cli --json validate .artifacts/vsphere-cluster-configured/specs/vsphere/cluster-infrastructure-assessment.arazzo.yaml --strict
arazzo-cli --json run .artifacts/vsphere-cluster-configured/specs/vsphere/cluster-infrastructure-assessment.arazzo.yaml cluster-infrastructure-assessment \
  --dry-run --strict-inputs --max-redirects 0 --step login \
  --input authorization=synthetic-preview \
  --input datacenter_name='Lab DC' --input cluster_name='Compute A'
```

The preview prints only a login plan: no cluster, pool or inventory results.
After choosing an authorized real HTTPS origin and privately setting
`VSPHERE_AUTHORIZATION` using the hidden-prompt setup above, run the whole chain:

```bash
set -o pipefail
umask 077
: "${VSPHERE_AUTHORIZATION:?VSPHERE_AUTHORIZATION must contain a complete Basic header}"
arazzo-cli --json run .artifacts/vsphere-cluster-configured/specs/vsphere/cluster-infrastructure-assessment.arazzo.yaml cluster-infrastructure-assessment \
  --strict-inputs --max-redirects 0 \
  --http-timeout 30s --execution-timeout 5m --max-response-size 10485760 \
  --input 'authorization=${VSPHERE_AUTHORIZATION}' \
  --input datacenter_name='Lab DC' --input cluster_name='Compute A' \
  > .artifacts/vsphere-cluster-assessment.json && \
  jq -er -f views/vsphere.cluster-infrastructure-assessment.summary.jq .artifacts/vsphere-cluster-assessment.json
unset VSPHERE_AUTHORIZATION
```

Agents use `.artifacts/vsphere-cluster-assessment.json` as raw data; jq only
presents it and rejects error envelopes. Never use live `--step`, traces,
verbose output, global Basic headers or redirects. Ordinary failures after
login attempt the separate failure logout and remain nonzero; successful work
also requires successful logout. Cancellation/whole-run timeout can skip
cleanup, and cleanup replaces the original top-level error. Use the approved
administrator session-revocation/expiry process if cleanup fails or is skipped.
No real credentials or live calls were used in this implementation.

Inspect the full raw outputs separately without losing optional omissions:

```bash
jq -e '.outputs' .artifacts/vsphere-cluster-assessment.json
```

The [cluster OpenAPI subset](../../fixtures/openapi/vsphere/cluster-infrastructure-assessment.yaml)
links the exact official 8.0.3 operation pages. The
[fixture provenance](../../fixtures/responses/vsphere/README.md) links the
required/optional field definitions. Run its complete synthetic scenarios with:

```bash
python3 scripts/verify.py vsphere.cluster-infrastructure-assessment
```
