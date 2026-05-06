"""FastAPI surface for the fixture-safe bridge proof."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request

from api_webhook_bridge.audit import AuditStore
from api_webhook_bridge.backbone import automation_kit_contract
from api_webhook_bridge.bridge import bridge_event
from api_webhook_bridge.mapping import list_mappings

app = FastAPI(
    title="API Webhook Bridge",
    version="0.2.0",
    description="Fixture-safe Automation Kit backed API/webhook bridge proof.",
)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "fixture_safe": True, "live_services_used": False}


@app.get("/integrations")
def integrations() -> dict[str, Any]:
    return {
        "sources": ["hubspot-like", "shopify-like", "stripe-like"],
        "destinations": ["airtable-like", "crm-like", "slack-like", "payment-audit-like"],
        "automation_kit_backbone": automation_kit_contract(),
        "fixture_safe": True,
        "live_services_used": False,
    }


@app.get("/mappings")
def mappings() -> dict[str, Any]:
    return {"mappings": list_mappings(), "fixture_safe": True, "live_services_used": False}


async def _payload(request: Request) -> dict[str, Any]:
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="Webhook payload must be a JSON object")
    return body


@app.post("/webhooks/hubspot-like")
async def hubspot_like(request: Request) -> dict[str, Any]:
    return bridge_event(await _payload(request), audit_store=AuditStore())


@app.post("/webhooks/shopify-like")
async def shopify_like(request: Request) -> dict[str, Any]:
    return bridge_event(await _payload(request), audit_store=AuditStore())


@app.post("/webhooks/stripe-like")
async def stripe_like(request: Request) -> dict[str, Any]:
    return bridge_event(await _payload(request), audit_store=AuditStore())


@app.post("/webhooks/{source}")
async def webhook(source: str, request: Request) -> dict[str, Any]:
    allowed = {"hubspot-like", "shopify-like", "stripe-like"}
    if source not in allowed:
        raise HTTPException(status_code=404, detail=f"Unknown source: {source}")
    return bridge_event(await _payload(request), audit_store=AuditStore())


@app.get("/audit/events")
def audit_events() -> dict[str, Any]:
    store = AuditStore()
    return {"events": store.read_events(), "fixture_safe": True, "live_services_used": False}


@app.get("/audit/dead-letter")
def audit_dead_letter() -> dict[str, Any]:
    store = AuditStore()
    return {
        "dead_letter": store.read_dead_letters(),
        "fixture_safe": True,
        "live_services_used": False,
    }
