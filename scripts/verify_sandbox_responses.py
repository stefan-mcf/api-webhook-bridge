#!/usr/bin/env python3
"""Verify saved sandbox walkthrough responses match the buyer-proof contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESPONSE_DIR = ROOT / "examples" / "api-responses"

EXPECTED: dict[str, dict[str, Any]] = {
    "health.json": {"status": "ok"},
    "hubspot-contact-response.json": {
        "status": "mapped",
        "source_event_type": "contact.created",
        "duplicate": False,
        "mapping_name": "hubspot-contact-to-airtable",
    },
    "shopify-order-response.json": {
        "status": "mapped",
        "source_event_type": "order.created",
        "duplicate": False,
        "mapping_name": "shopify-order-to-slack-crm",
    },
    "stripe-payment-response.json": {
        "status": "mapped",
        "source_event_type": "payment.succeeded",
        "duplicate": False,
        "mapping_name": "stripe-payment-to-audit-slack",
    },
    "stripe-payment-duplicate-response.json": {
        "status": "duplicate_ignored",
        "source_event_type": "payment.succeeded",
        "duplicate": True,
        "mapping_name": "stripe-payment-to-audit-slack",
    },
    "dead-letter-response.json": {
        "status": "validation_failed",
        "source_event_type": "contact.created",
        "duplicate": False,
        "mapping_name": "hubspot-contact-to-airtable",
    },
}

REQUIRED_FILES = [
    "health.json",
    "integrations.json",
    "mappings.json",
    "hubspot-contact-response.json",
    "shopify-order-response.json",
    "stripe-payment-response.json",
    "stripe-payment-duplicate-response.json",
    "dead-letter-response.json",
    "audit-events.json",
    "dead-letter.json",
]


def load_response(filename: str) -> dict[str, Any]:
    path = RESPONSE_DIR / filename
    if not path.exists():
        raise AssertionError(f"missing response artifact: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise AssertionError(f"response artifact is not a JSON object: {path}")
    return data


def assert_fixture_safe(filename: str, data: dict[str, Any]) -> None:
    if data.get("fixture_safe") is not True:
        raise AssertionError(f"{filename}: fixture_safe must be true")
    if data.get("live_services_used") is not False:
        raise AssertionError(f"{filename}: live_services_used must be false")


def assert_subset(filename: str, data: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, value in expected.items():
        if data.get(key) != value:
            raise AssertionError(f"{filename}: expected {key}={value!r}, got {data.get(key)!r}")


def main() -> None:
    for filename in REQUIRED_FILES:
        data = load_response(filename)
        assert_fixture_safe(filename, data)
        if filename in EXPECTED:
            assert_subset(filename, data, EXPECTED[filename])

    mappings = load_response("mappings.json")["mappings"]
    mapping_names = {mapping["name"] for mapping in mappings}
    required_mappings = {
        "hubspot-contact-to-airtable",
        "shopify-order-to-slack-crm",
        "stripe-payment-to-audit-slack",
    }
    if not required_mappings.issubset(mapping_names):
        missing = sorted(required_mappings - mapping_names)
        raise AssertionError(f"missing required mapping names: {missing}")

    audit_events = load_response("audit-events.json")["events"]
    event_status_pairs = {(event["event_type"], event["status"]) for event in audit_events}
    required_event_status_pairs = {
        ("order.created", "mapped"),
        ("payment.succeeded", "mapped"),
        ("payment.succeeded", "duplicate_ignored"),
    }
    if not required_event_status_pairs.issubset(event_status_pairs):
        missing = sorted(required_event_status_pairs - event_status_pairs)
        raise AssertionError(f"missing audit event/status pairs: {missing}")

    dead_letters = load_response("dead-letter.json")["dead_letter"]
    if not dead_letters:
        raise AssertionError("dead-letter.json must include at least one validation failure")

    print(f"Sandbox response verification passed for {len(REQUIRED_FILES)} artifacts")


if __name__ == "__main__":
    main()
