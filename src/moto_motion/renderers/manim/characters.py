"""Layer-aware Manim adapter for modular SVG driver characters."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from manim import AnimationGroup, RIGHT, SVGMobject, Text, UP, VGroup, Wait
except ImportError:  # pragma: no cover - used only in minimal installs
    AnimationGroup = RIGHT = SVGMobject = Text = UP = VGroup = Wait = None

from ...models.characters import DriverCharacterSpec, load_character_spec


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NAMESPACE)
DRAW_ORDER = ("left_arm", "right_arm", "torso", "number", "neck", "head", "hair", "eyebrows", "eyes", "nose", "mouth")


def _svg_tag(name: str) -> str:
    return f"{{{SVG_NAMESPACE}}}{name}"


def _layer_svg(source: Path, layer_id: str) -> Path:
    """Extract one named SVG group while preserving the canonical canvas.

    Manim flattens SVG groups while parsing, so this small adapter keeps each
    semantic group independently transformable without introducing a browser
    renderer or an image-based rig.
    """
    digest = hashlib.sha256(f"{source.resolve()}:{source.stat().st_mtime_ns}:{layer_id}".encode()).hexdigest()[:16]
    target = Path(tempfile.gettempdir()) / "moto-motion-character-layers" / digest / f"{layer_id}.svg"
    if target.exists():
        return target
    root = ET.parse(source).getroot()
    extracted = next((child for child in root if child.get("id") == layer_id), None)
    if extracted is None:
        raise ValueError(f"SVG layer {layer_id!r} missing from {source}")
    out = ET.Element(_svg_tag("svg"), {key: value for key, value in root.attrib.items() if key not in {"role", "aria-labelledby", "data-character-id", "data-design-version"}})
    for child in root:
        if child.tag in {_svg_tag("style"), _svg_tag("defs")}:
            out.append(child)
    # Keep all layers on one 512×512 coordinate system.  The invisible canvas
    # is intentionally included in layout bounds, never in visible pixels.
    ET.SubElement(out, _svg_tag("rect"), {"width": "512", "height": "512", "fill": "none", "stroke": "none", "opacity": "0"})
    out.append(extracted)
    target.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(out).write(target, encoding="utf-8", xml_declaration=True)
    return target


class DriverCharacter(VGroup if VGroup is not None else object):
    """A reusable character whose SVG layers remain animation-addressable."""

    def __init__(self, character_id: str = "kimi_antonelli", *, variant: str = "neutral", scale: float = 1.0, assets_dir: Path | None = None):
        if VGroup is None or SVGMobject is None:
            raise RuntimeError("DriverCharacter requires Manim; install the project dependencies first")
        super().__init__()
        self.spec: DriverCharacterSpec = load_character_spec(character_id, assets_dir) if assets_dir else load_character_spec(character_id)
        self.variant = variant
        self.layers: dict[str, SVGMobject] = {}
        self._load_variant(variant)
        self.scale(scale)

    def _make_layer(self, source: Path, layer_id: str) -> SVGMobject:
        if layer_id == "number":
            width, height = self.spec.canvas_size
            x, y = self.spec.number_anchor
            number = Text(str(self.spec.driver_number), font=self.spec.number_font, weight=self.spec.number_weight, color=self.spec.number_color)
            number.set_height(self.spec.number_height / height * 2)
            number.move_to((-1 + x / width * 2, 1 - y / height * 2, 0))
            return number
        return SVGMobject(str(_layer_svg(source, layer_id)))

    def _load_variant(self, name: str) -> None:
        source = self.spec.variant_svg(name)
        self.layers = {layer_id: self._make_layer(source, layer_id) for layer_id in self.spec.layer_ids}
        self.add(*(self.layers[layer_id] for layer_id in DRAW_ORDER if layer_id in self.layers))

    def layer(self, name: str):
        return self.layers[name]

    @property
    def head(self):
        return self.layer("head")

    @property
    def eyes(self):
        return self.layer("eyes")

    @property
    def mouth(self):
        return self.layer("mouth")

    @property
    def left_arm(self):
        return self.layer("left_arm")

    @property
    def right_arm(self):
        return self.layer("right_arm")

    def face(self):
        """Return the layers that must travel together for head movement."""
        return VGroup(*(self.layer(name) for name in ("head", "hair", "eyebrows", "eyes", "nose", "mouth")))

    def eye_features(self):
        """Return only eye artwork, excluding the invisible alignment canvas."""
        # _layer_svg prepends a full-canvas invisible rectangle. It is the
        # first parsed submobject and must not participate in a blink transform.
        return VGroup(*self.eyes.submobjects[1:])

    def anchor_point(self, name: str):
        """Return a canvas anchor in the character's current local placement."""
        x, y = self.spec.anchors[name]
        width, height = self.spec.canvas_size
        # SVG coordinates start at the top-left; Manim coordinates start at
        # the bottom-left.  The previous implementation used get_left() for
        # both axes, which placed the Y anchor relative to the character's
        # center and caused arms to rotate around a point above the shoulder.
        left_x = self.get_left()[0]
        bottom_y = self.get_bottom()[1]
        return left_x * RIGHT + bottom_y * UP + (x / width) * self.width * RIGHT + (1 - y / height) * self.height * UP

    def change_expression(self, variant: str):
        """Swap only expression layers while preserving pose and transform state.

        ``SVGMobject`` does not reliably morph unrelated SVG path topologies;
        replacing the semantic layers is deterministic and avoids rasterising a
        character just to change a mouth.
        """
        source = self.spec.variant_svg(variant)
        for layer_id in ("eyebrows", "eyes", "mouth"):
            replacement = self._make_layer(source, layer_id).match_width(self).move_to(self.get_center())
            self.layers[layer_id].become(replacement)
        self.variant = variant
        return Wait(0.001)

    def blink(self, duration: float = 0.10):
        """Return a compact mobile-readable blink animation."""
        features = self.eye_features()
        return AnimationGroup(features.animate.stretch(0.08, dim=1, about_point=features.get_center()), run_time=duration)

    def open_eyes(self, duration: float = 0.10):
        features = self.eye_features()
        return AnimationGroup(features.animate.stretch(12.5, dim=1, about_point=features.get_center()), run_time=duration)

    def celebrate(self, angle: float = 2.35):
        """Raise both arms from their physical shoulder anchors."""
        return AnimationGroup(
            self.left_arm.animate.rotate(-angle, about_point=self.anchor_point("left_shoulder")),
            self.right_arm.animate.rotate(angle, about_point=self.anchor_point("right_shoulder")),
            self.face().animate.shift(UP * 0.08),
            run_time=0.35,
            lag_ratio=0,
        )
