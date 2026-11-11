"""Raster-backed MotoGP identity assets derived from the supplied sticker grid."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

try:
    from manim import DOWN, ImageMobject, Text, VGroup
except ImportError:  # pragma: no cover
    DOWN = ImageMobject = Text = VGroup = None

ASSET_ROOT = Path(__file__).resolve().parents[4] / "assets" / "characters" / "motogp_raster"
MANIFEST = ASSET_ROOT / "manifest.json"


@dataclass(frozen=True)
class RasterRiderIdentity:
    rider_id: str
    display_name: str
    racing_number: str
    bike_path: Path
    helmet_path: Path


def _load_identities() -> dict[str, RasterRiderIdentity]:
    if not MANIFEST.exists():
        return {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[4]
    return {
        item["id"]: RasterRiderIdentity(
            item["id"], item["display_name"], str(item["number"]),
            root / item["bike_side"], root / item["helmet_badge"],
        )
        for item in data.get("assets", [])
    }


RASTER_IDENTITIES = _load_identities()


def get_raster_identity(identity: RasterRiderIdentity | str) -> RasterRiderIdentity:
    if isinstance(identity, RasterRiderIdentity):
        return identity
    try:
        return RASTER_IDENTITIES[identity]
    except KeyError as exc:
        raise KeyError(f"Unknown raster MotoGP identity: {identity}") from exc


class _RasterComponent:
    def __getattr__(self, name):
        return getattr(self.mobject, name)


class MotoGPBikeSideImage(_RasterComponent):
    """Approved bike+rider crop for identity graphics and transitions."""

    def __init__(self, identity: RasterRiderIdentity | str, scale: float = 1.0):
        if ImageMobject is None:
            raise RuntimeError("MotoGPBikeSideImage requires Manim")
        self.identity = get_raster_identity(identity)
        if not self.identity.bike_path.exists():
            raise FileNotFoundError(self.identity.bike_path)
        self.mobject = ImageMobject(str(self.identity.bike_path)).scale(scale)


class RiderHelmetBadgeImage(_RasterComponent):
    """Approved full-face helmet badge crop for identity graphics."""

    def __init__(self, identity: RasterRiderIdentity | str, scale: float = 1.0, with_label: bool = False):
        if ImageMobject is None:
            raise RuntimeError("RiderHelmetBadgeImage requires Manim")
        self.identity = get_raster_identity(identity)
        if not self.identity.helmet_path.exists():
            raise FileNotFoundError(self.identity.helmet_path)
        self.mobject = ImageMobject(str(self.identity.helmet_path)).scale(scale)
        if with_label:
            label = Text(f"{self.identity.racing_number}  {self.identity.display_name.upper()}", font="Barlow Condensed", weight="BOLD", font_size=15)
            self.mobject = VGroup(self.mobject, label.next_to(self.mobject, DOWN, buff=0.08))


__all__ = ["RasterRiderIdentity", "RASTER_IDENTITIES", "get_raster_identity", "MotoGPBikeSideImage", "RiderHelmetBadgeImage"]
