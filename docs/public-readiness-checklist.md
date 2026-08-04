# Public Readiness Checklist

Status: public at <https://github.com/stefan-mcf/api-webhook-bridge>.

## Public scope

- [x] The repository presents a synthetic, pre-live integration implementation rather than a live provider connection.
- [x] README and docs do not claim production deployment, hosted availability, real customer data, or completed external delivery.
- [x] Live external-service access, cloud resources, releases, and external sharing remain gated.

## Portfolio assets

- [x] `docs/local-operation.md` explains the source -> bridge -> mapping -> destination -> audit/dead-letter flow.
- [x] `docs/screenshots/01-system-flow.png` exists and is readable at GitHub width.
- [x] Interface, processing, guardrail, readback, and validation images exist.
- [x] The image index explains every functional panel.
- [x] All screenshots show synthetic data only and no private desktop/browser/account context.

## Reuse and adaptation

- [x] README/docs describe how the bridge adapts to provider-shaped payloads without requiring live credentials.
- [x] Provider names are framed as source/target shapes unless live credentials are explicitly approved.
- [x] One command regenerates and validates example responses locally.

## Privacy and artifact hygiene

Run:

```bash
git grep -n -I -E '/(Users|home)/|HOME=/|api[_-]?key|secret|password|token|PRIVATE KEY|chat_id|auth\.json|\.env' -- $(git ls-files) || true
git ls-files --others --exclude-standard
git ls-files -ci --exclude-standard
git diff --check
```

Review all hits before release tags or major public positioning changes.

## Verification bundle

Run from the repo root:

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m pytest -q
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m ruff check .
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m mypy src
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" examples/run-local-validation.sh
python - <<'PY'
from pathlib import Path
import json
for base in ['examples', 'configs']:
    for p in Path(base).rglob('*.json'):
        json.loads(p.read_text())
print('json ok')
PY
git diff --check
```

## Remaining gates

Stop before any of these until explicitly approved:

- release or tag created;
- live external-service credentials/accounts connected;
- cloud deployment or public URL created;
- real client data used;
- external message or client handoff sent;
- external collaborator invited.
