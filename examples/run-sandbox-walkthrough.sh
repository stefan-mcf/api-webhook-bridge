#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d src/api_webhook_bridge || ! -d examples/input ]]; then
  echo "Run from the api-webhook-bridge repo root" >&2
  exit 1
fi

PORT="${PORT:-8011}"
HOST="127.0.0.1"
BASE_URL="http://${HOST}:${PORT}"
OUT_DIR="examples/api-responses"
PYTHON_BIN="${PYTHON_BIN:-python}"
mkdir -p "$OUT_DIR"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f .local/audit/events.jsonl .local/audit/dead-letter.jsonl 2>/dev/null || true

$PYTHON_BIN -m uvicorn api_webhook_bridge.api:app --host "$HOST" --port "$PORT" > .local-sandbox-walkthrough.log 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 80); do
  if curl -fsS "$BASE_URL/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done
curl -fsS "$BASE_URL/health" | $PYTHON_BIN -m json.tool > "$OUT_DIR/health.json"
curl -fsS "$BASE_URL/integrations" | $PYTHON_BIN -m json.tool > "$OUT_DIR/integrations.json"
curl -fsS "$BASE_URL/mappings" | $PYTHON_BIN -m json.tool > "$OUT_DIR/mappings.json"

curl -fsS -X POST "$BASE_URL/webhooks/hubspot-like"   -H 'content-type: application/json'   --data @examples/input/contact-created.json   | $PYTHON_BIN -m json.tool > "$OUT_DIR/hubspot-contact-response.json"

curl -fsS -X POST "$BASE_URL/webhooks/shopify-like"   -H 'content-type: application/json'   --data @examples/input/shopify-order-created.json   | $PYTHON_BIN -m json.tool > "$OUT_DIR/shopify-order-response.json"

curl -fsS -X POST "$BASE_URL/webhooks/stripe-like"   -H 'content-type: application/json'   --data @examples/input/stripe-payment-succeeded.json   | $PYTHON_BIN -m json.tool > "$OUT_DIR/stripe-payment-response.json"

curl -fsS -X POST "$BASE_URL/webhooks/stripe-like"   -H 'content-type: application/json'   --data @examples/input/stripe-payment-succeeded.json   | $PYTHON_BIN -m json.tool > "$OUT_DIR/stripe-payment-duplicate-response.json"

curl -fsS -X POST "$BASE_URL/webhooks/hubspot-like"   -H 'content-type: application/json'   --data @examples/input/contact-created-invalid.json   | $PYTHON_BIN -m json.tool > "$OUT_DIR/dead-letter-response.json"

curl -fsS "$BASE_URL/audit/events" | $PYTHON_BIN -m json.tool > "$OUT_DIR/audit-events.json"
curl -fsS "$BASE_URL/audit/dead-letter" | $PYTHON_BIN -m json.tool > "$OUT_DIR/dead-letter.json"

echo "Sandbox walkthrough responses written to $OUT_DIR"
