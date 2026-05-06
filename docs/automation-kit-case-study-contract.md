# Automation Kit Case-Study Contract

`api-webhook-bridge` is a concrete companion template for Automation Kit's reusable automation architecture.

## Contract

- Automation Kit owns reusable pattern vocabulary and mock clients.
- This repo owns API/webhook mappings, FastAPI routes, fixtures, and case-study evidence.
- All proof examples are fixture-safe and local.
- The repo can be reviewed without claiming live SaaS connectivity or hosted availability.

## Verified flows

1. HubSpot-like contact -> Airtable-style upsert.
2. Shopify-like order -> Slack-style alert + CRM note.
3. Stripe-like payment -> payment audit + Slack-style alert + idempotency proof.

## Evidence paths

- `README.md`
- `docs/case-study.md`
- `docs/evidence.md`
- `docs/screenshots/`
- `configs/mappings/`
- `examples/api-responses/`
