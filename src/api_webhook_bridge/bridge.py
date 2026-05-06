"""Fixture-safe source-to-destination webhook bridge."""

from __future__ import annotations

from typing import Any

from api_webhook_bridge.audit import AuditStore, audit_event, dead_letter_record
from api_webhook_bridge.backbone import prepare_crm_upsert, prepare_slack_alert
from api_webhook_bridge.idempotency import InMemoryIdempotencyStore, duplicate_response
from api_webhook_bridge.mapping import (
    MappingConfig,
    MappingError,
    apply_mapping,
    get_mapping_for_event,
    idempotency_key,
    validate_event,
)

_DEFAULT_STORE = InMemoryIdempotencyStore()


def reset_default_state() -> None:
    """Clear default in-memory idempotency state used by API tests/proofs."""

    _DEFAULT_STORE.clear()


def _unknown_response(
    event_type: str | None, errors: list[str], audit_store: AuditStore | None
) -> dict[str, Any]:
    audit = dead_letter_record(
        event_type=event_type,
        status="needs_review",
        reason="unsupported event type",
        errors=errors,
    )
    if audit_store is not None:
        audit_store.append_dead_letter(audit)
    return {
        "status": "needs_review",
        "source_event_type": event_type,
        "mapped_fields": {},
        "destination_operations": [],
        "validation_errors": errors,
        "validation_summary": {"status": "failed", "errors": errors},
        "retry_policy": "manual_review_before_retry",
        "retry_recommendation": "add/approve a mapping before replay",
        "safe_to_retry": False,
        "manual_review_reason": "unsupported event type",
        "audit_id": audit["audit_id"],
        "correlation_id": audit["correlation_id"],
        "audit_log": [audit],
        "handoff_note": "Unsupported event type; add a mapping before any live delivery.",
        "fixture_safe": True,
        "live_services_used": False,
    }


def _validation_failed_response(
    event_type: str | None,
    config: MappingConfig,
    errors: list[str],
    key: str,
    audit_store: AuditStore | None,
) -> dict[str, Any]:
    audit = dead_letter_record(
        event_type=event_type,
        status="validation_failed",
        reason="Required fields are missing; no destination operation was prepared.",
        errors=errors,
        mapping_name=config.name,
        idempotency_key=key,
    )
    if audit_store is not None:
        audit_store.append_dead_letter(audit)
    return {
        "status": "validation_failed",
        "source_event_type": event_type,
        "mapping_name": config.name,
        "mapped_fields": {},
        "destination_operations": [],
        "validation_errors": errors,
        "validation_summary": {"status": "failed", "errors": errors},
        "retry_policy": "fix_payload_then_retry",
        "retry_recommendation": "fix missing fields and replay the event",
        "safe_to_retry": True,
        "manual_review_reason": "required fields missing",
        "idempotency_key": key,
        "duplicate": False,
        "audit_id": audit["audit_id"],
        "correlation_id": audit["correlation_id"],
        "audit_log": [audit],
        "handoff_note": "Required fields are missing; no destination operation was prepared.",
        "fixture_safe": True,
        "live_services_used": False,
    }


def _backbone_enrich_operation(operation: dict[str, Any]) -> dict[str, Any]:
    """Use Automation Kit mock clients for deterministic destination preparation proof."""

    system = str(operation.get("system", ""))
    enriched = dict(operation)
    if system in {"airtable", "crm"} and isinstance(operation.get("fields"), dict):
        fields = dict(operation["fields"])
        email = str(fields.get("Email") or fields.get("email") or "unknown@example.com")
        enriched["mock_client_record"] = prepare_crm_upsert(email, fields)
    if system == "slack":
        channel = str(operation.get("channel", "#ops"))
        text = str(operation.get("text", "fixture-safe notification"))
        severity = str(operation.get("severity", "info"))
        enriched["mock_client_record"] = prepare_slack_alert(channel, text, severity)
    return enriched


def bridge_event(
    event: dict[str, Any],
    *,
    idempotency_store: InMemoryIdempotencyStore | None = None,
    audit_store: AuditStore | None = None,
) -> dict[str, Any]:
    """Map one synthetic source event into destination operations."""

    store = idempotency_store or _DEFAULT_STORE
    event_type = event.get("type")
    try:
        config = get_mapping_for_event(str(event_type) if event_type is not None else None)
    except MappingError as exc:
        return _unknown_response(
            str(event_type) if event_type is not None else None, [str(exc)], audit_store
        )

    key = idempotency_key(config, event)
    existing = store.get(key)
    if existing is not None:
        duplicate = duplicate_response(existing)
        audit = audit_event(
            event_type=config.source_event_type,
            mapping_name=config.name,
            status="duplicate_ignored",
            destination_operation_count=0,
            idempotency_key=key,
            source=config.source,
        )
        duplicate["audit_log"] = [audit]
        duplicate["audit_id"] = audit["audit_id"]
        duplicate["correlation_id"] = audit["correlation_id"]
        if audit_store is not None:
            audit_store.append_event(audit)
        return duplicate

    errors = validate_event(config, event)
    if errors:
        return _validation_failed_response(str(event_type), config, errors, key, audit_store)

    operations = [_backbone_enrich_operation(op) for op in apply_mapping(config, event)]
    audit = audit_event(
        event_type=config.source_event_type,
        mapping_name=config.name,
        status="mapped",
        destination_operation_count=len(operations),
        idempotency_key=key,
        source=config.source,
    )
    response = {
        "status": "mapped",
        "source_event_type": config.source_event_type,
        "mapping_name": config.name,
        "mapped_fields": operations[0].get("fields", {}) if operations else {},
        "destination_operations": operations,
        "validation_errors": [],
        "validation_summary": {
            "status": "passed",
            "message": config.validation_summary,
            "required_fields_checked": config.required_fields,
        },
        "retry_policy": "idempotent_by_source_event_key",
        "retry_recommendation": (
            "safe to replay; duplicate deliveries are detected by idempotency_key"
        ),
        "safe_to_retry": True,
        "manual_review_reason": "",
        "idempotency_key": key,
        "duplicate": False,
        "audit_id": audit["audit_id"],
        "correlation_id": audit["correlation_id"],
        "audit_log": [audit],
        "handoff_note": config.handoff_note_template,
        "fixture_safe": True,
        "live_services_used": False,
    }
    store.set(key, response)
    if audit_store is not None:
        audit_store.append_event(audit)
    return response
