from __future__ import annotations

import pytest

from api_webhook_bridge.mapping import MappingError, apply_mapping, load_mapping, validate_event


def test_contact_mapping_transforms_visible_fields() -> None:
    config = load_mapping("hubspot-contact-to-airtable")
    event = {
        "type": "contact.created",
        "contact_id": "C-1",
        "email": "A@EXAMPLE.COM",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "company": "Math",
    }

    operations = apply_mapping(config, event)

    assert operations[0]["system"] == "airtable"
    assert operations[0]["record_id"] == "contact:C-1"
    assert operations[0]["fields"]["Name"] == "Ada Lovelace"


def test_missing_required_fields_are_reported() -> None:
    config = load_mapping("shopify-order-to-slack-crm")

    assert validate_event(config, {"type": "order.created", "order_id": "O-1"}) == [
        "missing_required_field: email",
        "missing_required_field: total_price",
        "missing_required_field: currency",
        "missing_required_field: customer.first_name",
        "missing_required_field: customer.last_name",
    ]


def test_optional_fields_can_be_absent() -> None:
    config = load_mapping("stripe-payment-to-audit-slack")
    event = {
        "type": "payment.succeeded",
        "event_id": "evt_1",
        "payment_intent": "pi_1",
        "customer_email": "payer@example.com",
        "amount": "42.00",
        "currency": "USD",
    }

    assert validate_event(config, event) == []
    assert apply_mapping(config, event)[0]["fields"]["Invoice ID"] == ""


def test_unknown_mapping_name_fails_clearly() -> None:
    with pytest.raises(MappingError, match="unknown_mapping"):
        load_mapping("missing")
