# Case Study: Fixture-Safe API Webhook Bridge

## Client problem

API/webhook clients need confidence before live credentials are connected: one source event should be validated, mapped to the destination shape, replayed safely, and documented with request/response evidence.

## Local proof

This repo demonstrates three synthetic flows:

1. HubSpot-like `contact.created` -> Airtable-style upsert.
2. Shopify-like `order.created` -> Slack-style ops alert plus CRM note.
3. Stripe-like `payment.succeeded` -> payment audit record plus Slack-style notification with duplicate delivery proof.

## Field mapping deliverable

The first buyer artifact is a field map under `configs/mappings/`. Each JSON config lists required fields, idempotency fields, destination operations, and a handoff note. That mirrors the first milestone a client receives before live system access.

## Automation Kit backbone

`api-webhook-bridge` is a thin spoke. It imports Automation Kit through `backbone.py` for workflow vocabulary and deterministic mock clients while keeping source-to-destination mapping logic in this repo.

## Observability and safe retry proof

Responses include:

- `audit_id`
- `correlation_id`
- `idempotency_key`
- `duplicate`
- `retry_recommendation`
- `safe_to_retry`
- `fixture_safe: true`
- `live_services_used: false`

Unknown events and missing required fields create local dead-letter records rather than pretending a destination write happened.

## Scope boundary

This is local proof. It does not connect live HubSpot, Shopify, Stripe, Airtable, Slack, CRM, cloud, or client accounts. A production path would add scoped credentials, staging replay, durable idempotency storage, retries/backoff, observability, and rollback planning after approval.
