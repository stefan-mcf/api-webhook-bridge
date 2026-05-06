"""Capture page-clean public evidence screenshots for the sandbox walkthrough."""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "docs" / "screenshots"
CAPTURE = SCREENSHOTS / "_capture"

PAGES = {
    "01-flow-overview.png": CAPTURE / "01-flow-overview.html",
    "03-sandbox-contact-event.png": CAPTURE / "03-sandbox-contact-event.html",
    "04-mapping-config.png": CAPTURE / "04-mapping-config.html",
    "05-idempotency-audit.png": CAPTURE / "05-idempotency-audit.html",
    "06-dead-letter.png": CAPTURE / "06-dead-letter.html",
}


async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1400, "height": 1200},
            device_scale_factor=1,
        )
        for output_name, html_path in PAGES.items():
            await page.goto(html_path.as_uri(), wait_until="networkidle")
            await page.screenshot(path=SCREENSHOTS / output_name, full_page=True)
        await page.goto("http://127.0.0.1:8012/docs", wait_until="networkidle")
        await page.screenshot(path=SCREENSHOTS / "02-openapi-webhook-endpoint.png", full_page=True)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
