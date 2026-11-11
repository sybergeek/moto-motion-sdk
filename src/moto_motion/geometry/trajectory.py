"""Numerically robust, dependency-free trajectory geometry."""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, atan2, hypot
from typing import Iterable, Sequence

Point = tuple[float, float]


def _add(a: Point, b: Point) -> Point:
    return a[0] + b[0], a[1] + b[1]


def _sub(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


def _scale(a: Point, factor: float) -> Point:
    return a[0] * factor, a[1] * factor


def _norm(a: Point) -> float:
    return hypot(*a)


def cubic_bezier(control_points: Sequence[Point], t: float) -> Point:
    """Evaluate a cubic Bézier at *t* using four control points."""
    if len(control_points) != 4:
        raise ValueError("a cubic Bézier requires exactly four control points")
    t = max(0.0, min(1.0, float(t)))
    u = 1.0 - t
    p0, p1, p2, p3 = control_points
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
    )


def cubic_derivative(control_points: Sequence[Point], t: float) -> Point:
    """Return dP/dt for a cubic Bézier."""
    p0, p1, p2, p3 = control_points
    u = 1.0 - max(0.0, min(1.0, float(t)))
    return (
        3 * u**2 * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t**2 * (p3[0] - p2[0]),
        3 * u**2 * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t**2 * (p3[1] - p2[1]),
    )


@dataclass(frozen=True)
class Trajectory:
    """A cubic path with an arc-length lookup table for constant-speed travel."""

    control_points: tuple[Point, Point, Point, Point]
    resolution: int = 400

    def __post_init__(self) -> None:
        if self.resolution < 2:
            raise ValueError("resolution must be at least 2")
        if all(self.control_points[0] == point for point in self.control_points[1:]):
            raise ValueError("degenerate trajectory: all control points are identical")
        object.__setattr__(self, "_parameters", tuple(i / self.resolution for i in range(self.resolution + 1)))
        samples = tuple(cubic_bezier(self.control_points, t) for t in self._parameters)
        distances = [0.0]
        for a, b in zip(samples, samples[1:]):
            distances.append(distances[-1] + _norm(_sub(b, a)))
        object.__setattr__(self, "_samples", samples)
        object.__setattr__(self, "_distances", tuple(distances))
        object.__setattr__(self, "_length", distances[-1])

    @property
    def length(self) -> float:
        return self._length

    def point(self, t: float) -> Point:
        return cubic_bezier(self.control_points, t)

    def distance_to_parameter(self, distance: float) -> float:
        """Invert arc length with linear interpolation in the lookup table."""
        if self.length == 0:
            return 0.0
        target = max(0.0, min(self.length, distance))
        for index in range(1, len(self._distances)):
            if self._distances[index] >= target:
                low, high = self._distances[index - 1], self._distances[index]
                fraction = 0.0 if high == low else (target - low) / (high - low)
                return (index - 1 + fraction) / self.resolution
        return 1.0

    def point_at_distance(self, normalized_distance: float) -> Point:
        return self.point(self.distance_to_parameter(normalized_distance * self.length))

    def tangent(self, t: float) -> Point:
        tangent = cubic_derivative(self.control_points, t)
        magnitude = _norm(tangent)
        if magnitude < 1e-12:
            epsilon = 1e-5
            tangent = _sub(self.point(min(1.0, t + epsilon)), self.point(max(0.0, t - epsilon)))
            magnitude = _norm(tangent)
        return (0.0, 0.0) if magnitude < 1e-12 else _scale(tangent, 1.0 / magnitude)

    def heading(self, t: float) -> float:
        dx, dy = self.tangent(t)
        return atan2(dy, dx)

    def join_position_gap(self, following: "Trajectory") -> float:
        """Distance between this endpoint and the following path's start."""
        return _norm(_sub(self.point(1.0), following.point(0.0)))

    def join_heading_delta(self, following: "Trajectory") -> float:
        """Unsigned tangent-angle discontinuity at a path join, in radians."""
        current = self.tangent(1.0)
        upcoming = following.tangent(0.0)
        dot = max(-1.0, min(1.0, current[0] * upcoming[0] + current[1] * upcoming[1]))
        return acos(dot)

    def validate_smooth_join(
        self,
        following: "Trajectory",
        *,
        position_tolerance: float = 1e-6,
        heading_tolerance: float = 1e-3,
    ) -> None:
        """Reject joins that would make a vehicle or follow camera snap."""
        position_gap = self.join_position_gap(following)
        heading_gap = self.join_heading_delta(following)
        if position_gap > position_tolerance:
            raise ValueError(f"trajectory join has a position gap of {position_gap:.6f}")
        if heading_gap > heading_tolerance:
            raise ValueError(f"trajectory join has a heading discontinuity of {heading_gap:.6f} radians")

    def curvature(self, t: float) -> float:
        p0, p1, p2, p3 = self.control_points
        d = cubic_derivative((p0, p1, p2, p3), t)
        dd = _add(
            _scale(_add(_sub(p2, _scale(p1, 2)), p0), 6 * (1 - t)),
            _scale(_add(_sub(p3, _scale(p2, 2)), p1), 6 * t),
        )
        denominator = _norm(d) ** 3
        return 0.0 if denominator < 1e-12 else (d[0] * dd[1] - d[1] * dd[0]) / denominator

    def sample(self, count: int, *, constant_speed: bool = True) -> tuple[Point, ...]:
        if count < 2:
            raise ValueError("count must be at least 2")
        if constant_speed:
            return tuple(self.point_at_distance(i / (count - 1)) for i in range(count))
        return tuple(self.point(i / (count - 1)) for i in range(count))
