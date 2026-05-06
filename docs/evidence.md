# Evidence

## Verified local gates

Run from the repo root with a sibling Automation Kit checkout:

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m pytest -q
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m ruff check .
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m mypy src
```

Current implementation has passing pytest, Ruff, and mypy gates after the Automation Kit backed bridge work.

## One-command sandbox walkthrough

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" examples/run-sandbox-walkthrough.sh
```

The walkthrough starts a local FastAPI server, posts the synthetic fixtures, saves pretty JSON responses under `examples/api-responses/`, fetches audit/dead-letter endpoints, and shuts the server down.

Generated response files include:

- `examples/api-responses/health.json`
- `examples/api-responses/integrations.json`
- `examples/api-responses/mappings.json`
- `examples/api-responses/hubspot-contact-response.json`
- `examples/api-responses/shopify-order-response.json`
- `examples/api-responses/stripe-payment-response.json`
- `examples/api-responses/stripe-payment-duplicate-response.json`
- `examples/api-responses/dead-letter-response.json`
- `examples/api-responses/audit-events.json`
- `examples/api-responses/dead-letter.json`

## Manual API smoke commands

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" uvicorn api_webhook_bridge.api:app --host 127.0.0.1 --port 8011
curl -fsS http://127.0.0.1:8011/health
curl -fsS http://127.0.0.1:8011/integrations
curl -fsS http://127.0.0.1:8011/mappings
curl -fsS -X POST http://127.0.0.1:8011/webhooks/hubspot-like -H 'content-type: application/json' --data @examples/input/contact-created.json
curl -fsS -X POST http://127.0.0.1:8011/webhooks/shopify-like -H 'content-type: application/json' --data @examples/input/shopify-order-created.json
curl -fsS -X POST http://127.0.0.1:8011/webhooks/stripe-like -H 'content-type: application/json' --data @examples/input/stripe-payment-succeeded.json
curl -fsS http://127.0.0.1:8011/audit/events
curl -fsS http://127.0.0.1:8011/audit/dead-letter
```

## Screenshot package

See `docs/screenshots/README.md` and `docs/sandbox-walkthrough.md`.

## Safety notes

All examples are synthetic. Runtime audit logs under `.local/` are ignored. The proof uses no live credentials, real client data, public visibility change, cloud resource, or external sharing action.
