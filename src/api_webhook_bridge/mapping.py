"""Visible source-to-destination mapping contract for fixture-safe proof flows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MAPPINGS_DIR = REPO_ROOT / "configs" / "mappings"


class MappingError(ValueError):
    """Raised when a mapping config cannot safely transform an event."""


@dataclass(frozen=True)
class MappingConfig:
    """Validated mapping configuration loaded from JSON."""

    name: str
    source: str
    source_event_type: str
    idempotency_fields: list[str]
    required_fields: list[str]
    optional_fields: list[str]
    destination_operations: list[dict[str, Any]]
    validation_summary: str
    handoff_note_template: str


def _require_str_list(data: dict[str, Any], key: str) -> list[str]:
    raw = data.get(key)
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise MappingError(f"mapping field {key!r} must be a list of strings")
    return list(raw)


def load_mapping(name: str) -> MappingConfig:
    """Load and validate a named mapping config from configs/mappings."""

    if "/" in name or ".." in name:
        raise MappingError(f"unknown_mapping: {name}")
    path = MAPPINGS_DIR / f"{name}.json"
    if not path.exists():
        raise MappingError(f"unknown_mapping: {name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    destination_operations = data.get("destination_operations")
    if not isinstance(destination_operations, list) or not all(
        isinstance(item, dict) for item in destination_operations
    ):
        raise MappingError("mapping field destination_operations must be a list of objects")
    return MappingConfig(
        name=str(data["name"]),
        source=str(data["source"]),
        source_event_type=str(data["source_event_type"]),
        idempotency_fields=_require_str_list(data, "idempotency_fields"),
        required_fields=_require_str_list(data, "required_fields"),
        optional_fields=_require_str_list(data, "optional_fields"),
        destination_operations=list(destination_operations),
        validation_summary=str(data["validation_summary"]),
        handoff_note_template=str(data["handoff_note_template"]),
    )


def list_mappings() -> list[dict[str, Any]]:
    """Return buyer-readable summaries for all local mapping configs."""

    mappings: list[dict[str, Any]] = []
    for path in sorted(MAPPINGS_DIR.glob("*.json")):
        config = load_mapping(path.stem)
        mappings.append(
            {
                "name": config.name,
                "source": config.source,
                "source_event_type": config.source_event_type,
                "destination_systems": [
                    str(op.get("system", "unknown")) for op in config.destination_operations
                ],
                "required_fields": config.required_fields,
                "fixture_safe": True,
                "live_services_used": False,
            }
        )
    return mappings


def get_mapping_for_event(event_type: str | None) -> MappingConfig:
    """Find a mapping config by source event type."""

    for path in sorted(MAPPINGS_DIR.glob("*.json")):
        config = load_mapping(path.stem)
        if config.source_event_type == event_type:
            return config
    raise MappingError(f"unsupported_event_type: {event_type}")


def read_field(event: dict[str, Any], field_path: str) -> Any:
    """Read dot-separated fields from a JSON-like event dict."""

    value: Any = event
    for part in field_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def render_template(template: str, event: dict[str, Any]) -> str:
    """Render {field.path} placeholders using event values."""

    result = template
    for token in sorted(set(part.split("}", 1)[0] for part in result.split("{")[1:])):
        value = read_field(event, token)
        result = result.replace("{" + token + "}", "" if value is None else str(value))
    return result


def validate_event(config: MappingConfig, event: dict[str, Any]) -> list[str]:
    """Return validation errors for missing required fields."""

    errors: list[str] = []
    for field in config.required_fields:
        value = read_field(event, field)
        if value is None or value == "":
            errors.append(f"missing_required_field: {field}")
    return errors


def idempotency_key(config: MappingConfig, event: dict[str, Any]) -> str:
    """Build a deterministic idempotency key from configured source fields."""

    parts: list[str] = [config.source_event_type]
    for field in config.idempotency_fields:
        value = read_field(event, field)
        if value is not None:
            parts.append(str(value))
    return ":".join(parts)


def apply_mapping(config: MappingConfig, event: dict[str, Any]) -> list[dict[str, Any]]:
    """Prepare deterministic destination operations from a mapping config."""

    operations: list[dict[str, Any]] = []
    for operation in config.destination_operations:
        prepared: dict[str, Any] = {}
        for key, value in operation.items():
            if isinstance(value, str):
                prepared[key] = render_template(value, event)
            elif isinstance(value, dict):
                prepared[key] = {
                    sub_key: render_template(str(sub_value), event)
                    for sub_key, sub_value in value.items()
                }
            else:
                prepared[key] = value
        operations.append(prepared)
    return operations
