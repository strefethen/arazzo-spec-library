# NWS Public-Live Slice

The National Weather Service API is the first repeatable public-live provider in
the corpus. It does not require an API token. The canonical workflow uses
Nominatim for address geocoding and NWS for point, forecast, and alert data.
Both services should receive a descriptive `User-Agent`, so live commands should
override the default with `NWS_USER_AGENT`.

## Workflow

`nws.address-forecast` lives at `specs/nws/address-forecast.arazzo.yaml`.
This is the canonical reference case for the corpus.

It models a small real-world chain from Apple's corporate address:

1. Geocode the address with Nominatim.
2. Resolve the returned latitude/longitude with
   `GET /points/{latitude},{longitude}`.
3. Use the returned office and gridpoint to fetch
   `GET /gridpoints/{wfo}/{x},{y}/forecast`.
4. Check active alerts for the geocoded point with `GET /alerts/active`.

The workflow accepts:

| Input | Purpose |
|-------|---------|
| `address` | One-line US street address. |
| `user_agent` | Optional descriptive NWS User-Agent. Defaults to `arazzo-spec-library-example`; override with `NWS_USER_AGENT` for live use. |

## Files

| Path | Purpose |
|------|---------|
| `specs/nws/README.md` | Provider-local quickstart and safe command set. |
| `specs/nws/address-forecast.arazzo.yaml` | Canonical address-to-forecast workflow. |
| `specs/nws/point-forecast-alerts.arazzo.yaml` | Lower-level latitude/longitude workflow. |
| `fixtures/openapi/nominatim/search.yaml` | Local OpenAPI subset for address geocoding. |
| `fixtures/openapi/nws/weather-api.yaml` | Local OpenAPI subset for exercised endpoints. |
| `fixtures/responses/nws/address-forecast/` | Canonical example response envelopes. |
| `views/nws.address-forecast.summary.jq` | Readable jq projection for run output. |

## Verification

Default verification executes the full chain against loopback fixtures with
`python3 scripts/verify.py nws.address-forecast`. For a request preview, dry-run
the geocoding step because later NWS URLs depend on response outputs:

```bash
arazzo-cli --json validate specs/nws/address-forecast.arazzo.yaml
arazzo-cli --json list specs/nws/address-forecast.arazzo.yaml
arazzo-cli --json show address-forecast --dir specs/nws
arazzo-cli --json run specs/nws/address-forecast.arazzo.yaml address-forecast --dry-run --strict-inputs --step geocode-address --input address="One Apple Park Way, Cupertino, CA 95014"
```

Live execution is intentionally explicit:

```bash
arazzo-cli --json run specs/nws/address-forecast.arazzo.yaml address-forecast --strict-inputs --input address="One Apple Park Way, Cupertino, CA 95014" --input user_agent="${NWS_USER_AGENT:-arazzo-spec-library-example}"
```

For readable output, pipe the JSON through the bundled jq view:

```bash
set -o pipefail
arazzo-cli --json run specs/nws/address-forecast.arazzo.yaml address-forecast \
  --strict-inputs \
  --input address="One Apple Park Way, Cupertino, CA 95014" \
  --input user_agent="${NWS_USER_AGENT:-arazzo-spec-library-example}" \
| jq -er -f views/nws.address-forecast.summary.jq
```

Do not loop public-live checks aggressively. Nominatim's public service has
limited capacity and requires a descriptive User-Agent, attribution, and no heavy
use. NWS alert checks should also not be run in tight loops.

The public weather input is the address. The workflow exposes the geocoded
coordinates and resolved NWS gridpoint as outputs so callers can inspect each
intermediate decision.
