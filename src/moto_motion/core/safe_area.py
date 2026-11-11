"""Resolution-independent layout and safe-area validation primitives.

The public logical coordinate system is normalized, top-left origin.  Manim's
world coordinates are an adapter at the boundary; scene authors should not
store pixel coordinates in reel code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import cos, radians, sin
from typing import Iterable, Sequence


Point = tuple[float, float]


class LayoutClass(StrEnum):
    STRICT_SAFE = "strict_safe"
    SAFE_ANCHOR = "safe_anchor"
    FULL_BLEED = "full_bleed"


class LayoutError(ValueError):
    """Raised when a layout profile or strict element is invalid."""


@dataclass(frozen=True)
class NormalizedRect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains(self, point: Point, *, epsilon: float = 1e-9) -> bool:
        return self.x - epsilon <= point[0] <= self.right + epsilon and self.y - epsilon <= point[1] <= self.bottom + epsilon

    def inset(self, padding: float) -> "NormalizedRect":
        return NormalizedRect(self.x + padding, self.y + padding, self.width - 2 * padding, self.height - 2 * padding)


@dataclass(frozen=True)
class PixelRect:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class SafeAreaProfile:
    id: str
    left: float
    right: float
    top: float
    bottom: float

    def __post_init__(self) -> None:
        if min(self.left, self.right, self.top, self.bottom) < 0:
            raise LayoutError("safe-area margins cannot be negative")
        if self.left + self.right >= 1 or self.top + self.bottom >= 1:
            raise LayoutError("safe-area margins must leave a positive usable rectangle")

    @property
    def rect(self) -> NormalizedRect:
        return NormalizedRect(self.left, self.top, 1 - self.left - self.right, 1 - self.top - self.bottom)


@dataclass(frozen=True)
class ExportProfile:
    id: str
    width: int
    height: int
    fps: int
    video_codec: str
    audio_codec: str
    audio_sample_rate: int
    safe_area_profile: str


INSTAGRAM_REELS_V1 = SafeAreaProfile("instagram_reels_v1", left=.1056, right=.1056, top=.09375, bottom=.1953)
ARCHIVAL_MASTER = SafeAreaProfile("archival_master", left=0.0, right=0.0, top=0.0, bottom=0.0)

EXPORT_PROFILES = {
    "instagram_reels_v1": ExportProfile("instagram_reels_v1", 1080, 1920, 30, "h264", "aac", 48000, "instagram_reels_v1"),
    "archival_master": ExportProfile("archival_master", 2160, 3840, 30, "h264", "pcm_s16le", 48000, "archival_master"),
}
SAFE_AREA_PROFILES = {INSTAGRAM_REELS_V1.id: INSTAGRAM_REELS_V1, ARCHIVAL_MASTER.id: ARCHIVAL_MASTER}


@dataclass(frozen=True)
class LogicalCanvas:
    width: int
    height: int
    safe_area: SafeAreaProfile = INSTAGRAM_REELS_V1
    manim_frame_width: float = 9.0

    @property
    def manim_frame_height(self) -> float:
        return self.manim_frame_width * self.height / self.width

    @property
    def safe_rect(self) -> NormalizedRect:
        return self.safe_area.rect

    def get_canvas_dimensions(self) -> tuple[int, int]:
        return self.width, self.height

    def normalized_to_pixels(self, point: Point) -> Point:
        return point[0] * self.width, point[1] * self.height

    def pixels_to_normalized(self, point: Point) -> Point:
        return point[0] / self.width, point[1] / self.height

    def normalized_to_manim(self, point: Point) -> Point:
        return ((point[0] - .5) * self.manim_frame_width, (.5 - point[1]) * self.manim_frame_height)

    def manim_to_normalized(self, point: Point) -> Point:
        return (point[0] / self.manim_frame_width + .5, .5 - point[1] / self.manim_frame_height)

    def rect_to_pixels(self, rect: NormalizedRect) -> PixelRect:
        return PixelRect(rect.x * self.width, rect.y * self.height, rect.width * self.width, rect.height * self.height)

    def safe_rect_pixels(self) -> PixelRect:
        return self.rect_to_pixels(self.safe_rect)

    def caption_band(self, height: float = .09, bottom_gap: float = .035) -> NormalizedRect:
        safe = self.safe_rect
        return NormalizedRect(safe.x, safe.bottom - bottom_gap - height, safe.width, height)


def get_canvas_dimensions(width: int, height: int) -> tuple[int, int]:
    return LogicalCanvas(width, height).get_canvas_dimensions()


def normalized_to_pixels(point: Point, width: int, height: int) -> Point:
    return LogicalCanvas(width, height).normalized_to_pixels(point)


def pixels_to_normalized(point: Point, width: int, height: int) -> Point:
    return LogicalCanvas(width, height).pixels_to_normalized(point)


def normalized_to_manim(point: Point, width: int, height: int, frame_width: float = 9.0) -> Point:
    return LogicalCanvas(width, height, manim_frame_width=frame_width).normalized_to_manim(point)


def manim_to_normalized(point: Point, width: int, height: int, frame_width: float = 9.0) -> Point:
    return LogicalCanvas(width, height, manim_frame_width=frame_width).manim_to_normalized(point)


def fit_to_safe_area(bounds: NormalizedRect, canvas: LogicalCanvas, *, padding: float = 0.0) -> float:
    safe = canvas.safe_rect.inset(padding)
    if bounds.width <= 0 or bounds.height <= 0:
        raise LayoutError("element bounds must have positive width and height")
    return min(1.0, safe.width / bounds.width, safe.height / bounds.height)


def position_within_safe_area(center: Point, size: Point, canvas: LogicalCanvas, *, padding: float = 0.0) -> Point:
    safe = canvas.safe_rect.inset(padding)
    half_w, half_h = size[0] / 2, size[1] / 2
    if half_w * 2 > safe.width or half_h * 2 > safe.height:
        raise LayoutError("element cannot fit inside the safe rectangle")
    return (min(max(center[0], safe.x + half_w), safe.right - half_w), min(max(center[1], safe.y + half_h), safe.bottom - half_h))


@dataclass(frozen=True)
class LayoutElement:
    id: str
    classification: LayoutClass
    samples: tuple[tuple[float, NormalizedRect], ...]
    critical_anchors: tuple[tuple[str, Point], ...] = ()


@dataclass(frozen=True)
class LayoutViolation:
    element_id: str
    classification: LayoutClass
    timestamp: float
    boundary: str
    severity: str
    message: str
    bounds: NormalizedRect | None = None


@dataclass(frozen=True)
class SceneVisualContract:
    """Minimum semantic proof required for a production scene."""

    scene_id: str
    primary_subject: str
    primary_subject_label: str
    spoken_claim: str
    visual_proof: str
    full_bleed_background: bool


def validate_camera_canvas(canvas: LogicalCanvas, *, frame_width: float, frame_height: float, epsilon: float = 1e-6) -> list[LayoutViolation]:
    """Flag camera/logical-canvas mismatches that create an outer matte."""
    if abs(frame_width - canvas.manim_frame_width) <= epsilon and abs(frame_height - canvas.manim_frame_height) <= epsilon:
        return []
    return [LayoutViolation("camera", LayoutClass.FULL_BLEED, 0.0, "camera-frame", "error", "camera dimensions do not match the logical canvas; full-bleed layers may render as an unintended matte")]


def validate_scene_visual_contracts(contracts: Iterable[SceneVisualContract]) -> list[LayoutViolation]:
    """Require a named, labeled and visually supported claim per scene."""
    violations: list[LayoutViolation] = []
    for contract in contracts:
        for boundary, value in {
            "primary-subject": contract.primary_subject,
            "subject-label": contract.primary_subject_label,
            "spoken-claim": contract.spoken_claim,
            "visual-proof": contract.visual_proof,
        }.items():
            if not value.strip():
                violations.append(LayoutViolation(contract.scene_id, LayoutClass.STRICT_SAFE, 0.0, boundary, "error", "scene is missing required semantic-proof metadata"))
        if not contract.full_bleed_background:
            violations.append(LayoutViolation(contract.scene_id, LayoutClass.FULL_BLEED, 0.0, "full-bleed-background", "warning", "safe-area protection applies to semantic elements, not the entire canvas; use a full-bleed background unless intentionally letterboxed"))
    return violations


def _outside(rect: NormalizedRect, safe: NormalizedRect) -> list[str]:
    return [
        *(["left"] if rect.x < safe.x else []),
        *(["right"] if rect.right > safe.right else []),
        *(["top"] if rect.y < safe.y else []),
        *(["bottom"] if rect.bottom > safe.bottom else []),
    ]


def validate_scene_layout(canvas: LogicalCanvas, elements: Iterable[LayoutElement]) -> list[LayoutViolation]:
    violations: list[LayoutViolation] = []
    for element in elements:
        if element.classification is LayoutClass.FULL_BLEED:
            continue
        for timestamp, bounds in element.samples:
            if element.classification is LayoutClass.STRICT_SAFE:
                for boundary in _outside(bounds, canvas.safe_rect):
                    violations.append(LayoutViolation(element.id, element.classification, timestamp, boundary, "error", "strict-safe bounds leave the safe rectangle", bounds))
            else:
                for anchor_id, anchor in element.critical_anchors:
                    if not canvas.safe_rect.contains(anchor):
                        violations.append(LayoutViolation(element.id, element.classification, timestamp, anchor_id, "error", "critical anchor is outside the safe rectangle", bounds))
    return violations


def validate_element_collisions(elements: Iterable[LayoutElement], *, ignore_pairs: frozenset[tuple[str, str]] = frozenset()) -> list[LayoutViolation]:
    """Flag overlapping semantic elements sampled at the same animation time.

    Full-bleed and safe-anchor geometry are deliberately excluded: a road can
    pass behind a label, but two strict-safe labels or a caption and a result
    card cannot occupy the same space unless explicitly exempted.
    """
    candidates = [element for element in elements if element.classification is LayoutClass.STRICT_SAFE]
    violations: list[LayoutViolation] = []
    for index, first in enumerate(candidates):
        for second in candidates[index + 1:]:
            if (first.id, second.id) in ignore_pairs or (second.id, first.id) in ignore_pairs:
                continue
            for first_time, first_bounds in first.samples:
                for second_time, second_bounds in second.samples:
                    if abs(first_time - second_time) > 1e-6:
                        continue
                    overlaps = first_bounds.x < second_bounds.right and first_bounds.right > second_bounds.x and first_bounds.y < second_bounds.bottom and first_bounds.bottom > second_bounds.y
                    if overlaps:
                        violations.append(LayoutViolation(first.id, LayoutClass.STRICT_SAFE, first_time, f"overlap:{second.id}", "error", "strict-safe semantic elements overlap", first_bounds))
    return violations


def make_safe_area_overlay(canvas: LogicalCanvas, elements: Sequence[LayoutElement] = ()):
    """Return a Manim overlay group; imported lazily so core math stays headless."""
    from manim import DashedVMobject, Dot, Rectangle, VGroup

    frame = Rectangle(width=canvas.manim_frame_width, height=canvas.manim_frame_height, stroke_color="#6B7280", stroke_width=1, fill_opacity=0)
    safe = canvas.safe_rect
    center = canvas.normalized_to_manim((safe.x + safe.width / 2, safe.y + safe.height / 2))
    safe_box = Rectangle(width=safe.width * canvas.manim_frame_width, height=safe.height * canvas.manim_frame_height, stroke_color="#F4C95D", stroke_width=2, fill_opacity=0).move_to((*center, 0))
    overlay = VGroup(frame, DashedVMobject(safe_box, num_dashes=48))
    colors = {LayoutClass.STRICT_SAFE: "#F04444", LayoutClass.SAFE_ANCHOR: "#F4C95D", LayoutClass.FULL_BLEED: "#4ADE80"}
    for element in elements:
        if not element.samples:
            continue
        _, bounds = element.samples[0]
        center = canvas.normalized_to_manim((bounds.x + bounds.width / 2, bounds.y + bounds.height / 2))
        box = Rectangle(width=bounds.width * canvas.manim_frame_width, height=bounds.height * canvas.manim_frame_height, stroke_color=colors[element.classification], stroke_width=2, fill_opacity=0).move_to((*center, 0))
        overlay.add(box)
        for _, anchor in element.critical_anchors:
            point = canvas.normalized_to_manim(anchor)
            overlay.add(Dot((*point, 0), radius=.045, color=colors[element.classification]))
    return overlay
