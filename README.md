# API Webhook Bridge

Fixture-safe FastAPI webhook bridge template for validating payloads, mapping fields, handling duplicates, and auditing integration flows before connecting live external-service credentials.

It proves a safe first milestone for integration jobs: receive one source event, validate it, map fields into destination-shaped operations, return request/response evidence, write audit/dead-letter proof, and leave handoff notes before any live account is touched.

## What it connects locally

| Flow | Source event | Destination proof | Evidence |
|---|---|---|---|
| HubSpot-like contact | `contact.created` | Airtable-style upsert | `examples/input/contact-created.json`, `examples/api-responses/hubspot-contact-response.json` |
| Shopify-like order | `order.created` | Slack ops alert + CRM note | `examples/input/shopify-order-created.json`, `examples/api-responses/shopify-order-response.json` |
| Stripe-like payment | `payment.succeeded` | Payment audit record + Slack alert + idempotency | `examples/input/stripe-payment-succeeded.json`, `examples/api-responses/stripe-payment-response.json` |
| Invalid contact | `contact.created` missing required fields | Dead-letter review record | `examples/input/contact-created-invalid.json`, `examples/api-responses/dead-letter-response.json` |

All systems are synthetic and local. The project does not call HubSpot, Shopify, Stripe, Airtable, Slack, CRM, or a cloud service.

## Evidence package

| Evidence | What to open |
|---|---|
| Flow overview | `docs/screenshots/01-flow-overview.png` |
| OpenAPI webhook endpoints | `docs/screenshots/02-openapi-webhook-endpoint.png` |
| Sandbox contact event | `docs/screenshots/03-sandbox-contact-event.png` |
| Visible mapping config | `docs/screenshots/04-mapping-config.png` |
| Idempotency and audit proof | `docs/screenshots/05-idempotency-audit.png` |
| Dead-letter proof | `docs/screenshots/06-dead-letter.png` |
| Walkthrough narrative | `docs/sandbox-walkthrough.md` |
| Command evidence and local gates | `docs/evidence.md` |

The screenshots are page-clean captures from synthetic local fixtures. They show no live account screens, credentials, browser tabs, private desktop context, or client data.

## Run the sandbox walkthrough

Use a sibling Automation Kit checkout, then regenerate the API responses locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ../automation-kit
pip install -e '.[dev]'
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" examples/run-sandbox-walkthrough.sh
```

Inspect locally:

- `GET /health`
- `GET /integrations`
- `GET /mappings`
- `POST /webhooks/hubspot-like`
- `POST /webhooks/shopify-like`
- `POST /webhooks/stripe-like`
- `GET /audit/events`
- `GET /audit/dead-letter`

## Adapt this template

| Source | Target | Client use case | What changes in this template |
|---|---|---|---|
| Stripe payment | Airtable + Slack | Payment ops alert and reconciliation | payment fixture, mapping JSON, target adapter |
| Shopify order | CRM + Slack | New order notification and customer note | order fixture, mapping JSON, target adapter |
| HubSpot contact | Airtable/Sheets | Lead sync and sales handoff | contact fixture, mapping JSON, target adapter |
| Typeform lead | CRM/Slack | Form-to-sales routing | lead fixture, validation schema, target adapter |
| Custom webhook | Database/API | Internal workflow bridge | fixture schema, mapping JSON, target adapter |

These are adaptation paths, not live-provider claims. Live credentials, OAuth scopes, provider dashboards, and real webhook delivery logs are separate gated work.

## Built on Automation Kit

Automation Kit is the reusable backbone. This repo is the thin buyer-shaped spoke.

Used backbone modules:

- `auto_kit.pattern_runner` for pattern/workflow vocabulary;
- `auto_kit.mock_clients` for deterministic CRM and Slack-style mock destination preparation;
- `auto_kit.workflow_schema` for validated workflow contract language.

See `docs/automation-kit-backbone.md` and `docs/automation-kit-case-study-contract.md`.

## Project docs

| Proof surface | Path |
|---|---|
| Sandbox walkthrough | `docs/sandbox-walkthrough.md` |
| Case study | `docs/case-study.md` |
| Command evidence and local gates | `docs/evidence.md` |
| FastAPI/OpenAPI notes | `docs/api.md` |
| Mapping configs | `configs/mappings/` |
| API request examples | `examples/api-requests/` |
| API response examples | `examples/api-responses/` |
| Screenshots | `docs/screenshots/` |
| First milestone copy | `docs/first-milestone.md` |
| Production path notes | `docs/production-path.md` |
| Public readiness checklist | `docs/public-readiness-checklist.md` |

## Safety boundary

- Fixture-safe synthetic examples only.
- Empty credential placeholders only.
- `fixture_safe: true` and `live_services_used: false` are returned in proof responses.
- Runtime audit files under `.local/` are ignored.
- No live external-service calls, client data, cloud resources, public visibility changes, releases, or external sharing actions are part of the local proof.
- Public export, existing-repo visibility changes, private collaborator access, live external-service proof, and cloud deployment remain human-gated.

## First milestone shape

Map one approved source event to the destination schema, run it against synthetic or approved sample data, return the validated output payload, audit log, retry/idempotency notes, and a handoff note. Live credential connection happens only after that proof slice is reviewed.
