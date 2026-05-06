# Automation Kit Backbone Contract

This spoke uses Automation Kit as the reusable engine and keeps buyer-specific API/webhook mapping in this repository.

## Local dependency strategy

For the private local proof, install the sibling repository in editable mode before this spoke:

```bash
pip install -e ../automation-kit
pip install -e '.[dev]'
```

The package metadata intentionally does not hardcode an absolute path dependency. That keeps public/export packaging honest while making the private local prerequisite explicit.

## Imported modules

All production imports from Automation Kit are isolated in `src/api_webhook_bridge/backbone.py`:

- `auto_kit.pattern_runner.discover_patterns`
- `auto_kit.pattern_runner.load_workflow_json`
- `auto_kit.mock_clients.MockCRMClient`
- `auto_kit.mock_clients.MockSlackClient`
- `auto_kit.workflow_schema.WorkflowJSON`

## Verification

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m pytest tests/test_automation_kit_contract.py -q
```

The contract test fails clearly if Automation Kit is missing or if the expected modules cannot be imported.
