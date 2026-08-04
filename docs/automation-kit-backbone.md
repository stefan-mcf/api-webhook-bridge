# Automation Kit Dependency Contract

API Webhook Bridge uses Automation Kit for reusable workflow discovery, schema loading, and mock destination clients. Source contracts, mapping configurations, FastAPI routes, idempotency, and audit handling remain in this repository.

## Pinned revision

`pyproject.toml` installs Automation Kit from this exact public Git revision:

```text
b4b1df2730bc928b8c9ee96f716b706b41856cf1
```

The CI workflow checks out the same revision before running the bridge gates. This keeps local, CI, and reviewer setup aligned while avoiding an absolute machine path in package metadata.

## Imported modules

Production imports are isolated in `src/api_webhook_bridge/backbone.py`:

- `auto_kit.pattern_runner.discover_patterns`
- `auto_kit.pattern_runner.load_workflow_json`
- `auto_kit.mock_clients.MockCRMClient`
- `auto_kit.mock_clients.MockSlackClient`
- `auto_kit.workflow_schema.WorkflowJSON`

## Local pattern path

The `/integrations` readback loads reusable JSON patterns from an explicit checkout:

```bash
export AUTOMATION_KIT_PATH=../automation-kit
export AUTOMATION_KIT_PATTERNS="$AUTOMATION_KIT_PATH/patterns"
export PYTHONPATH="$AUTOMATION_KIT_PATH/src:src"
```

## Contract check

```bash
python -m pytest tests/test_automation_kit_contract.py -q
```

The check fails if the expected modules, mock clients, or workflow schema are unavailable at the pinned revision.
