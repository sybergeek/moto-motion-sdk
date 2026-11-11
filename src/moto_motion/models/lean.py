"""Renderer-neutral front-view motorcycle lean geometry."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import atan2, cos, degrees, hypot, radians, sin, tan

Point = tuple[float, float]


def _bike_to_world(point: Point, lean_degrees: float) -> Point:
    """Rotate bike-local coordinates clockwise about the tyre contact point."""
    angle = radians(lean_degrees)
    x, y = point
    return (x * cos(angle) + y * sin(angle), -x * sin(angle) + y * cos(angle))


@dataclass(frozen=True)
class LeanPose:
    """Simplified bike+rider pose with a fixed road contact point."""

    bike_lean_degrees: float = 48.0
    rider_offset: float = 0.0
    rider_relative_lean_degrees: float = 0.0
    bike_mass: float = 157.0
    rider_mass: float = 70.0
    bike_com_height: float = 1.05
    seat_height: float = 1.43
    rider_com_from_pelvis: float = 0.42

    @property
    def contact_point(self) -> Point:
        return (0.0, 0.0)

    @property
    def bike_com(self) -> Point:
        return _bike_to_world((0.0, self.bike_com_height), self.bike_lean_degrees)

    @property
    def rider_pelvis(self) -> Point:
        return _bike_to_world((self.rider_offset, self.seat_height), self.bike_lean_degrees)

    @property
    def rider_absolute_lean_degrees(self) -> float:
        return self.bike_lean_degrees + self.rider_relative_lean_degrees

    @property
    def rider_com(self) -> Point:
        angle = radians(self.rider_absolute_lean_degrees)
        pelvis = self.rider_pelvis
        return (
            pelvis[0] + self.rider_com_from_pelvis * sin(angle),
            pelvis[1] + self.rider_com_from_pelvis * cos(angle),
        )

    @property
    def combined_com(self) -> Point:
        total = self.bike_mass + self.rider_mass
        bike = self.bike_com
        rider = self.rider_com
        return (
            (bike[0] * self.bike_mass + rider[0] * self.rider_mass) / total,
            (bike[1] * self.bike_mass + rider[1] * self.rider_mass) / total,
        )

    @property
    def combined_lean_degrees(self) -> float:
        x, y = self.combined_com
        return degrees(atan2(x, y))

    @property
    def lateral_force_ratio(self) -> float:
        """Required lateral/vertical road-force ratio for this COM lean."""
        return tan(radians(self.combined_lean_degrees))

    @property
    def normalized_road_force(self) -> Point:
        vector = (self.lateral_force_ratio, 1.0)
        magnitude = hypot(*vector)
        return (vector[0] / magnitude, vector[1] / magnitude)

    def with_bike_lean(self, lean_degrees: float) -> "LeanPose":
        return replace(self, bike_lean_degrees=lean_degrees)

    def solve_bike_lean_for_combined(
        self,
        target_degrees: float,
        *,
        lower: float = 0.0,
        upper: float = 70.0,
        iterations: int = 80,
    ) -> "LeanPose":
        """Solve motorcycle lean while preserving a target combined COM lean."""
        if not lower <= target_degrees <= upper:
            raise ValueError("target combined lean must be within the solve interval")
        low, high = lower, upper
        low_value = self.with_bike_lean(low).combined_lean_degrees
        high_value = self.with_bike_lean(high).combined_lean_degrees
        if not low_value <= target_degrees <= high_value:
            raise ValueError("rider pose cannot achieve the requested combined lean")
        for _ in range(iterations):
            middle = (low + high) / 2
            value = self.with_bike_lean(middle).combined_lean_degrees
            if value < target_degrees:
                low = middle
            else:
                high = middle
        return self.with_bike_lean((low + high) / 2)


def equilibrium_lean_degrees(speed: float, radius: float, gravity: float = 9.81) -> float:
    """Idealized steady-state combined lean from speed and corner radius."""
    if speed < 0 or radius <= 0 or gravity <= 0:
        raise ValueError("speed must be non-negative and radius/gravity positive")
    return degrees(atan2(speed * speed, radius * gravity))
