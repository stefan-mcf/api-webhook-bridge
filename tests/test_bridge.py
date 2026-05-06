from __future__ import annotations

from api_webhook_bridge.bridge import bridge_event
from api_webhook_bridge.idempotency import InMemoryIdempotencyStore


def test_contact_event_maps_to_airtable_upsert_and_audit() -> None:
    event = {
        "type": "contact.created",
        "contact_id": "C-100",
        "email": "ALICE@example.com",
        "first_name": "Alice",
        "last_name": "Ng",
        "company": "Northwind",
    }

    result = bridge_event(event, idempotency_store=InMemoryIdempotencyStore())

    assert result["status"] == "mapped"
    assert result["source_event_type"] == "contact.created"
    assert result["destination_operations"][0]["system"] == "airtable"
    assert result["destination_operations"][0]["record_id"] == "contact:C-100"
    assert result["destination_operations"][0]["fields"]["Email"] == "ALICE@example.com"
    assert result["audit_log"][0]["live_services_used"] is False
    assert result["handoff_note"].startswith("Mapped contact.created")


def test_shopify_order_maps_to_slack_and_crm_operations() -> None:
    event = {
        "type": "order.created",
        "order_id": "O-200",
        "email": "buyer@example.com",
        "total_price": "149.00",
        "currency": "USD",
        "customer": {"first_name": "Sam", "last_name": "Rivera"},
    }

    result = bridge_event(event, idempotency_store=InMemoryIdempotencyStore())

    assert result["status"] == "mapped"
    assert [op["system"] for op in result["destination_operations"]] == ["slack", "crm"]
    assert result["fixture_safe"] is True
    assert result["live_services_used"] is False


def test_stripe_payment_maps_to_audit_and_slack_operations() -> None:
    event = {
        "type": "payment.succeeded",
        "event_id": "evt_300",
        "payment_intent": "pi_300",
        "customer_email": "payer@example.com",
        "amount": "149.00",
        "currency": "USD",
    }

    result = bridge_event(event, idempotency_store=InMemoryIdempotencyStore())

    assert result["status"] == "mapped"
    assert result["idempotency_key"] == "payment.succeeded:evt_300:pi_300"
    assert [op["system"] for op in result["destination_operations"]] == ["payment_audit", "slack"]


def test_unknown_event_routes_to_review_without_live_call() -> None:
    result = bridge_event(
        {"type": "deal.deleted", "deal_id": "D-1"}, idempotency_store=InMemoryIdempotencyStore()
    )

    assert result["status"] == "needs_review"
    assert result["destination_operations"] == []
    assert result["validation_errors"] == ["unsupported_event_type: deal.deleted"]
    assert result["audit_log"][0]["live_services_used"] is False


def test_missing_required_field_fails_cleanly() -> None:
    result = bridge_event(
        {"type": "contact.created", "contact_id": "C-101"},
        idempotency_store=InMemoryIdempotencyStore(),
    )

    assert result["status"] == "validation_failed"
    assert "missing_required_field: email" in result["validation_errors"]
    assert result["destination_operations"] == []
