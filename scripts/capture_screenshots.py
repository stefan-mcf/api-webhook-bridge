from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageStat, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 1400
HEIGHT = 800
BG = (11, 17, 32)
PANEL = (17, 24, 39)
PANEL_2 = (24, 34, 53)
TEXT = (229, 231, 235)
MUTED = (148, 163, 184)
BLUE = (96, 165, 250)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
BORDER = (51, 65, 85)

HEADER_BOX = (32, 28, 1368, 122)
FOOTER_BOX = (32, 730, 1368, 772)
TWO_COLUMN_BOXES = ((52, 154, 674, 670), (726, 154, 1348, 670))
THREE_COLUMN_BOXES = (
    (52, 154, 446, 670),
    (503, 154, 897, 670),
    (954, 154, 1348, 670),
)


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
PANEL_TITLE_FONT = font(18, bold=True)
BODY_FONT = font(16)
MONO_FONT = font(15)


def run(cmd: list[str], *, max_lines: int = 30) -> list[str]:
    env = {
        **os.environ,
        "PYTHONPATH": os.environ.get("PYTHONPATH", "src"),
        "PYTHONWARNINGS": "ignore",
    }
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True, env=env)
    combined = (proc.stdout + proc.stderr).strip().splitlines()
    return combined[:max_lines] or ["command completed"]


def passed_count(lines: list[str]) -> int:
    summary = next((line for line in reversed(lines) if " passed" in line), "")
    match = re.search(r"(?P<passed>\d+) passed", summary)
    if not match:
        raise RuntimeError(f"unable to read pytest result from: {lines!r}")
    return int(match.group("passed"))


