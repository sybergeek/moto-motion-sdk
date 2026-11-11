"""Validated, serializable contracts for RaceXplained carousels."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping


class CarouselLayout(StrEnum):
    HERO = "hero"
    TECHNICAL_DIAGRAM = "technical_diagram"
    COMPARISON = "comparison"
    TIMELINE = "timeline"
    DATA = "data"
    MYTH_FACT = "myth_fact"
    FULL_BLEED = "full_bleed"
    CONCLUSION = "conclusion"


SUPPORTED_ASPECT_RATIOS = {"3:4": (1080, 1440), "4:5": (1080, 1350), "1:1": (1080, 1080)}
MAX_SLIDES = 10
_REPO_ROOT = Path(__file__).resolve().parents[3]
KNOWN_ASSETS = {
    "f1_car": _REPO_ROOT / "assets/generated/f1_car.svg",
    "f1_car_svg": _REPO_ROOT / "assets/generated/f1_car.svg",
    "motogp_bike": _REPO_ROOT / "assets/characters/motogp/bike_side_master.svg",
    "motogp_bike_side": _REPO_ROOT / "assets/characters/motogp/bike_side_master.svg",
    "red_bull_editorial_f1": _REPO_ROOT / "assets/generated/f1_car_1e3a8a_e73e47_000000.svg",
    "mercedes_editorial_f1": _REPO_ROOT / "assets/generated/f1_car.svg",
    "mercedes_driver_pair": _REPO_ROOT / "assets/references/f1/mercedes_2026/driver_pair.jpg",
    "mercedes_podium_celebration": _REPO_ROOT / "assets/references/f1/mercedes_2026/podium_celebration.webp",
    "verstappen_2024_rain": _REPO_ROOT / "assets/references/f1/sao_paulo/verstappen_2024_rain.webp",
    "verstappen_2024_rain_action": _REPO_ROOT / "assets/references/f1/sao_paulo/verstappen_2024_rain_action.webp",
    "verstappen_2025_podium": _REPO_ROOT / "assets/references/f1/sao_paulo/verstappen_2025_podium.webp",
    "verstappen_2026_race": _REPO_ROOT / "assets/references/f1/sao_paulo/verstappen_2026_race.webp",
}


@dataclass(frozen=True)
class VisualSpec:
    type: str = "technical_diagram"
    asset_id: str | None = None
    annotations: tuple[dict[str, Any], ...] = ()
    source: str | None = None


@dataclass(frozen=True)
class CarouselSlide:
    index: int
    layout: CarouselLayout
    headline: str
    body: str | None = None
    visual: VisualSpec = field(default_factory=VisualSpec)
    kicker: str | None = None
    footer: str | None = None
    source_attribution: str | None = None
    theme: str | None = None


@dataclass(frozen=True)
class CarouselManifest:
    topic: str
    slides: tuple[CarouselSlide, ...]
    carousel_id: str = "carousel"
    aspect_ratio: str = "3:4"
    theme: str = "editorial_ivory"
    resolution: tuple[int, int] | None = None
    source_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
            raise ValueError(f"unsupported aspect ratio: {self.aspect_ratio}")
        expected = SUPPORTED_ASPECT_RATIOS[self.aspect_ratio]
        if self.resolution is not None and tuple(self.resolution) != expected:
            raise ValueError(f"{self.aspect_ratio} carousels must use {expected[0]}x{expected[1]}")
        if not 2 <= len(self.slides) <= MAX_SLIDES:
            raise ValueError(f"slide count must be between 2 and {MAX_SLIDES}")
        indices = tuple(slide.index for slide in self.slides)
        if indices != tuple(range(1, len(self.slides) + 1)):
            raise ValueError("slide indices must be consecutive and start at 1")
        if not self.topic.strip():
            raise ValueError("topic cannot be empty")
        if self.theme not in {"midnight_technical", "editorial_ivory", "carbon_signal", "racing_heritage"}:
            raise ValueError(f"unknown theme: {self.theme}")
        for slide in self.slides:
            if not slide.headline.strip():
                raise ValueError(f"slide {slide.index} headline cannot be empty")
            if slide.visual.type == "existing_asset" and not slide.visual.asset_id:
                raise ValueError(f"slide {slide.index} existing_asset requires asset_id")
            if slide.visual.type == "existing_asset" and slide.visual.asset_id in KNOWN_ASSETS and not KNOWN_ASSETS[slide.visual.asset_id].exists():
                raise ValueError(f"slide {slide.index} references unavailable asset: {slide.visual.asset_id}")

    @property
    def dimensions(self) -> tuple[int, int]:
        return SUPPORTED_ASPECT_RATIOS[self.aspect_ratio]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["slides"] = [asdict(slide) for slide in self.slides]
        for slide in value["slides"]:
            slide["layout"] = slide["layout"].value
        value["resolution"] = list(self.resolution or self.dimensions)
        value["source_references"] = list(self.source_references)
        return value

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CarouselManifest":
        slides = []
        for raw in data.get("slides", ()):
            visual = raw.get("visual") or {}
            slides.append(CarouselSlide(
                index=int(raw["index"]), layout=CarouselLayout(raw["layout"]),
                headline=str(raw["headline"]), body=raw.get("body"),
                visual=VisualSpec(type=str(visual.get("type", "technical_diagram")), asset_id=visual.get("asset_id"), annotations=tuple(visual.get("annotations", ())), source=visual.get("source")),
                kicker=raw.get("kicker"), footer=raw.get("footer"),
                source_attribution=raw.get("source_attribution"), theme=raw.get("theme"),
            ))
        return cls(topic=str(data["topic"]), slides=tuple(slides), carousel_id=str(data.get("carousel_id", "carousel")), aspect_ratio=str(data.get("aspect_ratio", "3:4")), theme=str(data.get("theme", "editorial_ivory")), resolution=tuple(data["resolution"]) if data.get("resolution") else None, source_references=tuple(data.get("source_references", ())))

    @classmethod
    def from_json(cls, path: str | Path) -> "CarouselManifest":
        import json
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

