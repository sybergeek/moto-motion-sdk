"""Manim rendering for a minimal editorial circuit corner."""

from __future__ import annotations

from math import dist
from typing import Sequence

try:
    from manim import DashedVMobject, Dot, Line, VGroup, VMobject
except ImportError:  # pragma: no cover
    DashedVMobject = Dot = Line = VGroup = VMobject = None

from ...core.themes import DEFAULT_THEME, Theme
from ...geometry import Trajectory


def chained_points(
    paths: Sequence[Trajectory],
    *,
    samples: int = 80,
    tolerance: float = 0.08,
    extend_start: float = 0.0,
    extend_end: float = 0.0,
) -> list[tuple[float, float]]:
    """Sample connected trajectory segments as one continuous centerline.

    A circuit must render every segment a vehicle can drive.  Silent gaps are
    especially misleading in portrait explainers because a car appears to
    leave the road even when its trajectory is valid.
    """
    if not paths:
        raise ValueError("at least one trajectory segment is required")
    points: list[tuple[float, float]] = []
    for path in paths:
        segment = list(path.sample(samples))
        if points and dist(points[-1], segment[0]) > tolerance:
            raise ValueError("circuit trajectory segments are not connected")
        points.extend(segment if not points else segment[1:])
    if extend_start < 0 or extend_end < 0:
        raise ValueError("path extensions must be non-negative")
    if extend_start:
        tangent = paths[0].tangent(0.0)
        points.insert(0, (points[0][0] - tangent[0] * extend_start, points[0][1] - tangent[1] * extend_start))
    if extend_end:
        tangent = paths[-1].tangent(1.0)
        points.append((points[-1][0] + tangent[0] * extend_end, points[-1][1] + tangent[1] * extend_end))
    return points


def path_mobject(
    paths: Sequence[Trajectory],
    color: str,
    width: float,
    *,
    opacity: float = 1.0,
    samples: int = 80,
    extend_start: float = 0.0,
    extend_end: float = 0.0,
):
    """Build a continuous path, optionally extending beyond its endpoints.

    Endpoint extension lets a road continue beyond a moving portrait camera
    while vehicle trajectories retain their exact authored timing.
    """
    if VMobject is None:
        raise RuntimeError("path_mobject requires Manim")
    points = chained_points(paths, samples=samples, extend_start=extend_start, extend_end=extend_end)
    return VMobject().set_points_smoothly([(*point, 0) for point in points]).set_stroke(color, width, opacity=opacity)


def trajectory_history(paths: Sequence[Trajectory], color: str, *, width: float = 1.4, opacity: float = 0.52, dashes: int = 70):
    """Return a thin dotted route trace suitable for vehicle history."""
    if DashedVMobject is None:
        raise RuntimeError("trajectory_history requires Manim")
    return DashedVMobject(path_mobject(paths, color, width, opacity=opacity), num_dashes=dashes)


class Circuit:
    def __init__(self, centerline: Trajectory | Sequence[Trajectory], width: float = 1.5, kerb_spacing: int = 20, braking_zone: tuple[float, float] = (0.18, 0.34), theme: Theme = DEFAULT_THEME):
        self.centerline = (centerline,) if isinstance(centerline, Trajectory) else tuple(centerline)
        self.width, self.kerb_spacing, self.braking_zone, self.theme = width, kerb_spacing, braking_zone, theme
        chained_points(self.centerline, samples=20)

    def mobjects(self):
        if VMobject is None:
            raise RuntimeError("Circuit requires Manim")
        points = chained_points(self.centerline)
        border = VMobject().set_points_smoothly([(*point, 0) for point in points]).set_stroke(self.theme.border, self.width + 0.24)
        road = VMobject().set_points_smoothly([(*point, 0) for point in points]).set_stroke(self.theme.track, self.width)
        racing = VMobject().set_points_smoothly([(*point, 0) for point in points]).set_stroke(self.theme.accent, 0.06)
        apex_path = self.centerline[0]
        apex = Dot((*apex_path.point_at_distance(0.52), 0), color=self.theme.semantic.focus, radius=0.1)
        kerbs = VGroup()
        for index in range(self.kerb_spacing, len(points) - self.kerb_spacing, self.kerb_spacing):
            point = points[index]
            before = points[max(0, index - 1)]
            after = points[min(len(points) - 1, index + 1)]
            length = max(dist(before, after), 1e-9)
            tangent = ((after[0] - before[0]) / length, (after[1] - before[1]) / length)
            normal = (-tangent[1], tangent[0])
            start = (point[0] - normal[0] * self.width * 0.42, point[1] - normal[1] * self.width * 0.42, 0)
            end = (point[0] + normal[0] * self.width * 0.42, point[1] + normal[1] * self.width * 0.42, 0)
            kerb = Line(start, end, color=self.theme.semantic.braking, stroke_width=8)
            kerbs.add(kerb)
        brake_start, brake_end = self.braking_zone
        brake_marks = VGroup()
        brake_path = self.centerline[0]
        for fraction in (brake_start, (brake_start + brake_end) / 2, brake_end):
            point = brake_path.point_at_distance(fraction)
            tangent = brake_path.tangent(brake_path.distance_to_parameter(fraction * brake_path.length))
            brake_marks.add(Line((*point, 0), (point[0] - tangent[0] * 0.28, point[1] - tangent[1] * 0.28, 0), color=self.theme.semantic.braking, stroke_width=7))
        return VGroup(border, road, kerbs, DashedVMobject(racing, num_dashes=45), brake_marks, apex)
