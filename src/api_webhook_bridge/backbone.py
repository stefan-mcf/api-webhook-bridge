"""Automation Kit backbone imports for the API/webhook bridge spoke.

This is the only production module that imports Automation Kit directly. Keeping the
boundary here makes the spoke's reusable-framework dependency explicit while leaving
case-study mapping code focused on buyer-specific API/webhook flows.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

from auto_kit.mock_clients import MockCRMClient, MockSlackClient
from auto_kit.pattern_runner import discover_patterns, load_workflow_json
from auto_kit.workflow_schema import WorkflowJSON

AUTOMATION_KIT_PATTERNS = Path(
    os.environ.get(
        "AUTOMATION_KIT_PATTERNS",
        Path(__file__).resolve().parents[3] / "automation-kit" / "patterns",
    )
)


def automation_kit_contract() -> dict[str, Any]:
    """Return a small, testable description of the Automation Kit backbone in use."""

    patterns = [path.name for path in discover_patterns(AUTOMATION_KIT_PATTERNS)]
    return {
        "backbone": "Automation Kit",
        "modules": [
            "auto_kit.pattern_runner",
            "auto_kit.mock_clients",
            "auto_kit.workflow_schema",
        ],
        "patterns_available": patterns,
        "uses_mock_clients": True,
        "fixture_safe": True,
        "live_services_used": False,
    }


def load_backbone_workflow(pattern_name: str) -> WorkflowJSON:
    """Load one Automation Kit workflow by name for documentation/contract proof."""

    return load_workflow_json(AUTOMATION_KIT_PATTERNS / pattern_name)


def prepare_crm_upsert(email: str, data: dict[str, Any]) -> dict[str, Any]:
    """Prepare a deterministic CRM-style upsert through Automation Kit's mock client."""

    client = MockCRMClient()
    return cast(dict[str, Any], client.upsert_contact(email, dict(data)))


def prepare_slack_alert(channel: str, text: str, severity: str = "info") -> dict[str, Any]:
    """Prepare a deterministic Slack-style alert through Automation Kit's mock client."""

    client = MockSlackClient()
    return cast(dict[str, Any], client.send_alert(channel=channel, text=text, severity=severity))
