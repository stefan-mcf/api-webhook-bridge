# Sandbox Walkthrough

This walkthrough shows the fixture-safe API/webhook bridge as a reusable client template. It
proves the pre-live integration slice: receive a source webhook, validate the payload, map
fields to a target-shaped operation, handle duplicate delivery, write audit/dead-letter
records, and leave handoff evidence before any live credentials are connected.

## What this proves

- A FastAPI webhook receiver with OpenAPI-visible routes.
- Explicit field mapping from source payloads to destination operations.
- Deterministic request/response examples with synthetic data.
- Idempotency handling for duplicate events.
- Audit and dead-letter records for reviewable operations.
- A repeatable first milestone that can adapt to approved external-service stacks later.

The bridge does not call live HubSpot, Shopify, Stripe, Airtable, Slack, CRM, or cloud APIs.
Every fixture is synthetic and local.

## End-to-end flow

1. A synthetic source event is sent to a local FastAPI webhook route. 2. The bridge selects
the mapping config for the event type. 3. Required fields are validated before any target
operation is prepared. 4. Source fields are transformed into target-shaped destination
operations. 5. An idempotency key prevents duplicate delivery from creating new work. 6. A
structured audit record is written for mapped or duplicate events. 7. Invalid payloads become
dead-letter records for manual review.

Open the visual overview: `docs/screenshots/01-flow-overview.png`.

## Scenario A — contact created

| Item | Path |
|---|---|
| Source event | `examples/input/contact-created.json` |
| Mapping config | `configs/mappings/hubspot-contact-to-airtable.json` |
| API response | `examples/api-responses/hubspot-contact-response.json` |
| Screenshot | `docs/screenshots/03-contact-bridge-proof.png` |

A HubSpot-like `contact.created` event is mapped into an Airtable-style upsert operation. The
response includes validation status, mapped fields, destination operation details, audit
identifiers, and safety flags.

## Scenario B — Shopify order + Stripe payment intake for Mock Job 01

| Item | Path |
|---|---|
| Shopify source event | `examples/input/shopify-order-created.json` |
| Shopify mapping config | `configs/mappings/shopify-order-to-slack-crm.json` |
| Shopify API response | `examples/api-responses/shopify-order-response.json` |
| Stripe source event | `examples/input/stripe-payment-succeeded.json` |
| Stripe mapping config | `configs/mappings/stripe-payment-to-audit-slack.json` |
| Stripe API response | `examples/api-responses/stripe-payment-response.json` |
| Mock Job 01 screenshot | `docs/screenshots/09-mock-job-01-bridge-proof.png` |
| Duplicate screenshot | `docs/screenshots/05-idempotency-audit.png` |

Shopify-like `order.created` and Stripe-like `payment.succeeded` events provide the primary Mock Job 01 green path. This bridge proves receipt, validation, mapping, idempotency, and audit behavior; downstream Airtable Ops Ledger and spreadsheet-friendly reporting are demonstrated by `sheets-airtable-sync` in the mock-job package.

## Scenario C — payment retry / duplicate delivery

| Item | Path |
|---|---|
| Source event | `examples/input/stripe-payment-succeeded.json` |
| Mapping config | `configs/mappings/stripe-payment-to-audit-slack.json` |
| API response | `examples/api-responses/stripe-payment-response.json` |
| Duplicate response | `examples/api-responses/stripe-payment-duplicate-response.json` |
| Screenshot | `docs/screenshots/05-idempotency-audit.png` |

A Stripe-like `payment.succeeded` event is mapped to payment-audit and Slack-style operations.
Replaying the same event proves duplicate detection through the idempotency key. In Mock Job 01,
this gives the payment-side intake proof that is later paired with downstream ops ledgers and
exception reporting in `sheets-airtable-sync`.

## Failure path — dead letter

| Item | Path |
|---|---|
| Invalid source event | `examples/input/contact-created-invalid.json` |
| Dead-letter response | `examples/api-responses/dead-letter-response.json` |
| Dead-letter records | `examples/api-responses/dead-letter.json` |
| Screenshot | `docs/screenshots/06-dead-letter.png` |

The invalid contact fixture omits required fields. The bridge prepares no destination
operation, marks the event as `validation_failed`, and writes a dead-letter record that can be
reviewed and replayed after the payload is fixed.

## Client adaptation matrix

| Source | Target | Use case | Change |
|---|---|---|---|
| Stripe payment | Airtable + Slack | Ops alert | payment fixture + mapping |
| Shopify order | CRM + Slack | Order note | order fixture + mapping |
| HubSpot contact | Airtable/Sheets | Lead sync | contact fixture + mapping |
| Typeform lead | CRM/Slack | Lead routing | lead fixture + schema |
| Custom webhook | Database/API | Internal bridge | fixture schema + adapter |

These rows describe adaptation paths, not live-provider claims. Live credentials, OAuth
scopes, provider dashboard screenshots, and real webhook delivery logs remain separate gated
work.

## Run the local walkthrough

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" examples/run-sandbox-walkthrough.sh
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python scripts/verify_sandbox_responses.py
```

The script starts the local API, sends all synthetic fixtures, saves pretty JSON responses
under `examples/api-responses/`, verifies the saved response contract, and shuts the server down.
If the configured port is already occupied, it exits before deleting/regenerating artifacts so a
stale server cannot contaminate the proof run.

## Safety boundary

- Synthetic fixtures only.
- No live external-service calls.
- No credentials or secrets.
- No real client/customer/account data.
- No cloud deployment or public URL.
- Public sharing, clean export, private collaborator access, and live external-service proof
  remain separately gated.
