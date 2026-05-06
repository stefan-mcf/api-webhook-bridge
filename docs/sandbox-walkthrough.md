# Sandbox Walkthrough

This walkthrough shows the fixture-safe API/webhook bridge as a reusable client template. It proves the pre-live integration slice: receive a source webhook, validate the payload, map fields to a target-shaped operation, handle duplicate delivery, write audit/dead-letter records, and leave handoff evidence before any live credentials are connected.

## What this proves

- A FastAPI webhook receiver with OpenAPI-visible routes.
- Explicit field mapping from source payloads to destination operations.
- Deterministic request/response examples with synthetic data.
- Idempotency handling for duplicate events.
- Audit and dead-letter records for reviewable operations.
- A repeatable first milestone that can be adapted to client-specific SaaS stacks after credential approval.

The bridge does not call live HubSpot, Shopify, Stripe, Airtable, Slack, CRM, or cloud APIs. Every fixture is synthetic and local.

## End-to-end flow

1. A synthetic source event is sent to a local FastAPI webhook route.
2. The bridge selects the mapping config for the event type.
3. Required fields are validated before any target operation is prepared.
4. Source fields are transformed into target-shaped destination operations.
5. An idempotency key prevents duplicate delivery from creating new work.
6. A structured audit record is written for mapped or duplicate events.
7. Invalid payloads become dead-letter records for manual review.

Open the visual overview: `docs/screenshots/01-flow-overview.png`.

## Scenario A — contact created

| Item | Path |
|---|---|
| Source event | `examples/input/contact-created.json` |
| Mapping config | `configs/mappings/hubspot-contact-to-airtable.json` |
| API response | `examples/api-responses/hubspot-contact-response.json` |
| Screenshot | `docs/screenshots/03-sandbox-contact-event.png` |

A HubSpot-like `contact.created` event is mapped into an Airtable-style upsert operation. The response includes validation status, mapped fields, destination operation details, audit identifiers, and safety flags.

## Scenario B — order created

| Item | Path |
|---|---|
| Source event | `examples/input/shopify-order-created.json` |
| Mapping config | `configs/mappings/shopify-order-to-slack-crm.json` |
| API response | `examples/api-responses/shopify-order-response.json` |
| Screenshot | `docs/screenshots/02-openapi-webhook-endpoint.png` |

A Shopify-like `order.created` event is mapped to a Slack-style operations alert and a CRM-style note. This demonstrates a common ecommerce handoff pattern without touching live accounts.

## Scenario C — payment succeeded

| Item | Path |
|---|---|
| Source event | `examples/input/stripe-payment-succeeded.json` |
| Mapping config | `configs/mappings/stripe-payment-to-audit-slack.json` |
| API response | `examples/api-responses/stripe-payment-response.json` |
| Duplicate response | `examples/api-responses/stripe-payment-duplicate-response.json` |
| Screenshot | `docs/screenshots/05-idempotency-audit.png` |

A Stripe-like `payment.succeeded` event is mapped to payment-audit and Slack-style operations. Replaying the same event proves duplicate detection through the idempotency key.

## Failure path — dead letter

| Item | Path |
|---|---|
| Invalid source event | `examples/input/contact-created-invalid.json` |
| Dead-letter response | `examples/api-responses/dead-letter-response.json` |
| Dead-letter records | `examples/api-responses/dead-letter.json` |
| Screenshot | `docs/screenshots/06-dead-letter.png` |

The invalid contact fixture omits required fields. The bridge prepares no destination operation, marks the event as `validation_failed`, and writes a dead-letter record that can be reviewed and replayed after the payload is fixed.

## Client adaptation matrix

| Source | Target | Client use case | What changes in this template |
|---|---|---|---|
| Stripe payment | Airtable + Slack | Payment ops alert and reconciliation | payment fixture, mapping JSON, target adapter |
| Shopify order | CRM + Slack | New order notification and customer note | order fixture, mapping JSON, target adapter |
| HubSpot contact | Airtable/Sheets | Lead sync and sales handoff | contact fixture, mapping JSON, target adapter |
| Typeform lead | CRM/Slack | Form-to-sales routing | lead fixture, validation schema, target adapter |
| Custom webhook | Database/API | Internal workflow bridge | fixture schema, mapping JSON, target adapter |

These rows describe adaptation paths, not live-provider claims. Live credentials, OAuth scopes, provider dashboard screenshots, and real webhook delivery logs remain separate gated work.

## Run the local walkthrough

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" examples/run-sandbox-walkthrough.sh
```

The script starts the local API, sends all synthetic fixtures, saves pretty JSON responses under `examples/api-responses/`, and shuts the server down.

## Safety boundary

- Synthetic fixtures only.
- No live SaaS calls.
- No credentials or secrets.
- No real client/customer/account data.
- No cloud deployment or public URL.
- Public sharing, clean export, private collaborator access, and live SaaS proof remain separately gated.
