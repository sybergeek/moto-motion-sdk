import math

import pytest

from moto_motion.models import LeanPose, equilibrium_lean_degrees


def test_aligned_rider_matches_motorcycle_lean():
    pose = LeanPose(bike_lean_degrees=48.0)
    assert pose.contact_point == (0.0, 0.0)
    assert pose.combined_lean_degrees == pytest.approx(48.0)


def test_hanging_off_reduces_bike_lean_for_same_combined_lean():
    target = 48.0
    aligned = LeanPose(bike_lean_degrees=target)
    hanging = LeanPose(rider_offset=0.42, rider_relative_lean_degrees=10.0).solve_bike_lean_for_combined(target)
    assert hanging.combined_lean_degrees == pytest.approx(aligned.combined_lean_degrees, abs=1e-8)
    assert hanging.bike_lean_degrees < aligned.bike_lean_degrees


def test_road_force_points_along_combined_com_axis():
    pose = LeanPose(bike_lean_degrees=44.0, rider_offset=0.24, rider_relative_lean_degrees=6.0)
    force = pose.normalized_road_force
    force_angle = math.degrees(math.atan2(force[0], force[1]))
    assert force_angle == pytest.approx(pose.combined_lean_degrees)
    assert pose.lateral_force_ratio > 0


def test_motorcycle_lean_pivots_without_moving_contact():
    upright = LeanPose(bike_lean_degrees=0.0)
    leaned = LeanPose(bike_lean_degrees=55.0)
    assert upright.contact_point == leaned.contact_point == (0.0, 0.0)
    assert leaned.bike_com[0] > upright.bike_com[0]
    assert leaned.bike_com[1] < upright.bike_com[1]


def test_equilibrium_lean_validates_inputs():
    assert equilibrium_lean_degrees(0.0, 50.0) == pytest.approx(0.0)
    assert equilibrium_lean_degrees(30.0, 80.0) > 0
    with pytest.raises(ValueError):
        equilibrium_lean_degrees(30.0, 0.0)
