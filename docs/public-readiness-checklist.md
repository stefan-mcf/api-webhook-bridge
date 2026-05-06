# Public Readiness Checklist

Use this before making this repo public, creating a clean public export, or sharing it with a client/reviewer.

## Public claim

- [ ] The repo claims fixture-safe pre-live integration proof, not live SaaS integration.
- [ ] README and docs do not claim production deployment, hosted availability, real customer data, or completed external delivery.
- [ ] Live SaaS, cloud resources, releases, public visibility changes, and external sharing remain gated.

## Evidence package

- [ ] `docs/sandbox-walkthrough.md` explains the source -> bridge -> mapping -> destination -> audit/dead-letter flow.
- [ ] `docs/screenshots/01-flow-overview.png` exists and is readable at GitHub width.
- [ ] OpenAPI, sandbox event, mapping, idempotency/audit, and dead-letter screenshots exist.
- [ ] Screenshot README explains what every image proves.
- [ ] All screenshots show synthetic data only and no private desktop/browser/account context.

## Reuse and adaptation

- [ ] README includes a client adaptation matrix or links to the walkthrough matrix.
- [ ] Provider names are framed as source/target shapes unless live credentials are explicitly approved.
- [ ] The one-command walkthrough regenerates example responses locally.

## Privacy and artifact hygiene

Run:

```bash
git grep -n -I -E '/(Users|home)/|HOME=/|api[_-]?key|secret|password|token|PRIVATE KEY|chat_id|auth\.json|\.env' -- $(git ls-files) || true
git ls-files --others --exclude-standard
git ls-files -ci --exclude-standard
git diff --check
```

Review all hits before public export. Private-only plan/checkpoint files may be excluded from a clean public export instead of rewritten in place.

## Verification bundle

Run from the repo root:

```bash
export AUTOMATION_KIT_PATH=../automation-kit
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m pytest -q
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m ruff check .
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" python -m mypy src
PYTHONPATH="$AUTOMATION_KIT_PATH/src:src" examples/run-sandbox-walkthrough.sh
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

## Publication gate

Stop before any of these until explicitly approved:

- existing repo visibility changed to public;
- clean public export repo created/pushed;
- release or tag created;
- live SaaS credentials/accounts connected;
- cloud deployment or public URL created;
- real client data used;
- external message or client handoff sent;
- external collaborator invited.
