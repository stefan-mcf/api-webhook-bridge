# Local Operation

The local service exercises the complete bridge path without connecting provider accounts: receive a synthetic webhook, validate its contract, map approved fields, control duplicate delivery, and record accepted or rejected outcomes.

## Expected results

- FastAPI routes visible through the generated OpenAPI contract.
- Explicit mappings from source fields to destination-shaped operations.
- Deterministic request and response records built from synthetic data.
- Stable idempotency keys for repeated provider-style deliveries.
- Audit and dead-letter records suitable for operator review.

The service does not call HubSpot, Shopify, Stripe, Airtable, Slack, CRM, or cloud APIs.

## Operating flow

1. Send a synthetic event to a named local route.
2. Select the mapping configuration for its source and event type.
3. Validate required fields before preparing destination work.
4. Transform approved fields into destination-shaped operations.
5. Evaluate a stable idempotency key.
6. Record accepted, duplicate, or rejected processing.
7. Return audit and correlation identifiers for readback.

## Contact scenario

| Item | Path |
| --- | --- |
| Source event | `examples/input/contact-created.json` |
| Mapping | `configs/mappings/hubspot-contact-to-airtable.json` |
| Saved response | `examples/api-responses/hubspot-contact-response.json` |
| Processing image | `docs/screenshots/03-core-processing.png` |

A HubSpot-shaped contact event becomes one Airtable-shaped upsert operation. The response exposes its mapping, destination operation, audit identifier, correlation identifier, and retry state.

## Order and payment scenarios

| Item | Path |
| --- | --- |
| Order event | `examples/input/shopify-order-created.json` |
| Order mapping | `configs/mappings/shopify-order-to-slack-crm.json` |
| Order response | `examples/api-responses/shopify-order-response.json` |
| Payment event | `examples/input/stripe-payment-succeeded.json` |
| Payment mapping | `configs/mappings/stripe-payment-to-audit-slack.json` |
| Payment response | `examples/api-responses/stripe-payment-response.json` |
| Readback image | `docs/screenshots/05-operating-readback.png` |

The order event prepares coordinated CRM-note and operations-alert actions. The payment event prepares audit and alert actions, then rejects an identical replay without creating repeated destination work.

## Failure scenario

| Item | Path |
| --- | --- |
| Invalid event | `examples/input/contact-created-invalid.json` |
| API response | `examples/api-responses/dead-letter-response.json` |
| Dead-letter records | `examples/api-responses/dead-letter.json` |
| Guardrail image | `docs/screenshots/04-event-guardrails.png` |

The invalid contact omits required fields. The bridge prepares no destination operation and records a structured dead-letter item with reason codes and a recommended next action.

## Run the local scenarios

```bash
export AUTOMATION_KIT_PATH=../automation-kit
export AUTOMATION_KIT_PATTERNS="$AUTOMATION_KIT_PATH/patterns"
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" examples/run-local-validation.sh
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python scripts/validate_saved_responses.py
```

The script starts the API, sends every synthetic fixture, refreshes the saved JSON responses, validates their contracts, and stops the service. It exits before changing saved files if the configured port is already occupied.

## Operating boundary

- Synthetic fixtures and local storage only.
- No credentials, provider writes, or customer records.
- No cloud deployment or public API endpoint.
- Destination-shaped operations are prepared but not executed.
- Live adapters, durable storage, retry policy, monitoring, and deployment remain separate production work.
