"""SVG-backed MotoGP rider identity components reconstructed from the master."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from manim import DOWN, RIGHT, SVGMobject, Text, VGroup
except ImportError:  # pragma: no cover
    DOWN = RIGHT = SVGMobject = Text = VGroup = None


ASSET_ROOT = Path(__file__).resolve().parents[4] / "assets" / "characters" / "motogp"


@dataclass(frozen=True)
class RiderIdentity:
    rider_id: str
    display_name: str
    racing_number: str
    primary_color: str
    secondary_color: str
    accent_color: str
    helmet_pattern: str = "angular"


IDENTITIES = {
    "marc_marquez": RiderIdentity("marc_marquez", "Marc Márquez", "93", "#F12E2E", "#18232E", "#FFFFFF"),
    "jorge_martin": RiderIdentity("jorge_martin", "Jorge Martín", "89", "#7E32D7", "#18232E", "#F04A9B"),
    "marco_bezzecchi": RiderIdentity("marco_bezzecchi", "Marco Bezzecchi", "72", "#F1E51E", "#18232E", "#111820"),
}


def _asset(name: str) -> Path:
    path = ASSET_ROOT / name
    if not path.exists():
        raise FileNotFoundError(f"MotoGP master SVG is missing: {path}")
    return path


def _recolor_helmet(mobject, identity: RiderIdentity | None) -> None:
    """Apply palette changes to the known ordered SVG groups without flattening layers."""
    if identity is None:
        return
    parts = mobject.submobjects
    for index in (0, 5):
        if index < len(parts):
            parts[index].set_fill(identity.primary_color)
    for index in (6, 7):
        if index < len(parts):
            parts[index].set_fill(identity.accent_color)


class _SVGComponent:
    def __getattr__(self, name):
        return getattr(self.mobject, name)

    def layer(self, name: str):
        return self.layers.get(name, self.mobject)

    def anchor(self, name: str) -> tuple[float, float]:
        if name not in self.anchors:
            raise KeyError(f"unknown {self.__class__.__name__} anchor: {name}")
        return self.anchors[name]


class MotoGPBikeSide(_SVGComponent):
    """Approved side-view motorcycle master, loaded as editable SVG layers."""

    layer_names = ("shadow", "rear-wheel", "front-wheel", "brake-discs", "rear-swingarm", "main-chassis", "lower-fairing", "upper-fairing", "tank", "tail", "windscreen", "front-fork", "exhaust", "mechanical-accents", "number-panel")
    anchors = {"rear_axle": (-.31, -.12), "front_axle": (.31, -.12), "steering_head": (.20, .03), "handlebar_grip": (.14, .12), "seat_contact": (-.10, .06), "left_footpeg": (-.02, -.04)}

    def __init__(self, identity: RiderIdentity | str | None = None, number: str | None = None, scale: float = 1.0):
        if SVGMobject is None:
            raise RuntimeError("MotoGPBikeSide requires Manim; install the project dependencies first")
        identity = IDENTITIES.get(identity, identity) if isinstance(identity, str) else identity
        self.identity = identity
        self.mobject = SVGMobject(str(_asset("bike_side_master.svg"))).scale(scale)
        self.layers = {name: self.mobject for name in self.layer_names}
        if number or identity:
            number = number or identity.racing_number
            label = Text(str(number), font="Barlow Condensed", weight="BOLD", font_size=34, color="#0B1118")
            label.move_to(self.mobject.get_center() + RIGHT * .12 + DOWN * .02)
            self.mobject.add(label)


class RiderSideProfile(_SVGComponent):
    """Approved tucked rider master with stable joint/attachment anchors."""

    layer_names = ("helmet", "neck", "torso", "upper-arms", "forearms", "hands", "hips", "thighs", "lower-legs", "boots")
    anchors = {"helmet_center": (-.06, .25), "neck": (-.01, .10), "shoulder": (.04, .08), "elbow": (.20, -.04), "wrist": (.30, -.02), "hip": (-.02, -.05), "knee": (.10, -.15), "ankle": (.19, -.18), "boot_contact": (.22, -.19)}

    def __init__(self, identity: RiderIdentity | str | None = None, scale: float = 1.0):
        if SVGMobject is None:
            raise RuntimeError("RiderSideProfile requires Manim; install the project dependencies first")
        identity = IDENTITIES.get(identity, identity) if isinstance(identity, str) else identity
        self.identity = identity
        self.mobject = SVGMobject(str(_asset("rider_side_profile_master.svg"))).scale(scale)
        self.layers = {name: self.mobject for name in self.layer_names}


class RiderHelmetBadge(_SVGComponent):
    """Approved full-face helmet badge with configurable number and label."""

    layer_names = ("outer-shell", "visor-opening", "visor-trim", "chin-bar", "pivot", "livery-accent", "vent")
    anchors = {"helmet_center": (0.0, 0.0), "visor_center": (-.18, -.05), "number_center": (.20, -.02)}

    def __init__(self, identity: RiderIdentity | str | None = None, number: str | None = None, label: str | None = None, scale: float = 1.0, label_color: str = "#18232E"):
        if SVGMobject is None:
            raise RuntimeError("RiderHelmetBadge requires Manim; install the project dependencies first")
        identity = IDENTITIES.get(identity, identity) if isinstance(identity, str) else identity
        self.identity = identity
        self.mobject = SVGMobject(str(_asset("helmet_badge_master.svg"))).scale(scale)
        self.layers = {name: self.mobject for name in self.layer_names}
        _recolor_helmet(self.mobject, identity)
        number = number or (identity.racing_number if identity else None)
        label = label or (identity.display_name.upper() if identity else None)
        overlays = VGroup()
        if number:
            overlays.add(Text(str(number), font="Barlow Condensed", weight="BOLD", font_size=30, color="#FFFFFF").move_to(self.mobject.get_center() + RIGHT * .42 + DOWN * .04))
        if label:
            overlays.add(Text(label.upper(), font="Barlow Condensed", weight="BOLD", font_size=15, color=label_color).next_to(self.mobject, DOWN, buff=.14))
        self.mobject.add(overlays)
