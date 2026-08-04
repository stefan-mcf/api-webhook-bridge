from pathlib import Path

from PIL import Image, ImageStat

SCREENSHOT_DIR = Path("docs/screenshots")
EXPECTED = [
    "01-system-flow.png",
    "02-interface-surface.png",
    "03-core-processing.png",
    "04-event-guardrails.png",
    "05-operating-readback.png",
    "06-validation-scope.png",
]
BANNED_PUBLIC_TERMS = ("pro" + "of", "evi" + "dence")


def test_images_are_readable_validation_panels() -> None:
    assert sorted(path.name for path in SCREENSHOT_DIR.glob("*.png")) == EXPECTED
    for name in EXPECTED:
        path = SCREENSHOT_DIR / name
        assert path.stat().st_size > 25_000, f"{name} is too small and may be blank"
        with Image.open(path) as image:
            assert image.size == (1400, 800)
            metadata = image.info.get("SM-Systems-Validation")
            assert metadata, f"{name} is missing project metadata"
            lowered = str(metadata).lower()
            assert not any(term in lowered for term in BANNED_PUBLIC_TERMS)
            stat = ImageStat.Stat(image.convert("RGB"))
            assert max(stat.stddev) > 20, f"{name} has low visual variance and may be blank"


def test_readme_references_images_in_functional_order() -> None:
    readme = Path("README.md").read_text()
    offsets = [readme.index(f"docs/screenshots/{name}") for name in EXPECTED]
    assert offsets == sorted(offsets)


def test_public_copy_avoids_internal_packaging_language() -> None:
    public_files = [Path("README.md"), Path("scripts/capture_screenshots.py")]
    public_files.extend(sorted(Path("docs").rglob("*.md")))
    public_files.extend(sorted(Path("configs").rglob("*.json")))
    public_files.extend(sorted(Path("examples/api-responses").rglob("*.json")))
    for path in public_files:
        lowered = path.read_text().lower()
        assert not any(term in lowered for term in BANNED_PUBLIC_TERMS), path
        assert not any(term in path.name.lower() for term in BANNED_PUBLIC_TERMS), path
