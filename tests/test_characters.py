from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from moto_motion.models.characters import load_character_spec


ROOT = Path(__file__).resolve().parents[1]
SVG_NS = {"svg": "http://www.w3.org/2000/svg"}
EXPECTED_LAYERS = {"torso", "number", "neck", "head", "hair", "eyes", "eyebrows", "nose", "mouth", "left_arm", "right_arm"}


def test_registered_driver_sources_resolve():
    kimi = load_character_spec("kimi_antonelli")
    max_driver = load_character_spec("max_verstappen")
    assert kimi.driver_number == 12
    assert max_driver.driver_number == 3
    assert set(kimi.variants) == {"neutral", "smiling", "surprised", "celebrating", "pointing"}
    assert set(max_driver.variants) == {"neutral", "celebrating"}
    for spec in (kimi, max_driver):
        assert spec.canonical_svg.is_file()
        assert all(path.is_file() for path in spec.variants.values())


def test_registered_driver_svgs_keep_the_same_modular_layer_schema():
    for character_id in ("kimi_antonelli", "max_verstappen"):
        spec = load_character_spec(character_id)
        for asset in (spec.canonical_svg, *spec.variants.values()):
            root = ET.parse(asset).getroot()
            assert root.get("viewBox") == "0 0 512 512"
            layer_ids = {element.get("id") for element in root.findall("svg:g", SVG_NS)}
            assert layer_ids == EXPECTED_LAYERS


def test_character_animation_anchors_are_inside_the_canvas():
    spec = load_character_spec("kimi_antonelli")
    width, height = spec.canvas_size
    assert set(spec.anchors) >= {"character_origin", "head_center", "left_shoulder", "right_shoulder"}
    assert all(0 <= x <= width and 0 <= y <= height for x, y in spec.anchors.values())


def test_driver_identity_parameters_are_not_colour_only():
    kimi = load_character_spec("kimi_antonelli")
    max_driver = load_character_spec("max_verstappen")
    assert kimi.number_font == max_driver.number_font == "Barlow Condensed"
    assert kimi.facial_geometry != max_driver.facial_geometry
    assert kimi.facial_geometry["eye_centers"] != max_driver.facial_geometry["eye_centers"]
    assert kimi.facial_geometry["hairstyle"]["direction"] != max_driver.facial_geometry["hairstyle"]["direction"]
