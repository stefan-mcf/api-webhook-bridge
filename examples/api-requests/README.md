# API Request Examples

Use these with the local FastAPI server only:

```bash
curl -fsS -X POST http://127.0.0.1:8011/webhooks/hubspot-like -H 'content-type: application/json' --data @examples/api-requests/hubspot-contact.json
curl -fsS -X POST http://127.0.0.1:8011/webhooks/shopify-like -H 'content-type: application/json' --data @examples/api-requests/shopify-order.json
curl -fsS -X POST http://127.0.0.1:8011/webhooks/stripe-like -H 'content-type: application/json' --data @examples/api-requests/stripe-payment.json
```

All payloads are synthetic fixtures.
