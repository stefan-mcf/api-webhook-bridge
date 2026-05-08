from pathlib import Path

from PIL import Image, ImageStat

SCREENSHOT_DIR = Path("docs/screenshots")
EXPECTED = [
    "01-flow-overview.png",
    "02-openapi-webhook-endpoints.png",
    "03-contact-bridge-proof.png",
    "04-mapping-config.png",
    "05-idempotency-audit.png",
    "06-dead-letter.png",
    "07-quality-gates.png",
    "08-debugger-handoff.png",
    "09-mock-job-01-bridge-proof.png",
]


def test_screenshots_are_readable_proof_panels() -> None:
    for name in EXPECTED:
        path = SCREENSHOT_DIR / name
        assert path.exists(), name
        assert path.stat().st_size > 25_000, f"{name} is too small and may be blank"
        with Image.open(path) as image:
            assert image.size == (1280, 760)
            assert image.info.get("Proof"), f"{name} is missing proof metadata"
            stat = ImageStat.Stat(image.convert("RGB"))
            assert max(stat.stddev) > 20, f"{name} has low visual variance and may be blank"


def test_readme_references_all_screenshots() -> None:
    readme = Path("README.md").read_text()
    for name in EXPECTED:
        assert f"docs/screenshots/{name}" in readme
