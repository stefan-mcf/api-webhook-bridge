# Case study: a webhook bridge that makes integrations predictable

Webhook integrations often look simple in a diagram: receive an event, map a few fields, and call the next API. The difficult work appears when payloads are incomplete, providers retry deliveries, mappings change, or an operator needs to explain what happened after the request has finished.

API Webhook Bridge is a FastAPI service that makes those behaviours explicit before a live provider connection is introduced. It validates incoming events, converts them into destination-shaped operations, detects duplicates, and records both successful and rejected processing.

## The integration brief

The service was designed around three common event families:

| Source event | Destination-shaped result | Operational concern |
| --- | --- | --- |
| Contact created | Airtable-style upsert | Required fields and stable record identity |
| Order created | CRM note and operations alert | One source event producing coordinated actions |
| Payment succeeded | Payment audit entry and operations alert | Duplicate provider delivery |

The goal was not to hide these flows behind one generic “send data” function. Each route needed an inspectable contract, a deterministic mapping, and an audit trail that could be reviewed before real credentials were connected.

## Architecture

```text
webhook request
      │
      ▼
body size and JSON checks
      │
      ▼
source contract validation
      │
      ▼
config-driven field mapping
      │
      ▼
idempotency decision
   ┌──┴──────────────┐
   ▼                 ▼
operations plan   duplicate ignored
   │
   ▼
audit record

invalid input ──► dead-letter record
```

FastAPI provides named routes for contact, order, and payment events as well as a constrained generic route. Mapping configuration lives outside the request handlers, while the bridge layer owns validation, idempotency, and operation preparation.

## Key engineering decisions

### Mapping is configuration, not route code

Each JSON mapping declares required fields, idempotency fields, destination operations, and a handover note. A reviewer can understand the contract without tracing request-handler branches.

### Idempotency is visible in the response

Every processed event includes an `idempotency_key`, `audit_id`, and `correlation_id`. A first payment delivery prepares two operations. Repeating the same event returns `duplicate_ignored` and records zero repeated destination operations.

### Invalid data stops before mapping

Non-object JSON, oversized requests, unknown sources, and missing required fields are rejected early. Invalid events create a dead-letter record with reason codes and a recommended next action.

### The OpenAPI surface is part of the handover

Named endpoints keep the service understandable to an implementation team and make the local scenarios easy to reproduce. The generic endpoint supports the same approved source set without turning the service into an unbounded proxy.

## A representative payment flow

The committed payment scenario receives a `payment.succeeded` event and:

1. validates the event ID, payment intent, customer email, amount, and currency;
2. maps the payload into a payment-audit record and an operations notification;
3. assigns stable correlation and idempotency identifiers;
4. records two planned destination operations;
5. accepts the first delivery and ignores the second delivery without repeating either operation.

The invalid-contact scenario exercises the opposite path. Missing `contact_id` and `email` fields produce a validation failure, zero destination operations, and a dead-letter entry.

## Result

The completed repository includes:

- a runnable FastAPI application and OpenAPI contract;
- three source-to-destination mapping configurations;
- named and generic webhook routes;
- idempotency, audit, and dead-letter handling;
- one command that regenerates and validates request and response records;
- automated checks across API, mapping, bridge, audit, idempotency, failure behaviour, and image integrity;
- screenshots generated from the committed local runs.

This gives an implementation team a concrete integration contract before provider access is requested and a clear path for explaining successful, duplicate, and rejected events.

## Scope and production path

The checked-in scenarios use controlled local data and prepare destination-shaped operations without calling HubSpot, Shopify, Stripe, Airtable, Slack, or a CRM.

Moving the bridge into production would add scoped provider credentials, durable idempotency storage, retry and backoff policy, structured monitoring, staging replay, and rollback procedures. The repository keeps those adapters outside the core mapping and validation logic so they can be introduced deliberately.

## Explore the implementation

- [API notes](api.md)
- [Local operation](local-operation.md)
- [Validation record](validation.md)
- [Production extension notes](production-path.md)
- [Generated screenshots](screenshots/README.md)
- [Back to the repository overview](../README.md)
