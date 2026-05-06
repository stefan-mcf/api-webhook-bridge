# Screenshot Evidence

All screenshots are generated from current local FastAPI/API outputs and synthetic fixtures. They contain no secrets, real customer data, account screens, private browser tabs, cloud resources, or live SaaS context.

| File | Proves |
|---|---|
| `01-flow-overview.png` | Reusable source -> FastAPI bridge -> validation -> mapping -> mock target -> audit/dead-letter flow. |
| `02-openapi-webhook-endpoint.png` | OpenAPI exposes named local proof routes for health, integrations, mappings, three webhook sources, audit events, and dead-letter records. |
| `03-sandbox-contact-event.png` | HubSpot-like contact maps to an Airtable-style upsert response with validation and audit identifiers. |
| `04-mapping-config.png` | Field mapping is explicit and reviewable in JSON before live credentials are connected. |
| `05-idempotency-audit.png` | Stripe-like payment replay is detected as a duplicate and recorded in the audit surface. |
| `06-dead-letter.png` | Invalid payloads are routed to dead-letter records instead of silent failures. |

Validation notes:

- Final images are page-level screenshots with no obstructing windows or browser chrome.
- Full-page capture was used for taller evidence pages so lower audit/dead-letter content is not cut off.
- Screenshot review confirmed no secrets, private desktop/browser/account details, or live provider context.
