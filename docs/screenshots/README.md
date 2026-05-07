# Screenshot Evidence

All screenshots are generated proof panels from current local API responses, mapping JSON, and
synthetic fixtures. They contain no secrets, real customer data, account screens, private
browser tabs, cloud resources, or live external-service context.

- `01-flow-overview.png` — source -> bridge -> mapping -> audit/dead-letter flow.
- `02-openapi-webhook-endpoints.png` — local health, mapping, webhook, and audit routes.
- `03-contact-bridge-proof.png` — contact fixture to Airtable-style upsert evidence.
- `04-mapping-config.png` — explicit JSON field mapping before credential work.
- `05-idempotency-audit.png` — duplicate payment replay recorded as audit evidence.
- `06-dead-letter.png` — invalid payload routed to review evidence.
- `07-quality-gates.png` — local test proof backed by the full gate bundle.
- `08-debugger-handoff.png` — green-path bridge proof plus repair-path handoff.

Validation notes:

- Final images are generated at 1280x760 so README panels remain readable.
- Every PNG carries proof metadata and passes size/variance checks in screenshot tests.
- Screenshot review confirms no secrets, private browser/account details, or live context.
- Regenerate after changing fixtures, examples, README references, or proof copy:
  `PYTHONPATH=src python scripts/capture_screenshots.py`.
