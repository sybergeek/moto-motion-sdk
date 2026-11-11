import pytest

from moto_motion.core.safe_area import (
    INSTAGRAM_REELS_V1,
    LayoutClass,
    LayoutElement,
    LayoutError,
    LogicalCanvas,
    NormalizedRect,
    SceneVisualContract,
    SafeAreaProfile,
    manim_to_normalized,
    normalized_to_manim,
    validate_camera_canvas,
    validate_element_collisions,
    validate_scene_layout,
    validate_scene_visual_contracts,
)


def test_normalized_pixel_and_manim_round_trips_at_multiple_resolutions():
    for width, height in ((1080, 1920), (1440, 2560), (2160, 3840), (1000, 1600)):
        canvas = LogicalCanvas(width, height)
        point = (.23, .71)
        assert canvas.pixels_to_normalized(canvas.normalized_to_pixels(point)) == pytest.approx(point)
        assert canvas.manim_to_normalized(canvas.normalized_to_manim(point)) == pytest.approx(point)
        assert normalized_to_manim(point, width, height) == pytest.approx(canvas.normalized_to_manim(point))
        assert manim_to_normalized(canvas.normalized_to_manim(point), width, height) == pytest.approx(point)


def test_instagram_safe_area_is_normalized_and_scales_dynamically():
    small = LogicalCanvas(1080, 1920)
    large = LogicalCanvas(2160, 3840)
    assert small.safe_rect == large.safe_rect
    assert small.safe_rect_pixels().x == pytest.approx(114.048)
    assert large.safe_rect_pixels().x == pytest.approx(228.096)
    assert small.safe_rect_pixels().y == pytest.approx(180.0)
    assert small.safe_rect_pixels().height == pytest.approx(1365.024)


def test_invalid_profile_leaves_no_usable_area():
    with pytest.raises(LayoutError):
        SafeAreaProfile("invalid", .6, .5, 0, 0)


def test_strict_safe_fails_and_full_bleed_is_exempt():
    canvas = LogicalCanvas(1080, 1920)
    elements = [
        LayoutElement("title", LayoutClass.STRICT_SAFE, ((0.0, NormalizedRect(.0, .1, .3, .1)),)),
        LayoutElement("background", LayoutClass.FULL_BLEED, ((0.0, NormalizedRect(0, 0, 1, 1)),)),
    ]
    violations = validate_scene_layout(canvas, elements)
    assert len(violations) == 1
    assert violations[0].boundary == "left"


def test_safe_anchor_checks_critical_anchor_at_intermediate_sample():
    canvas = LogicalCanvas(1080, 1920)
    element = LayoutElement(
        "track",
        LayoutClass.SAFE_ANCHOR,
        ((0.0, NormalizedRect(-.2, .2, 1.4, .2)), (0.5, NormalizedRect(-.2, .2, 1.4, .2))),
        (("apex", (.5, .5)),),
    )
    assert validate_scene_layout(canvas, [element]) == []
    unsafe = LayoutElement("track", LayoutClass.SAFE_ANCHOR, ((.5, NormalizedRect(0, 0, 1, 1)),), (("apex", (.98, .98)),))
    assert validate_scene_layout(canvas, [unsafe])[0].boundary == "apex"


def test_camera_canvas_mismatch_flags_unintended_outer_matte():
    canvas = LogicalCanvas(1080, 1920)
    assert validate_camera_canvas(canvas, frame_width=9, frame_height=16) == []
    violations = validate_camera_canvas(canvas, frame_width=14.222, frame_height=8)
    assert violations[0].boundary == "camera-frame"
    assert violations[0].severity == "error"


def test_visual_contract_requires_named_labeled_visual_proof_and_full_bleed():
    complete = SceneVisualContract("hook", "Marc Marquez", "MARC MÁRQUEZ · #93", "one title from history", "labelled bike and 7-to-8 counter", True)
    assert validate_scene_visual_contracts([complete]) == []
    incomplete = SceneVisualContract("comparison", "", "", "record holder", "", False)
    violations = validate_scene_visual_contracts([incomplete])
    assert {violation.boundary for violation in violations} == {"primary-subject", "subject-label", "visual-proof", "full-bleed-background"}


def test_semantic_collision_validation_ignores_full_bleed_but_rejects_caption_overlap():
    title = LayoutElement("title", LayoutClass.STRICT_SAFE, ((0.0, NormalizedRect(.2, .2, .4, .1)),))
    caption = LayoutElement("caption", LayoutClass.STRICT_SAFE, ((0.0, NormalizedRect(.3, .25, .4, .1)),))
    background = LayoutElement("background", LayoutClass.FULL_BLEED, ((0.0, NormalizedRect(0, 0, 1, 1)),))
    assert validate_element_collisions([title, caption, background])[0].boundary == "overlap:caption"
    assert validate_element_collisions([title, caption], ignore_pairs=frozenset({("title", "caption")})) == []
