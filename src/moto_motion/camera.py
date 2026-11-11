"""Deterministic camera rig state for smooth, direction-aware framing."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import atan2

from .core.layout import CameraTransform, Point
from .effects.motion import smoothstep


@dataclass(frozen=True)
class CameraLimits:
    min_x: float = -20.0
    max_x: float = 20.0
    min_y: float = -20.0
    max_y: float = 20.0
    min_zoom: float = 0.65
    max_zoom: float = 1.6


@dataclass(frozen=True)
class CameraState:
    center: Point = (0.0, 0.0)
    zoom: float = 1.0
    heading: float = 0.0


class CameraRig:
    """Camera planner independent from any particular renderer or Mobject."""

    def __init__(self, *, limits: CameraLimits | None = None, look_ahead: float = 1.1):
        self.limits = limits or CameraLimits()
        self.look_ahead = look_ahead
        self.state = CameraState()

    def _clamp(self, point: Point) -> Point:
        return (min(max(point[0], self.limits.min_x), self.limits.max_x), min(max(point[1], self.limits.min_y), self.limits.max_y))

    def follow(self, target: Point, velocity: Point = (0.0, 0.0), *, zoom: float | None = None) -> CameraState:
        speed = (velocity[0] ** 2 + velocity[1] ** 2) ** 0.5
        direction = (velocity[0] / speed, velocity[1] / speed) if speed > 1e-9 else (0.0, 0.0)
        focus = self._clamp((target[0] + direction[0] * self.look_ahead, target[1] + direction[1] * self.look_ahead))
        self.state = CameraState(focus, self._clamp_zoom(zoom or self.state.zoom), self.state.heading if speed == 0 else atan2(direction[1], direction[0]))
        return self.state

    def focus(self, point: Point, *, zoom: float | None = None) -> CameraState:
        self.state = CameraState(self._clamp(point), self._clamp_zoom(zoom or self.state.zoom), self.state.heading)
        return self.state

    def frame_multiple(self, points: tuple[Point, ...], *, padding: float = 1.0) -> CameraState:
        if not points:
            return self.state
        center = (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))
        span = max(max(p[0] for p in points) - min(p[0] for p in points), max(p[1] for p in points) - min(p[1] for p in points)) + padding
        return self.focus(center, zoom=min(self.limits.max_zoom, max(self.limits.min_zoom, 5.0 / max(span, 1.0))))

    def interpolate(self, target: CameraState, progress: float) -> CameraState:
        eased = smoothstep(progress)
        self.state = CameraState(tuple(a + (b - a) * eased for a, b in zip(self.state.center, target.center)), self.state.zoom + (target.zoom - self.state.zoom) * eased, self.state.heading + (target.heading - self.state.heading) * eased)
        return self.state

    def transform(self) -> CameraTransform:
        return CameraTransform(self.state.center, self.state.zoom, 0.0)

    def _clamp_zoom(self, zoom: float) -> float:
        return min(max(zoom, self.limits.min_zoom), self.limits.max_zoom)
