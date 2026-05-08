from __future__ import annotations

from fastapi.testclient import TestClient

from api_webhook_bridge.api import MAX_WEBHOOK_BODY_BYTES, app
from api_webhook_bridge.bridge import reset_default_state

client = TestClient(app)


def setup_function() -> None:
    reset_default_state()


def test_health_is_fixture_safe() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "fixture_safe": True, "live_services_used": False}


def test_named_routes_return_bridge_responses() -> None:
    cases = [
        (
            "/webhooks/hubspot-like",
            {
                "type": "contact.created",
                "contact_id": "C-100",
                "email": "ALICE@example.com",
                "first_name": "Alice",
                "last_name": "Ng",
                "company": "Northwind",
            },
            "airtable",
        ),
        (
            "/webhooks/shopify-like",
            {
                "type": "order.created",
                "order_id": "O-200",
                "email": "buyer@example.com",
                "total_price": "149.00",
                "currency": "USD",
                "customer": {"first_name": "Sam", "last_name": "Rivera"},
            },
            "slack",
        ),
        (
            "/webhooks/stripe-like",
            {
                "type": "payment.succeeded",
                "event_id": "evt_300",
                "payment_intent": "pi_300",
                "customer_email": "payer@example.com",
                "amount": "149.00",
                "currency": "USD",
            },
            "payment_audit",
        ),
    ]
    for path, payload, first_system in cases:
        response = client.post(path, json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "mapped"
        assert body["destination_operations"][0]["system"] == first_system
        assert body["live_services_used"] is False


def test_integrations_and_mappings_are_buyer_legible() -> None:
    integrations = client.get("/integrations").json()
    mappings = client.get("/mappings").json()

    assert "shopify-like" in integrations["sources"]
    assert integrations["automation_kit_backbone"]["backbone"] == "Automation Kit"
    assert len(mappings["mappings"]) == 3


def test_webhook_endpoint_rejects_non_object_payload() -> None:
    response = client.post("/webhooks/hubspot-like", json=["bad"])

    assert response.status_code == 422
    assert "object" in response.json()["detail"].lower()


def test_webhook_endpoint_rejects_invalid_json() -> None:
    response = client.post(
        "/webhooks/hubspot-like",
        content=b"{bad json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert "valid json" in response.json()["detail"].lower()


def test_webhook_endpoint_rejects_empty_body() -> None:
    response = client.post(
        "/webhooks/hubspot-like",
        content=b"",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert "valid json" in response.json()["detail"].lower()


def test_webhook_endpoint_accepts_body_at_exact_size_limit() -> None:
    prefix = b'{"type":"deal.deleted","pad":"'
    suffix = b'"}'
    payload = prefix + (b"a" * (MAX_WEBHOOK_BODY_BYTES - len(prefix) - len(suffix))) + suffix

    assert len(payload) == MAX_WEBHOOK_BODY_BYTES

    response = client.post(
        "/webhooks/hubspot-like",
        content=payload,
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "needs_review"


def test_webhook_endpoint_rejects_body_one_byte_over_size_limit() -> None:
    prefix = b'{"type":"deal.deleted","pad":"'
    suffix = b'"}'
    payload = prefix + (b"a" * (MAX_WEBHOOK_BODY_BYTES + 1 - len(prefix) - len(suffix))) + suffix

    assert len(payload) == MAX_WEBHOOK_BODY_BYTES + 1

    response = client.post(
        "/webhooks/hubspot-like",
        content=payload,
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert "64kb" in response.json()["detail"].lower()


def test_unknown_source_returns_404() -> None:
    response = client.post("/webhooks/missing", json={"type": "missing.event"})

    assert response.status_code == 404


def test_unknown_event_returns_safe_review_response() -> None:
    response = client.post("/webhooks/hubspot-like", json={"type": "deal.deleted"})

    assert response.status_code == 200
    assert response.json()["status"] == "needs_review"


def test_audit_endpoints_are_available() -> None:
    assert client.get("/audit/events").status_code == 200
    assert client.get("/audit/dead-letter").status_code == 200