def validation_summary(core_lines: list[str], image_lines: list[str]) -> list[str]:
    core = passed_count(core_lines)
    image_checks = passed_count(image_lines)
    return [
        f"core checks: {core} passed",
        f"image checks: {image_checks} passed",
        f"full suite: {core + image_checks} passed",
    ]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def response_summary(path: str) -> list[str]:
    data = load_json(path)
    operations = data.get("destination_operations")
    operation_list = operations if isinstance(operations, list) else []
    systems = [str(item.get("system")) for item in operation_list if isinstance(item, dict)]
    return [
        f"status={data.get('status')}",
        f"mapping={data.get('mapping_name')}",
        f"operation_count={len(operation_list)}",
        f"destination_systems={','.join(systems) or 'none'}",
        f"duplicate={data.get('duplicate')}",
        f"safe_to_retry={data.get('safe_to_retry')}",
        f"audit_id={'present' if data.get('audit_id') else 'missing'}",
        f"correlation_id={'present' if data.get('correlation_id') else 'missing'}",
    ]


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
    draw.rounded_rectangle(box, radius=20, fill=PANEL, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x1 + 6, y2), fill=accent)
    draw.text((x1 + 26, y1 + 20), title, font=PANEL_TITLE_FONT, fill=TEXT)
    y = y1 + 62
    selected_font = MONO_FONT if code else BODY_FONT
    max_chars = max(34, (x2 - x1 - 66) // (9 if code else 10))
    for line in wrap_lines(lines, max_chars)[:18]:
        fill = TEXT
        lowered = line.lower()
        if line.startswith(("PASS", "OK", "fixture_safe=true")) or "passed" in lowered:
            fill = GREEN
        elif line.startswith(("REFUSE", "BLOCK", "DENY")) or "failed" in lowered:
            fill = RED
        elif line.startswith(("$", "python", "PYTHONPATH")):
            fill = BLUE
        draw.text((x1 + 26, y), line, font=selected_font, fill=fill)
        y += 24 if code else 28
        if y > y2 - 32:
            break


def render(
    path: Path,
    title: str,
    subtitle: str,
    panels: list[dict[str, Any]],
    footer: str = "Local inputs | No provider writes | Synthetic records",
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    for x in range(0, WIDTH, 100):
        draw.line((x, 0, x, HEIGHT), fill=(15, 23, 42))
    for y in range(0, HEIGHT, 100):
        draw.line((0, y, WIDTH, y), fill=(15, 23, 42))

    draw.rounded_rectangle(HEADER_BOX, radius=24, fill=PANEL_2, outline=BORDER, width=2)
    draw.text((60, 50), title, font=TITLE_FONT, fill=TEXT)
    draw.text((60, 94), subtitle, font=SUBTITLE_FONT, fill=MUTED)

    for panel in panels:
        draw_panel(
            draw,
            panel["box"],
            str(panel["title"]),
            list(panel["lines"]),
            accent=panel.get("accent", BLUE),
            code=bool(panel.get("code", False)),
        )

    draw.rounded_rectangle(FOOTER_BOX, radius=16, fill=PANEL_2, outline=BORDER, width=1)
    draw.text((56, 742), footer, font=BODY_FONT, fill=MUTED)

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("SM-Systems-Validation", f"{title}\n{subtitle}\n{footer}")
    image.save(path, pnginfo=metadata, optimize=True)

    stat = ImageStat.Stat(image)
    if path.stat().st_size < 25_000 or max(stat.stddev) < 20:
        raise RuntimeError(
            f"image may be unreadable or blank: {path} "
            f"size={path.stat().st_size} stddev={stat.stddev}"
        )


def main() -> None:
    py = sys.executable
    contact = load_json("examples/input/contact-created.json")
    invalid_contact = load_json("examples/input/contact-created-invalid.json")
    health = load_json("examples/api-responses/health.json")
    contact_response = response_summary("examples/api-responses/hubspot-contact-response.json")
    order_response = response_summary("examples/api-responses/shopify-order-response.json")
    payment_response = response_summary("examples/api-responses/stripe-payment-response.json")
    duplicate_response = response_summary(
        "examples/api-responses/stripe-payment-duplicate-response.json"
    )
    dead_letter_response = response_summary("examples/api-responses/dead-letter-response.json")
    core_test_lines = run(
        [py, "-m", "pytest", "-q", "-p", "no:warnings", "tests", "-k", "not screenshots"]
    )
    image_test_lines = run(
        [py, "-m", "pytest", "-q", "-p", "no:warnings", "tests/test_screenshots.py"]
    )

    render(
        OUT / "01-system-flow.png",
        "API Webhook Bridge System Flow",
        (
            "Validate input, apply approved mappings, control duplicates, "
            "and return operating readback."
        ),
        [
            {
                "box": THREE_COLUMN_BOXES[0],
                "title": "Sources",
                "lines": [
                    "HubSpot-like contact",
                    "Shopify-like order",
                    "Stripe-like payment",
                    "constrained generic route",
                    "invalid event scenario",
                ],
            },
            {
                "box": THREE_COLUMN_BOXES[1],
                "title": "Control",
                "lines": [
                    "stream and size-check body",
                    "validate source contract",
                    "apply explicit mapping",
                    "evaluate idempotency",
                    "prepare destination operations",
                ],
            },
            {
                "box": THREE_COLUMN_BOXES[2],
                "title": "Outcomes",
                "lines": [
                    "mapped operation plan",
                    "duplicate ignored",
                    "dead-letter review",
                    "audit and correlation IDs",
                    "operator handoff note",
                ],
            },
        ],
    )

    render(
        OUT / "02-interface-surface.png",
        "OpenAPI Interface Surface",
        "Named routes keep contact, order, payment, mapping, and audit contracts explicit.",
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "HTTP routes",
                "code": True,
                "lines": [
                    "GET  /health",
                    "GET  /integrations",
                    "GET  /mappings",
                    "POST /webhooks/hubspot-like",
                    "POST /webhooks/shopify-like",
                    "POST /webhooks/stripe-like",
                    "GET  /audit/events",
                    "GET  /audit/dead-letter",
                ],
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Service contract",
                "accent": GREEN,
                "code": True,
                "lines": [
                    f"status={health.get('status')}",
                    f"fixture_safe={health.get('fixture_safe')}",
                    f"live_services_used={health.get('live_services_used')}",
                    "request_limit_bytes=64000",
                    "content_type=application/json",
                    "response_shape=JSON object",
                    "destination_execution=disabled",
                ],
            },
        ],
    )

    render(
        OUT / "03-core-processing.png",
        "Mapped Contact Processing",
        (
            "A controlled contact event becomes one Airtable-style operation "
            "through an explicit mapping."
        ),
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Source scenario",
                "code": True,
                "lines": [
                    f"type={contact.get('type')}",
                    f"contact_id={contact.get('contact_id')}",
                    "required_fields=contact_id,email",
                    "mapping=hubspot-contact-to-airtable",
                    "destination=airtable-like",
                ],
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Operation readback",
                "accent": GREEN,
                "code": True,
                "lines": contact_response,
            },
        ],
    )

    render(
        OUT / "04-event-guardrails.png",
        "Duplicate and Invalid Event Guardrails",
        "Repeated payments and incomplete contacts stop without repeated destination operations.",
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Duplicate payment",
                "accent": RED,
                "code": True,
                "lines": duplicate_response,
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Invalid contact",
                "accent": RED,
                "code": True,
                "lines": [
                    f"type={invalid_contact.get('type')}",
                    *dead_letter_response,
                ],
            },
        ],
    )

    render(
        OUT / "05-operating-readback.png",
        "Order and Payment Readback",
        (
            "Accepted events return destination-shaped operations with stable audit "
            "and correlation identifiers."
        ),
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Order processing",
                "accent": GREEN,
                "code": True,
                "lines": order_response,
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Payment processing",
                "accent": GREEN,
                "code": True,
                "lines": payment_response,
            },
        ],
    )

    render(
        OUT / "06-validation-scope.png",
        "Validation and Scope",
        (
            "Local checks cover routes, mappings, idempotency, audit records, "
            "saved responses, and image integrity."
        ),
        [
            {
                "box": TWO_COLUMN_BOXES[0],
                "title": "Validation commands",
                "code": True,
                "lines": [
                    "$ python -m pytest tests -q",
                    "$ python -m ruff check src tests scripts",
                    "$ python -m mypy src",
                    "$ examples/run-local-validation.sh",
                    "$ python scripts/capture_screenshots.py",
                ],
            },
            {
                "box": TWO_COLUMN_BOXES[1],
                "title": "Current result",
                "accent": GREEN,
                "lines": [
                    *validation_summary(core_test_lines, image_test_lines),
                    "source scenarios: synthetic",
                    "destination calls: zero",
                    "provider credentials: none",
                    "customer records: none",
                    "production storage: excluded",
                ],
            },
        ],
    )

    print("six portfolio images rendered")


if __name__ == "__main__":
    main()
