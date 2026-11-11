import math

import pytest
from manim import Dot

from moto_motion.camera import CameraLimits, CameraRig, CameraState
from moto_motion.choreography import SceneDirector
from moto_motion.core.layout import CameraTransform, SafeAreaLayout
from moto_motion.effects import endpoint_speed_profile, trajectory_speed_profile
from moto_motion.geometry import Trajectory
from moto_motion.transitions import TransitionDirector, fade_out_scene_foreground
from moto_motion.typography import F1_PROFILE, MOTOGP_PROFILE, NumericDelta, TelemetryCounter, TypographySystem


def test_normalized_safe_area_points_are_inside_bounds():
    layout = SafeAreaLayout()
    assert layout.safe.contains(layout.point((0, 0)))
    assert layout.safe.contains(layout.point((1, 1)))
    assert layout.point((0.5, 0.5)) == pytest.approx((0, 0))


def test_default_safe_area_reserves_mobile_edge_padding():
    """Portrait UI keeps a deliberate title/action-safe inset on all sides."""
    layout = SafeAreaLayout()
    assert layout.safe.left == pytest.approx(-3.6)
    assert layout.safe.right == pytest.approx(3.6)
    assert layout.safe.bottom == pytest.approx(-6.64)
    assert layout.safe.top == pytest.approx(6.64)


def test_camera_world_round_trip():
    transform = CameraTransform(center=(2.0, -1.0), zoom=1.4, rotation=0.2)
    point = (4.2, 3.7)
    assert transform.camera_to_world(transform.world_to_camera(point)) == pytest.approx(point)


def test_endpoint_speed_profile_preserves_boundary_velocity():
    profile = endpoint_speed_profile(0.6, 1.2)
    epsilon = 1e-6
    assert profile(0.0) == pytest.approx(0.0)
    assert profile(1.0) == pytest.approx(1.0)
    assert profile(epsilon) / epsilon == pytest.approx(0.6, rel=1e-4)
    assert (1.0 - profile(1.0 - epsilon)) / epsilon == pytest.approx(1.2, rel=1e-4)


def test_trajectory_speed_profile_uses_world_units_per_second():
    trajectory = Trajectory(((0, 0), (1, 0), (2, 0), (3, 0)))
    profile = trajectory_speed_profile(trajectory, 3.0, start_speed=0.5, end_speed=1.0)
    epsilon = 1e-6
    assert profile(epsilon) / epsilon == pytest.approx(0.5, rel=1e-4)
    assert (1.0 - profile(1.0 - epsilon)) / epsilon == pytest.approx(1.0, rel=1e-4)


def test_camera_look_ahead_and_limits():
    rig = CameraRig(limits=CameraLimits(-2, 2, -2, 2), look_ahead=1.0)
    state = rig.follow((1.8, 0.0), (4.0, 0.0), zoom=2.0)
    assert state.center == pytest.approx((2.0, 0.0))
    assert state.zoom == pytest.approx(1.6)
    assert state.heading == pytest.approx(0.0)


def test_camera_interpolation_is_smooth_and_deterministic():
    rig = CameraRig()
    target = CameraState((4, 2), 1.3, 0.5)
    first = rig.interpolate(target, 0.5)
    rig.state = CameraState()
    second = rig.interpolate(target, 0.5)
    assert first == second
    assert first.center[0] < target.center[0]


def test_choreography_presets_validate_and_overlap():
    director = SceneDirector()
    director.preset("approach_corner", 0, 4)
    director.preset("exit_corner", 3, 4)
    director.validate()
    assert len(director.events_at(3.5)) == 2
    with pytest.raises(ValueError):
        director.preset("spin_out", 0, 1)


def test_typography_wraps_and_rejects_unknown_animation():
    system = TypographySystem()
    assert system.wrap_words("WHY CORNER EXIT SPEED WINS RACES".split(), max_chars=16) == ("WHY CORNER EXIT", "SPEED WINS RACES")
    with pytest.raises(ValueError):
        system.animation_spec("random_effect")


def test_transitions_are_explicit_and_selective_about_blur():
    director = TransitionDirector()
    spec = director.object_reveal((1, 0), duration=0.6)
    assert spec.source == "vehicle"
    assert spec.blur is False
    with pytest.raises(ValueError):
        director.directional_wipe((1, 0), duration=0)


def test_premium_transition_set_preserves_direction():
    director = TransitionDirector()
    assert director.vehicle_follow((1, 0)).direction == (1, 0)
    assert director.match_position_cut((0, -1)).source == "object_position"
    assert director.telemetry_panel_slide((-1, 0)).source == "screen_ui"


def test_scene_clear_can_preserve_an_explicit_backdrop():
    class FakeScene:
        def __init__(self, *mobjects):
            self.mobjects = list(mobjects)

    backdrop = Dot()
    foreground = Dot()
    animations = fade_out_scene_foreground(FakeScene(backdrop, foreground), preserve=(backdrop,))
    assert len(animations) == 1
    assert animations[0].mobject is foreground


def test_scene_clear_rejects_non_positive_duration():
    with pytest.raises(ValueError):
        fade_out_scene_foreground(type("Scene", (), {"mobjects": []})(), run_time=0)


def test_telemetry_and_delta_formatting():
    assert TelemetryCounter(148, 164).value_at(1) == "164 km/h"
    assert NumericDelta(-0.31).formatted() == "-0.31 s"


def test_category_profiles_keep_distinct_hierarchies():
    f1 = TypographySystem(profile=F1_PROFILE)
    motogp = TypographySystem(profile=MOTOGP_PROFILE)
    assert f1.headline_style().font == "Oxanium"
    assert f1.body_style().font == "Saira"
    assert motogp.headline_style().font == "Rajdhani"
    assert motogp.body_style().font == "Barlow Condensed"
    assert f1.telemetry_style().font == motogp.telemetry_style().font == "IBM Plex Mono"


def test_missing_font_uses_declared_fallback(caplog):
    caplog.set_level("WARNING")
    resolved = TypographySystem.resolve_font("Definitely Missing Motorsport Font", ("Helvetica Neue",))
    assert resolved == "Helvetica Neue"
    assert "explicit fallback" in caplog.text


def test_profile_font_report_exposes_requested_weights():
    report = TypographySystem.font_report(MOTOGP_PROFILE)
    assert report["display"]["requested_weight"] == "BOLD"
    assert report["secondary"]["requested_weight"] == "SEMIBOLD"
    assert report["telemetry"]["requested_weight"] == "MEDIUM"
