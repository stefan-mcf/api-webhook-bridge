# Validation

The repository checks request limits, JSON parsing, source contracts, field mappings, idempotency, audit records, dead-letter handling, saved responses, and generated image integrity.

## Environment

Use Python 3.11 or newer and the Automation Kit revision pinned in `pyproject.toml`.

```bash
git -C ../automation-kit checkout b4b1df2730bc928b8c9ee96f716b706b41856cf1
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e '.[dev]'
export AUTOMATION_KIT_PATH=../automation-kit
export AUTOMATION_KIT_PATTERNS="$AUTOMATION_KIT_PATH/patterns"
export PYTHONPATH="$AUTOMATION_KIT_PATH/src:src"
```

## Quality gates

```bash
python -m pytest tests -q
python -m ruff check src tests scripts
python -m mypy src
examples/run-local-validation.sh
python scripts/capture_screenshots.py
git diff --check
```

The image generator derives its current test total from pytest output. The local scenario script fixes only the committed response timestamp so repeated runs produce stable public artifacts; normal runtime audit records still use the current UTC time.

## Saved response contract

The local scenario run refreshes and checks:

- health, integration, and mapping readback;
- accepted contact, order, and payment responses;
- duplicate payment handling;
- rejected contact handling;
- audit and dead-letter collections.

All saved files live under `examples/api-responses/`. They contain synthetic identifiers and no provider credentials or customer records.

## Manual API smoke commands

```bash
uvicorn api_webhook_bridge.api:app --host 127.0.0.1 --port 8011
curl -fsS http://127.0.0.1:8011/health
curl -fsS http://127.0.0.1:8011/integrations
curl -fsS http://127.0.0.1:8011/mappings
curl -fsS -X POST http://127.0.0.1:8011/webhooks/hubspot-like \
  -H 'content-type: application/json' \
  --data @examples/input/contact-created.json
curl -fsS http://127.0.0.1:8011/audit/events
curl -fsS http://127.0.0.1:8011/audit/dead-letter
```

See [Local operation](local-operation.md) and the [image index](screenshots/README.md) for the functional sequence.
