from __future__ import annotations

from api_webhook_bridge.audit import AuditStore
from api_webhook_bridge.bridge import bridge_event
from api_webhook_bridge.idempotency import InMemoryIdempotencyStore


def test_missing_required_fields_create_dead_letter(tmp_path) -> None:  # type: ignore[no-untyped-def]
    store = AuditStore(tmp_path)

    result = bridge_event(
        {"type": "contact.created", "contact_id": "C-101"},
        idempotency_store=InMemoryIdempotencyStore(),
        audit_store=store,
    )

    dead_letters = store.read_dead_letters()
    assert result["status"] == "validation_failed"
    assert dead_letters[0]["status"] == "validation_failed"
    assert "missing_required_field: email" in dead_letters[0]["validation_errors"]


def test_unknown_event_creates_dead_letter(tmp_path) -> None:  # type: ignore[no-untyped-def]
    store = AuditStore(tmp_path)

    result = bridge_event(
        {"type": "deal.deleted"}, idempotency_store=InMemoryIdempotencyStore(), audit_store=store
    )

    assert result["status"] == "needs_review"
    assert store.read_dead_letters()[0]["manual_review_reason"] == "unsupported event type"
