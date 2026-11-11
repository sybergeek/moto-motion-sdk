"""Objective post-render checks for carousel slides."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from ..core.themes import THEMES, contrast_ratio
from ..core.layout_allocator import LayoutAllocator, LayoutRequest
from ..core.safe_area import LogicalCanvas, NormalizedRect, SafeAreaProfile
from .models import KNOWN_ASSETS, CarouselManifest


@dataclass(frozen=True)
class CarouselFinding:
    severity: str
    code: str
    message: str
    slide: int | None = None


def _slide_layout_report(manifest: CarouselManifest, slide) -> object:
    safe = SafeAreaProfile("instagram_carousel_v1", .106, .106, .07, .06)
    canvas = LogicalCanvas(*manifest.dimensions, safe_area=safe)
    requests = [
        LayoutRequest("header", NormalizedRect(.106, .075, .788, .04), priority=100),
        LayoutRequest("headline", NormalizedRect(.106, .14, .788, .20), priority=90),
        LayoutRequest("body", NormalizedRect(.106, .36, .788, .11), priority=80),
        LayoutRequest("footer", NormalizedRect(.106, .90, .788, .03), priority=70),
    ]
    if slide.visual.type != "none":
        requests.append(LayoutRequest("visual", NormalizedRect(.12, .49, .76, .30), priority=60))
    else:
        requests = [
            LayoutRequest("header", NormalizedRect(.106, .075, .788, .04), priority=100),
            LayoutRequest("headline", NormalizedRect(.106, .30, .788, .16), priority=90),
            LayoutRequest("cta", NormalizedRect(.106, .50, .788, .12), priority=80),
            LayoutRequest("footer", NormalizedRect(.106, .90, .788, .03), priority=70),
        ]
    return LayoutAllocator(canvas).resolve(requests)


def validate_rendered_carousel(manifest: CarouselManifest, output_dir: str | Path) -> dict[str, object]:
    output_dir = Path(output_dir)
    width, height = manifest.dimensions
    findings: list[CarouselFinding] = []
    layout_reports = {}
    for slide in manifest.slides:
        layout = _slide_layout_report(manifest, slide)
        layout_reports[str(slide.index)] = {
            "allowed": layout.allowed,
            "allocations": [{"element_id": item.element_id, "bounds": item.bounds.__dict__, "scale": item.scale, "reflowed": item.reflowed} for item in layout.allocations],
            "violations": [{"element_id": item.element_id, "boundary": item.boundary, "severity": item.severity, "message": item.message} for item in layout.violations],
        }
        for violation in layout.violations:
            findings.append(CarouselFinding("ERROR", "layout_collision", violation.message, slide.index))
        if len(slide.headline) > 54:
            findings.append(CarouselFinding("WARNING", "headline_load", "Headline is long for a mobile cover/slide; review line wrapping.", slide.index))
        if slide.body and len(slide.body) > 180:
            findings.append(CarouselFinding("WARNING", "body_load", "Body copy is long for a swipeable slide; shorten or split the idea.", slide.index))
        if slide.visual.type == "existing_asset" and slide.visual.asset_id in KNOWN_ASSETS and not KNOWN_ASSETS[slide.visual.asset_id].exists():
            findings.append(CarouselFinding("ERROR", "missing_asset", f"Registered asset is unavailable: {slide.visual.asset_id}", slide.index))
        path = output_dir / f"slide_{slide.index:02d}.png"
        if not path.exists():
            findings.append(CarouselFinding("ERROR", "missing_slide", f"Missing rendered slide: {path.name}", slide.index))
            continue
        try:
            from PIL import Image
            with Image.open(path) as image:
                if image.size != (width, height):
                    findings.append(CarouselFinding("ERROR", "dimensions", f"Expected {width}x{height}, got {image.width}x{image.height}", slide.index))
                if image.getbbox() is None:
                    findings.append(CarouselFinding("ERROR", "empty_slide", "Rendered slide is empty", slide.index))
        except ImportError:
            findings.append(CarouselFinding("ERROR", "pillow_missing", "Pillow is required for rendered-slide checks", slide.index))
    for slide in manifest.slides:
        theme = THEMES[slide.theme or manifest.theme]
        if contrast_ratio(theme.text, theme.background) < 4.5:
            findings.append(CarouselFinding("ERROR", "theme_contrast", f"Primary text token fails normal-text contrast for {theme.key}.", slide.index))
        if contrast_ratio(theme.secondary_text, theme.background) < 4.5:
            findings.append(CarouselFinding("WARNING", "secondary_contrast", f"Secondary text may be low contrast for {theme.key}; inspect on a phone.", slide.index))
    if len(manifest.slides) and (output_dir / "preview.png").exists() is False:
        findings.append(CarouselFinding("WARNING", "missing_preview", "Generate a contact-sheet preview for human inspection."))
    return {"carousel_id": manifest.carousel_id, "dimensions": [width, height], "slide_count": len(manifest.slides), "safe_margin": {"left": 0.106, "right": 0.106, "top": 0.07, "bottom": 0.06}, "layout_allocations": layout_reports, "findings": [asdict(item) for item in findings], "status": "ERROR" if any(item.severity == "ERROR" for item in findings) else "PASS"}

