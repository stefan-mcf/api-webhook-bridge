from __future__ import annotations

from api_webhook_bridge.backbone import automation_kit_contract, load_backbone_workflow


def test_automation_kit_modules_are_importable() -> None:
    contract = automation_kit_contract()

    assert contract["backbone"] == "Automation Kit"
    assert "auto_kit.pattern_runner" in contract["modules"]
    assert "auto_kit.mock_clients" in contract["modules"]
    assert "auto_kit.workflow_schema" in contract["modules"]
    assert contract["fixture_safe"] is True
    assert contract["live_services_used"] is False


def test_webhook_router_workflow_can_be_loaded_from_backbone() -> None:
    workflow = load_backbone_workflow("webhook-router")

    assert workflow.name
    assert workflow.nodes
