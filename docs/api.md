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
| GET | `/health` | Fixture-safe health check |
| GET | `/integrations` | Lists source/destination proof scope and Automation Kit backbone contract |
| GET | `/mappings` | Lists visible mapping configs |
| POST | `/webhooks/hubspot-like` | Contact to Airtable-style upsert |
| POST | `/webhooks/shopify-like` | Order to Slack + CRM-style note |
| POST | `/webhooks/stripe-like` | Payment to audit + Slack-style notification |
| GET | `/audit/events` | Local success audit proof |
| GET | `/audit/dead-letter` | Local dead-letter proof |

Named routes are intentionally buyer-legible for OpenAPI screenshots. The generic `/webhooks/{source}` route remains for local convenience.
