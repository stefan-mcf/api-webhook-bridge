"""Structured local audit and dead-letter proof surfaces."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_DIR = REPO_ROOT / ".local" / "audit"


def stable_audit_id(event_type: str | None, status: str, idempotency_key: str | None = None) -> str:
    suffix = idempotency_key or "no-key"
    safe_event = event_type or "unknown"
    return f"audit:{safe_event}:{status}:{suffix}"


def stable_correlation_id(event_type: str | None, idempotency_key: str | None = None) -> str:
    suffix = idempotency_key or "no-key"
    safe_event = event_type or "unknown"
    return f"corr:{safe_event}:{suffix}"


def audit_event(
    *,
    event_type: str | None,
    mapping_name: str | None,
    status: str,
    destination_operation_count: int,
    idempotency_key: str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    return {
        "audit_id": stable_audit_id(event_type, status, idempotency_key),
        "correlation_id": stable_correlation_id(event_type, idempotency_key),
        "timestamp": "2026-05-06T00:00:00Z",
        "source": source or "unknown",
        "event_type": event_type,
        "mapping_name": mapping_name,
        "status": status,
        "destination_operation_count": destination_operation_count,
        "fixture_safe": True,
        "live_services_used": False,
    }


class AuditStore:
    """JSONL-backed local audit/dead-letter store for safe proof runs."""

    def __init__(self, root: Path = DEFAULT_AUDIT_DIR) -> None:
        self.root = root
        self.events_path = root / "events.jsonl"
        self.dead_letter_path = root / "dead-letter.jsonl"

    def append_event(self, event: dict[str, Any]) -> None:
        self._append(self.events_path, event)

    def append_dead_letter(self, event: dict[str, Any]) -> None:
        self._append(self.dead_letter_path, event)

    def read_events(self) -> list[dict[str, Any]]:
        return self._read(self.events_path)

    def read_dead_letters(self) -> list[dict[str, Any]]:
        return self._read(self.dead_letter_path)

    def clear(self) -> None:
        for path in (self.events_path, self.dead_letter_path):
            if path.exists():
                path.unlink()

    def _append(self, path: Path, event: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        record = dict(event)
        record.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def _read(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def dead_letter_record(
    *,
    event_type: str | None,
    status: str,
    reason: str,
    errors: list[str],
    mapping_name: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    record = audit_event(
        event_type=event_type,
        mapping_name=mapping_name,
        status=status,
        destination_operation_count=0,
        idempotency_key=idempotency_key,
    )
    record.update(
        {
            "reason": reason,
            "validation_errors": errors,
            "safe_to_retry": status != "unsupported_event_type",
            "retry_recommendation": "fix payload or mapping, then replay synthetic fixture",
            "manual_review_reason": reason,
        }
    )
    return record
