from __future__ import annotations

from api_webhook_bridge.bridge import bridge_event
from api_webhook_bridge.idempotency import InMemoryIdempotencyStore


def test_duplicate_contact_delivery_is_detected() -> None:
    store = InMemoryIdempotencyStore()
    event = {
        "type": "contact.created",
        "contact_id": "C-100",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Ng",
    }

    first = bridge_event(event, idempotency_store=store)
    second = bridge_event(event, idempotency_store=store)

    assert first["duplicate"] is False
    assert second["duplicate"] is True
    assert second["status"] == "duplicate_ignored"
    assert second["idempotency_key"] == first["idempotency_key"]


def test_duplicate_stripe_payment_delivery_is_safe() -> None:
    store = InMemoryIdempotencyStore()
    event = {
        "type": "payment.succeeded",
        "event_id": "evt_300",
        "payment_intent": "pi_300",
        "customer_email": "payer@example.com",
        "amount": "149.00",
        "currency": "USD",
    }

    bridge_event(event, idempotency_store=store)
    duplicate = bridge_event(event, idempotency_store=store)

    assert duplicate["duplicate"] is True
    assert duplicate["safe_to_retry"] is True
    assert duplicate["retry_recommendation"].startswith("duplicate delivery recognized")
