"""Configuration-backed metadata for reusable editorial driver characters."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


CHARACTERS_DIR = Path(__file__).resolve().parents[3] / "assets" / "characters"


@dataclass(frozen=True)
class DriverCharacterSpec:
    """A stable description of a character's source artwork and anchors."""

    character_id: str
    display_name: str
    driver_number: int
    asset_dir: Path
    canonical_svg: Path
    variants: dict[str, Path]
    layer_ids: tuple[str, ...]
    anchors: dict[str, tuple[float, float]]
    canvas_size: tuple[float, float]
    number_anchor: tuple[float, float]
    number_height: float
    number_font: str
    number_weight: str
    number_color: str
    facial_geometry: dict

    def variant_svg(self, name: str = "neutral") -> Path:
        try:
            return self.variants[name]
        except KeyError as error:
            available = ", ".join(sorted(self.variants))
            raise ValueError(f"Unknown {self.character_id} variant {name!r}; available: {available}") from error


def load_character_spec(character_id: str, assets_dir: Path = CHARACTERS_DIR) -> DriverCharacterSpec:
    """Load a character declared in ``assets/characters/registry.json``."""
    registry = json.loads((assets_dir / "registry.json").read_text(encoding="utf-8"))
    try:
        item = registry["drivers"][character_id]
    except KeyError as error:
        raise ValueError(f"Character {character_id!r} is not registered") from error
    config_path = assets_dir / item["config"]
    data = json.loads(config_path.read_text(encoding="utf-8"))
    asset_dir = config_path.parent
    canvas = data["canvas"]
    return DriverCharacterSpec(
        character_id=data["id"],
        display_name=data["display_name"],
        driver_number=int(data["driver_number"]),
        asset_dir=asset_dir,
        canonical_svg=asset_dir / data["canonical_svg"],
        variants={name: asset_dir / path for name, path in data["variants"].items()},
        layer_ids=tuple(data["layer_ids"]),
        anchors={name: tuple(point) for name, point in data["anchors"].items()},
        canvas_size=(float(canvas["width"]), float(canvas["height"])),
        number_anchor=tuple(data["number"]["anchor"]),
        number_height=float(data["number"]["height"]),
        number_font=data["number"]["font_family"],
        number_weight=data["number"]["font_weight"],
        number_color=data["number"]["color"],
        facial_geometry=data["facial_geometry"],
    )
