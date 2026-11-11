import math

import pytest

from moto_motion.geometry import Trajectory, cubic_bezier
from moto_motion.renderers.manim.circuit import chained_points
from moto_motion.renderers.manim.vehicles import F1Car


POINTS = ((0.0, 0.0), (1.0, 2.0), (3.0, 2.0), (4.0, 0.0))


def test_bezier_endpoints():
    assert cubic_bezier(POINTS, 0) == POINTS[0]
    assert cubic_bezier(POINTS, 1) == POINTS[-1]


def test_arc_length_is_positive_and_monotonic():
    trajectory = Trajectory(POINTS)
    assert trajectory.length > math.dist(POINTS[0], POINTS[-1])
    distances = [trajectory.distance_to_parameter(i * trajectory.length / 10) for i in range(11)]
    assert distances == sorted(distances)


def test_constant_speed_samples_have_similar_spacing():
    trajectory = Trajectory(POINTS)
    points = trajectory.sample(20)
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    assert max(lengths) - min(lengths) < 0.03


def test_tangent_orientation():
    trajectory = Trajectory(((0, 0), (0, 1), (0, 2), (1, 3)))
    dx, dy = trajectory.tangent(0)
    assert dx == pytest.approx(0)
    assert dy > 0
    assert trajectory.heading(0) == pytest.approx(math.pi / 2)


def test_heading_follows_path():
    trajectory = Trajectory(POINTS)
    assert trajectory.heading(0) > 0
    assert trajectory.heading(1) < 0


def test_degenerate_paths_are_rejected():
    with pytest.raises(ValueError):
        Trajectory(((1, 1), (1, 1), (1, 1), (1, 1)))


def test_normalized_distance_clamps():
    trajectory = Trajectory(POINTS)
    assert trajectory.point_at_distance(-2) == POINTS[0]
    assert trajectory.point_at_distance(2) == POINTS[-1]


def test_chained_circuit_rejects_visible_gaps():
    first = Trajectory(((0, 0), (1, 0), (2, 0), (3, 0)))
    connected = Trajectory(((3, 0), (4, 0), (5, 0), (6, 0)))
    disconnected = Trajectory(((4, 1), (5, 1), (6, 1), (7, 1)))
    assert chained_points((first, connected), samples=5)[-1] == connected.point(1)
    with pytest.raises(ValueError, match="not connected"):
        chained_points((first, disconnected), samples=5)


def test_smooth_join_validation_checks_position_and_heading():
    first = Trajectory(((0, 0), (1, 0), (2, 0), (3, 0)))
    smooth = Trajectory(((3, 0), (4, 0), (5, 1), (6, 1)))
    sharp = Trajectory(((3, 0), (3, 1), (4, 2), (5, 2)))
    disconnected = Trajectory(((3.1, 0), (4, 0), (5, 0), (6, 0)))

    first.validate_smooth_join(smooth)
    assert first.join_position_gap(smooth) == pytest.approx(0.0)
    assert first.join_heading_delta(smooth) == pytest.approx(0.0)
    with pytest.raises(ValueError, match="heading discontinuity"):
        first.validate_smooth_join(sharp)
    with pytest.raises(ValueError, match="position gap"):
        first.validate_smooth_join(disconnected)


def test_chained_circuit_can_extend_beyond_camera_edges():
    path = Trajectory(((0, 0), (0, 1), (0, 2), (0, 3)))
    points = chained_points((path,), extend_start=2.0, extend_end=4.0)
    assert points[0] == pytest.approx((0.0, -2.0))
    assert points[-1] == pytest.approx((0.0, 7.0))


def test_chained_circuit_rejects_negative_extensions():
    path = Trajectory(((0, 0), (0, 1), (0, 2), (0, 3)))
    with pytest.raises(ValueError, match="non-negative"):
        chained_points((path,), extend_start=-1.0)


def test_vehicle_pose_uses_trajectory_tangent_at_first_frame():
    downward = Trajectory(((0, 2), (0, 1), (0, 0), (0, -1)))
    point, rotation = F1Car.pose_on_trajectory(downward, 0)
    assert point == downward.point(0)
    assert rotation == pytest.approx(-math.pi)


def test_vehicle_pose_keeps_nose_aligned_with_upward_tangent():
    upward = Trajectory(((0, 0), (0, 1), (0, 2), (0, 3)))
    _, rotation = F1Car.pose_on_trajectory(upward, 0)
    assert rotation == pytest.approx(0.0)
