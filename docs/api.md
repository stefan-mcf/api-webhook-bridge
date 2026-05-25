# Local API Surface

Run locally only:

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" uvicorn api_webhook_bridge.api:app --host 127.0.0.1 --port 8011
```

OpenAPI JSON is available at `http://127.0.0.1:8011/openapi.json` and docs at `http://127.0.0.1:8011/docs`.

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Fixture-safe health check. |
| GET | `/integrations` | Lists supported source/destination scope and local integration contract. |
| GET | `/mappings` | Lists visible mapping configs. |
| POST | `/webhooks/hubspot-like` | Named contact intake route. |
| POST | `/webhooks/shopify-like` | Named order intake route. |
| POST | `/webhooks/stripe-like` | Named payment intake route. |
| POST | `/webhooks/{source}` | Generic route for approved sources only. Unknown sources return `404`. |
| GET | `/audit/events` | Local success and duplicate-processing audit output. |
| GET | `/audit/dead-letter` | Local dead-letter output for rejected payloads. |

## Request contract

- Request bodies are streamed and rejected above the 64KB payload limit.
- Payloads must be valid JSON.
- Payloads must decode to a JSON object; arrays and scalar values are rejected.
- Named webhook routes and the generic `/webhooks/{source}` route share the same payload handling and bridge logic.
- The generic route accepts only `hubspot-like`, `shopify-like`, and `stripe-like`.
- Unknown generic-route sources return `404` before bridge processing.

Named routes are intentionally buyer-legible for OpenAPI screenshots and direct local testing. The generic route remains useful for operator convenience and adaptation work.
