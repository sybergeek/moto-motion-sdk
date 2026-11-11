"""Portrait layout and coordinate-space contracts.

World coordinates belong to the track and vehicles. Screen coordinates belong
to fixed UI. Camera coordinates are world coordinates after the camera transform.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin

from .constants import PORTRAIT

Point = tuple[float, float]


@dataclass(frozen=True)
class Rect:
    left: float
    bottom: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.left + self.width

    @property
    def top(self) -> float:
        return self.bottom + self.height

    def contains(self, point: Point, padding: float = 0.0) -> bool:
        return self.left + padding <= point[0] <= self.right - padding and self.bottom + padding <= point[1] <= self.top - padding


@dataclass(frozen=True)
class CameraTransform:
    center: Point = (0.0, 0.0)
    zoom: float = 1.0
    rotation: float = 0.0

    def world_to_camera(self, point: Point) -> Point:
        x, y = point[0] - self.center[0], point[1] - self.center[1]
        c, s = cos(-self.rotation), sin(-self.rotation)
        return (self.zoom * (x * c - y * s), self.zoom * (x * s + y * c))

    def camera_to_world(self, point: Point) -> Point:
        x, y = point[0] / self.zoom, point[1] / self.zoom
        c, s = cos(self.rotation), sin(self.rotation)
        return (self.center[0] + x * c - y * s, self.center[1] + x * s + y * c)


class SafeAreaLayout:
    """Maps normalized portrait UI coordinates to the Manim frame.

    Normalized coordinates use (0, 0) at the bottom-left and (1, 1) at the
    top-right. Fixed UI should use this class and never be parented to a world
    object or a moving camera frame.
    """

    def __init__(self, frame_width: float = 9.0, frame_height: float = 16.0, safe_x: float = 0.10, safe_y: float = 0.085):
        self.frame = Rect(-frame_width / 2, -frame_height / 2, frame_width, frame_height)
        self.safe = Rect(self.frame.left + frame_width * safe_x, self.frame.bottom + frame_height * safe_y, frame_width * (1 - 2 * safe_x), frame_height * (1 - 2 * safe_y))

    def point(self, normalized: Point, *, safe: bool = True) -> Point:
        rect = self.safe if safe else self.frame
        return (rect.left + normalized[0] * rect.width, rect.bottom + normalized[1] * rect.height)

    def rect(self, left: float, bottom: float, width: float, height: float, *, safe: bool = True) -> Rect:
        origin = self.point((left, bottom), safe=safe)
        bounds = self.safe if safe else self.frame
        return Rect(origin[0], origin[1], width * bounds.width, height * bounds.height)

    def clamp(self, point: Point, *, safe: bool = True) -> Point:
        bounds = self.safe if safe else self.frame
        return (min(max(point[0], bounds.left), bounds.right), min(max(point[1], bounds.bottom), bounds.top))


DEFAULT_LAYOUT = SafeAreaLayout()
