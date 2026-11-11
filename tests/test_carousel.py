import json
from pathlib import Path

import pytest

from moto_motion.carousel import CarouselLayout, CarouselManifest, CarouselRenderer, CarouselSlide, VisualSpec, validate_rendered_carousel
from moto_motion.carousel.renderer import CarouselRenderer as RendererImplementation


def manifest(**overrides):
    slides = tuple(CarouselSlide(i, CarouselLayout.HERO if i == 1 else CarouselLayout.CONCLUSION, f"Slide {i}", visual=VisualSpec()) for i in range(1, 3))
    values = {"topic": "A topic", "slides": slides, **overrides}
    return CarouselManifest(**values)


def test_default_portrait_and_square_dimensions():
    assert manifest().dimensions == (1080, 1440)
    assert manifest(aspect_ratio="1:1").dimensions == (1080, 1080)


def test_manifest_rejects_non_consecutive_slides_and_bad_resolution():
    with pytest.raises(ValueError, match="consecutive"):
        CarouselManifest("topic", (CarouselSlide(2, CarouselLayout.HERO, "x"), CarouselSlide(3, CarouselLayout.CONCLUSION, "y")))
    with pytest.raises(ValueError, match="1080x1080"):
        CarouselManifest("topic", tuple(CarouselSlide(i, CarouselLayout.HERO, "x") for i in range(1, 3)), aspect_ratio="1:1", resolution=(1080, 1440))
    with pytest.raises(ValueError, match="asset_id"):
        CarouselManifest("topic", (CarouselSlide(1, CarouselLayout.HERO, "x", visual=VisualSpec(type="existing_asset")), CarouselSlide(2, CarouselLayout.CONCLUSION, "y")))


def test_manifest_rejects_unknown_theme():
    with pytest.raises(ValueError, match="unknown theme"):
        manifest(theme="neon")


def test_manifest_round_trip():
    source = manifest().to_dict()
    assert CarouselManifest.from_dict(json.loads(json.dumps(source))).to_dict() == source


def test_rendered_quality_reports_missing_slides(tmp_path: Path):
    report = validate_rendered_carousel(manifest(), tmp_path)
    assert report["status"] == "ERROR"
    assert any(item["code"] == "missing_slide" for item in report["findings"])


def test_renderer_can_regenerate_one_slide(tmp_path: Path):
    pytest.importorskip("PIL")
    renderer = CarouselRenderer(manifest(), tmp_path)
    renderer.render(slide_index=1)
    assert (tmp_path / "carousel" / "slide_01.png").exists()


def test_renderer_does_not_silently_clip_wrapped_text():
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw, ImageFont

    draw = ImageDraw.Draw(Image.new("RGB", (400, 200)))
    font = ImageFont.load_default()
    with pytest.raises(ValueError, match="does not fit"):
        RendererImplementation(manifest())._draw_wrapped(draw, "ONE TWO THREE FOUR", font, "#FFFFFF", (0, 0, 20, 20), max_lines=1)

