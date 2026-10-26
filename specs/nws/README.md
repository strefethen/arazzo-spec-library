# NWS Workflows

This directory contains public-live National Weather Service workflows. Run
commands from the repository root so paths resolve consistently.

## Canonical Reference

`address-forecast.arazzo.yaml` is the canonical reference workflow for the
corpus. It starts with Apple's corporate address, geocodes it with Nominatim,
resolves the NWS gridpoint, fetches the forecast, and checks active alerts.

```bash
set -o pipefail
arazzo-cli --json run specs/nws/address-forecast.arazzo.yaml address-forecast \
  --strict-inputs \
  --input address="One Apple Park Way, Cupertino, CA 95014" \
  --input user_agent="${NWS_USER_AGENT:-arazzo-spec-library-example}" \
| jq -er -f views/nws.address-forecast.summary.jq
```

## Default-Safe Checks

These checks do not call live APIs:

```bash
arazzo-cli --json validate specs/nws/address-forecast.arazzo.yaml
arazzo-cli --json list specs/nws/address-forecast.arazzo.yaml
arazzo-cli --json show address-forecast --dir specs/nws
arazzo-cli --json run specs/nws/address-forecast.arazzo.yaml address-forecast --dry-run --strict-inputs --step geocode-address --input address="One Apple Park Way, Cupertino, CA 95014"
```

## Files

| Path | Purpose |
|------|---------|
| `address-forecast.arazzo.yaml` | Address-to-forecast canonical reference. |
| `point-forecast-alerts.arazzo.yaml` | Lower-level latitude/longitude forecast flow. |
| `../../fixtures/openapi/nominatim/search.yaml` | Companion geocoder OpenAPI subset. |
| `../../fixtures/openapi/nws/weather-api.yaml` | Companion NWS OpenAPI subset. |
| `../../views/nws.address-forecast.summary.jq` | Readable jq projection for run output. |

## Coordinates Instead

```bash
set -o pipefail
arazzo-cli --json run specs/nws/point-forecast-alerts.arazzo.yaml point-forecast-alerts \
  --strict-inputs --input-json latitude=37.3350331 --input-json longitude=-122.0142785 \
| jq -er -f views/nws.point-forecast-alerts.summary.jq
```

The address workflow returns the matched address, not a guarantee of a rooftop
match. The point workflow starts directly from coordinates; neither asks users
to know NWS office/grid IDs. Both expose the full active-alert collection and
the summary prints every returned alert, including the valid empty-list case.

## Provider Policy and Proof

[NWS API guidance](https://www.weather.gov/documentation/services-web-api)
requests an identifying User-Agent. Override `NWS_USER_AGENT` with your app
name/contact. [Nominatim's public usage policy](https://operations.osmfoundation.org/policies/nominatim/)
requires an identifying app, a maximum of one request per second, attribution,
and forbids heavy/bulk and autocomplete use. This workflow makes one geocoding
request per execution; do not run batches or parallel loops. Respect the match's
OpenStreetMap attribution/license. Coordinates-only execution avoids geocoding.

All repository examples use Apple Headquarters, never a user's private address.
Response fixtures are static examples, not current weather. Offline tests
exercise full dataflow, multiple/empty alerts, no address match and upstream
failure. Live provider availability remains separate. This is not an emergency
alerting or life-safety system.
