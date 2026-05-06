from __future__ import annotations

from api_webhook_bridge.audit import AuditStore
from api_webhook_bridge.bridge import bridge_event
from api_webhook_bridge.idempotency import InMemoryIdempotencyStore


def test_success_audit_event_is_written(tmp_path) -> None:  # type: ignore[no-untyped-def]
    store = AuditStore(tmp_path)
    event = {
        "type": "order.created",
        "order_id": "O-200",
        "email": "buyer@example.com",
        "total_price": "149.00",
        "currency": "USD",
        "customer": {"first_name": "Sam", "last_name": "Rivera"},
    }

    result = bridge_event(event, idempotency_store=InMemoryIdempotencyStore(), audit_store=store)

    events = store.read_events()
    assert result["audit_id"] == events[0]["audit_id"]
    assert events[0]["correlation_id"].startswith("corr:order.created")
    assert events[0]["destination_operation_count"] == 2
    assert events[0]["fixture_safe"] is True
