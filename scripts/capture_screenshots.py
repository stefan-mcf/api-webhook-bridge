from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageStat, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 1280
HEIGHT = 760
BG = (10, 15, 28)
PANEL = (17, 24, 39)
PANEL_2 = (25, 35, 56)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)
GREEN = (74, 222, 128)
BLUE = (96, 165, 250)
YELLOW = (250, 204, 21)
PINK = (244, 114, 182)
RED = (248, 113, 113)
BORDER = (51, 65, 85)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(34, bold=True)
SUBTITLE_FONT = font(18)
SMALL_FONT = font(16)
MONO_SMALL = font(15)


def run(cmd: list[str], *, max_lines: int = 14) -> list[str]:
    env = {**os.environ, "PYTHONPATH": os.environ.get("PYTHONPATH", "src")}
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True, env=env)
    combined = (proc.stdout + proc.stderr).strip().splitlines()
    return combined[:max_lines] or ["command completed with no output"]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def compact_json_lines(path: str, keys: list[str], *, max_items: int = 12) -> list[str]:
    data = load_json(path)
    lines: list[str] = []
    for key in keys:
        value = data.get(key)
        if isinstance(value, (dict, list)):
            encoded = json.dumps(value, sort_keys=True)
            lines.append(f"{key}={encoded[:96]}")
        else:
            lines.append(f"{key}={value}")
    return lines[:max_items]


def wrap_lines(lines: list[str], width: int) -> list[str]:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(
            textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False)
            or [line]
        )
    return wrapped


