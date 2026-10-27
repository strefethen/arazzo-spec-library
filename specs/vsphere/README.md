# vSphere workflow foundation

**vSphere 8.0 U3 contract-based; synthetic fixtures; live execution unverified.**
No real vCenter has verified authentication, TLS trust, privileges, response
compatibility or operational usefulness. Synthetic tests prove request wiring
and declared failures only. This slice supplies shared session contracts and
endpoint configuration. No vSphere workflows are registered yet; VM diagnosis,
cluster assessment and OVF preparation commands will arrive with their slices.
Do not interpret this foundation as a runnable diagnostic workflow.

## Endpoint configuration

Run from the repository root with Python 3.10+ and PyYAML 6.0.3 installed.
Once vSphere workflows are registered, create a new local bundle:

```bash
python3 scripts/configure_vsphere.py \
  --server https://vcenter.example.invalid \
  --output-dir .artifacts/vsphere-configured
```

Use your deployment's HTTPS origin and optional port. Userinfo, URL paths
(except a root slash), queries, fragments and placeholders are rejected.
The `.invalid` value above is deliberately unusable. The helper currently
fails without creating a bundle because no vSphere workflows are registered.

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

Obtain the complete `Basic ...` Authorization value through your normal
private credential process and export it as `VSPHERE_AUTHORIZATION`. Base64
is not encryption. Never place credentials in endpoint URLs, files, workflow
outputs, shell history or Git. Before a future authenticated invocation, use
the shell missing-value guard:

```bash
: "${VSPHERE_AUTHORIZATION:?VSPHERE_AUTHORIZATION must contain a complete Basic header}"
```

Future workflow commands must pass the complete env reference as the
single-quoted argument `--input 'authorization=${VSPHERE_AUTHORIZATION}'`.
This lets CLI environment expansion resolve the value without putting the
expanded secret in the command arguments. Do not configure a global
Authorization header: Basic belongs only on login. The intermediate token
is named `session_token` and must never appear in final outputs.

Every authenticated invocation must use `--strict-inputs --max-redirects 0`.
CLI 0.8.2 does not reliably strip the session header on cross-host redirects;
a redirect must fail without contacting its target. Do not enable trace
capture: traces can include the scalar session response. Do not use live
single-step commands, which can skip logout. There is intentionally no live
run command in this foundation guide.

Use trusted HTTPS with hostname validation. CLI 0.8.2 has no custom-CA option
or runtime server override. The configuration helper solves endpoint selection
only. It does not install a CA or repair certificate trust. An operator who
explicitly chooses `--insecure-host <hostname>` disables certificate verification
for that host; this is not a trust-store fix and is outside normal pickup.
Do not silently weaken TLS. Have the vCenter administrator confirm account
permissions for each eventual workflow's scoped inventory and guest APIs;
successful authentication alone does not establish sufficient privileges.

## Failure and cleanup limits

The workflow slices must end explicitly on login failure, preventing an
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
