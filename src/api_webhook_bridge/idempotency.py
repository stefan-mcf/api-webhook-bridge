"""Local idempotency proof stores for fixture-safe webhook runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class InMemoryIdempotencyStore:
    """Tiny in-memory store used by tests and local proof runs."""

    def __init__(self) -> None:
        self._responses: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        existing = self._responses.get(key)
        return dict(existing) if existing is not None else None

    def set(self, key: str, response: dict[str, Any]) -> None:
        self._responses[key] = dict(response)

    def clear(self) -> None:
        self._responses.clear()


class JsonlIdempotencyStore(InMemoryIdempotencyStore):
    """Optional JSONL-backed local proof store under ignored .local paths."""

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                key = str(record["idempotency_key"])
                response = record.get("response")
                if isinstance(response, dict):
                    self._responses[key] = response

    def set(self, key: str, response: dict[str, Any]) -> None:
        super().set(key, response)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps({"idempotency_key": key, "response": response}, sort_keys=True) + "\n"
            )


def duplicate_response(existing: dict[str, Any]) -> dict[str, Any]:
    """Return a stable duplicate-safe response derived from the first delivery."""

    response = dict(existing)
    response["duplicate"] = True
    response["status"] = "duplicate_ignored"
    response["safe_to_retry"] = True
    response["manual_review_reason"] = ""
    response["retry_recommendation"] = (
        "duplicate delivery recognized; no destination operation repeated"
    )
    return response