def draw_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    *,
    accent: tuple[int, int, int] = BLUE,
    code: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x1 + 8, y2), fill=accent)
    draw.text((x1 + 26, y1 + 20), title, font=SUBTITLE_FONT, fill=accent)
    y = y1 + 58
    selected_font = MONO_SMALL if code else SMALL_FONT
    usable_width = max(220, x2 - x1 - 70)
    approx_char_px = 9 if code else 10
    max_chars = max(34, usable_width // approx_char_px)
    for line in wrap_lines(lines, max_chars)[:18]:
        fill = TEXT
        if line.startswith(("PASS", "✓", "fixture_safe=true", "live_services_used=false")):
            fill = GREEN
        elif line.startswith(("REFUSE", "unsafe", "blocked")) or "FAILED" in line:
            fill = RED
        elif line.startswith(("$", "python", "PYTHONPATH")):
            fill = YELLOW
        draw.text((x1 + 26, y), line, font=selected_font, fill=fill)
        y += 24 if code else 26
        if y > y2 - 34:
            break


def render(
    path: Path,
    title: str,
    subtitle: str,
    panels: list[dict[str, Any]],
    footer: str = "fixture_safe=true  live_services_used=false  synthetic_data_only=true",
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    for x in range(0, WIDTH, 80):
        draw.line((x, 0, x, HEIGHT), fill=(15, 23, 42))
    for y in range(0, HEIGHT, 80):
        draw.line((0, y, WIDTH, y), fill=(15, 23, 42))

    draw.rounded_rectangle(
        (30, 28, WIDTH - 30, 116), radius=24, fill=PANEL_2, outline=BORDER, width=2
    )
    draw.text((58, 48), title, font=TITLE_FONT, fill=TEXT)
    draw.text((60, 90), subtitle, font=SUBTITLE_FONT, fill=MUTED)
    for panel in panels:
        draw_panel(
            draw,
            panel["box"],
            str(panel["title"]),
            list(panel["lines"]),
            accent=panel.get("accent", BLUE),
            code=bool(panel.get("code", False)),
        )

    draw.rounded_rectangle(
        (30, HEIGHT - 54, WIDTH - 30, HEIGHT - 18), radius=16, fill=PANEL_2, outline=BORDER, width=1
    )
    draw.text((54, HEIGHT - 45), footer, font=SMALL_FONT, fill=GREEN)

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Proof", f"{title}\n{subtitle}\n{footer}")
    image.save(path, pnginfo=metadata, optimize=True)

    stat = ImageStat.Stat(image)
    if path.stat().st_size < 25_000 or max(stat.stddev) < 20:
        raise RuntimeError(
            f"screenshot may be unreadable/blank: {path} "
            f"size={path.stat().st_size} stddev={stat.stddev}"
        )


def main() -> None:
    py = sys.executable
    contact = load_json("examples/input/contact-created.json")
    payment = load_json("examples/input/stripe-payment-succeeded.json")

    health = compact_json_lines(
        "examples/api-responses/health.json",
        ["status", "fixture_safe", "live_services_used"],
    )
    hubspot = compact_json_lines(
        "examples/api-responses/hubspot-contact-response.json",
        ["status", "source_event_type", "mapping_name", "safe_to_retry", "duplicate", "audit_id"],
    )
    shopify = compact_json_lines(
        "examples/api-responses/shopify-order-response.json",
        [
            "status",
            "source_event_type",
            "mapping_name",
            "destination_operations",
            "idempotency_key",
        ],
    )
    stripe = compact_json_lines(
        "examples/api-responses/stripe-payment-response.json",
        [
            "status",
            "source_event_type",
            "mapping_name",
            "destination_operations",
            "idempotency_key",
        ],
    )
    duplicate = compact_json_lines(
        "examples/api-responses/stripe-payment-duplicate-response.json",
        ["status", "duplicate", "idempotency_key", "retry_policy", "audit_id"],
    )
    dead_letter = compact_json_lines(
        "examples/api-responses/dead-letter-response.json",
        ["status", "validation_errors", "retry_policy", "safe_to_retry", "audit_id"],
    )
    mapping = compact_json_lines(
        "configs/mappings/hubspot-contact-to-airtable.json",
        ["name", "source", "source_event_type", "destination", "required_fields"],
    )
    pytest_lines = run(
        [py, "-m", "pytest", "-q", "tests", "-k", "not screenshots"], max_lines=10
    )

    render(
        OUT / "01-flow-overview.png",
        "API Webhook Bridge Flow",
        "Synthetic source events become mapped operations and audit evidence.",
        [
            {
                "box": (52, 148, 410, 628),
                "title": "Sources",
                "accent": BLUE,
                "lines": [
                    "HubSpot-like contact",
                    "Shopify-like order",
                    "Stripe-like payment",
                    "Custom webhook pattern",
                    "Invalid event fixture",
                ],
            },
            {
                "box": (462, 148, 820, 628),
                "title": "Bridge",
                "accent": YELLOW,
                "lines": [
                    "FastAPI endpoint",
                    "schema validation",
                    "mapping JSON review",
                    "idempotency key",
                    "downstream handoff evidence",
                ],
            },
            {
                "box": (872, 148, 1230, 628),
                "title": "Evidence",
                "accent": GREEN,
                "lines": [
                    "response JSON files",
                    "audit event log",
                    "dead-letter record",
                    "handoff note",
                    "quality gate proof",
                ],
            },
        ],
    )
    render(
        OUT / "02-openapi-webhook-endpoints.png",
        "Local API Surface",
        "OpenAPI routes expose only fixture-safe bridge, audit, and review surfaces.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Endpoints",
                "accent": BLUE,
                "lines": [
                    "GET /health",
                    "GET /integrations",
                    "GET /mappings",
                    "POST /webhooks/hubspot-like",
                    "POST /webhooks/shopify-like",
                    "POST /webhooks/stripe-like",
                    "GET /audit/events",
                    "GET /audit/dead-letter",
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Health contract",
                "accent": GREEN,
                "code": True,
                "lines": health,
            },
        ],
    )
    render(
        OUT / "03-contact-bridge-proof.png",
        "Contact Bridge Proof",
        "A HubSpot-like contact fixture maps to an Airtable-style upsert without live credentials.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Fixture",
                "accent": PINK,
                "code": True,
                "lines": [
                    f"id={contact.get('id')}",
                    f"type={contact.get('type')}",
                    "target=Airtable-style upsert",
                    "required=email, firstname, lastname",
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Response excerpt",
                "accent": GREEN,
                "code": True,
                "lines": hubspot,
            },
        ],
    )
    render(
        OUT / "04-mapping-config.png",
        "Reviewable Mapping Config",
        "Field mapping stays explicit in JSON so a reviewer can approve schema changes first.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Mapping",
                "accent": YELLOW,
                "code": True,
                "lines": mapping,
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Review contract",
                "accent": BLUE,
                "lines": [
                    "source field names are visible",
                    "destination operation shape is visible",
                    "required fields are listed",
                    "handoff note is fixture-backed",
                    "live credential work remains gated",
                ],
            },
        ],
    )
    render(
        OUT / "05-idempotency-audit.png",
        "Idempotency And Audit Proof",
        "Repeated Stripe-like payments are detected as duplicates and kept in audit evidence.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "First payment",
                "accent": GREEN,
                "code": True,
                "lines": [f"id={payment.get('id')}", *stripe[:8]],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Duplicate replay",
                "accent": RED,
                "code": True,
                "lines": duplicate,
            },
        ],
    )
    render(
        OUT / "06-dead-letter.png",
        "Dead-Letter Proof",
        "Invalid contact payloads route to review instead of silent delivery.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Invalid input",
                "accent": RED,
                "lines": [
                    "contact.created fixture",
                    "missing required field(s)",
                    "no destination operation prepared",
                    "manual review record created",
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Response excerpt",
                "accent": YELLOW,
                "code": True,
                "lines": dead_letter,
            },
        ],
    )
    render(
        OUT / "07-quality-gates.png",
        "Quality Gate Proof",
        "Tests run against the current local bridge package before screenshots are accepted.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Command",
                "accent": YELLOW,
                "code": True,
                "lines": [
                    "$ PYTHONPATH=src python -m pytest -q tests -k 'not screenshots'",
                    "$ python -m ruff check .",
                    "$ python -m mypy src",
                    "$ python scripts/capture_screenshots.py",
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Pytest excerpt",
                "accent": GREEN,
                "code": True,
                "lines": pytest_lines,
            },
        ],
    )
    render(
        OUT / "08-debugger-handoff.png",
        "Debugger Handoff Surface",
        "Bridge proof covers the green path; Automation Debugger covers repair after failure.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Bridge milestone",
                "accent": GREEN,
                "lines": [
                    "valid event accepted",
                    "mapping reviewed",
                    "destination-shaped operations",
                    "audit evidence returned",
                    "dead-letter invalid payloads",
                ],
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Repair milestone",
                "accent": BLUE,
                "lines": [
                    "failed event exported",
                    "root cause diagnosed",
                    "safe replay decided",
                    "fix report generated",
                    "human review before live retry",
                ],
            },
        ],
    )
    render(
        OUT / "09-mock-job-01-bridge-proof.png",
        "Mock Job 01 Bridge Proof",
        "Shopify order and Stripe payment intake are verified before Airtable/Sheets output proof.",
        [
            {
                "box": (52, 148, 604, 628),
                "title": "Shopify order intake",
                "accent": BLUE,
                "code": True,
                "lines": shopify,
            },
            {
                "box": (650, 148, 1230, 628),
                "title": "Stripe payment intake",
                "accent": GREEN,
                "code": True,
                "lines": [*stripe[:7], "duplicate replay covered in 05-idempotency-audit.png"],
            },
        ],
    )


if __name__ == "__main__":
    main()
