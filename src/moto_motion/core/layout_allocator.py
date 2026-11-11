"""Deterministic semantic layout allocation shared by Reels and carousels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .safe_area import LayoutClass, LayoutViolation, LogicalCanvas, NormalizedRect, validate_scene_layout


@dataclass(frozen=True)
class LayoutRequest:
    element_id: str
    preferred: NormalizedRect
    alternatives: tuple[NormalizedRect, ...] = ()
    classification: LayoutClass = LayoutClass.STRICT_SAFE
    priority: int = 0
    min_width: float = 0.0
    min_height: float = 0.0
    shrinkable: bool = False
    allow_overlap_with: frozenset[str] = frozenset()


@dataclass(frozen=True)
class LayoutAllocation:
    element_id: str
    bounds: NormalizedRect
    classification: LayoutClass = LayoutClass.STRICT_SAFE
    scale: float = 1.0
    reflowed: bool = False


@dataclass(frozen=True)
class LayoutAllocationReport:
    allocations: tuple[LayoutAllocation, ...]
    violations: tuple[LayoutViolation, ...]

    @property
    def allowed(self) -> bool:
        return not any(item.severity == "error" for item in self.violations)


def _overlap(first: NormalizedRect, second: NormalizedRect) -> bool:
    return first.x < second.right and first.right > second.x and first.y < second.bottom and first.bottom > second.y


class LayoutAllocator:
    """Place semantic elements without silently allowing critical overlaps."""

    def __init__(self, canvas: LogicalCanvas):
        self.canvas = canvas

    def resolve(self, requests: Iterable[LayoutRequest]) -> LayoutAllocationReport:
        ordered = sorted(tuple(requests), key=lambda item: (-item.priority, item.element_id))
        allocations: list[LayoutAllocation] = []
        violations: list[LayoutViolation] = []
        for request in ordered:
            candidates = (request.preferred, *request.alternatives)
            chosen: LayoutAllocation | None = None
            for index, bounds in enumerate(candidates):
                if self._fits(request, bounds) and not self._collides(request, bounds, allocations):
                    chosen = LayoutAllocation(request.element_id, bounds, request.classification, 1.0, index > 0)
                    break
            if chosen is None and request.shrinkable:
                for scale in (.95, .90, .85, .80):
                    bounds = self._shrink(request.preferred, scale)
                    if self._fits(request, bounds) and not self._collides(request, bounds, allocations):
                        chosen = LayoutAllocation(request.element_id, bounds, request.classification, scale, True)
                        break
            if chosen is None:
                violations.append(LayoutViolation(request.element_id, request.classification, 0.0, "unresolved-overlap", "error", "layout allocator could not place the semantic element without an unsafe collision", request.preferred))
            else:
                allocations.append(chosen)
        violations.extend(validate_scene_layout(self.canvas, [LayoutElementAdapter(item) for item in allocations]))
        return LayoutAllocationReport(tuple(allocations), tuple(violations))

    def _fits(self, request: LayoutRequest, bounds: NormalizedRect) -> bool:
        if bounds.width < request.min_width or bounds.height < request.min_height:
            return False
        if request.classification is LayoutClass.FULL_BLEED:
            return True
        safe = self.canvas.safe_rect
        return safe.x <= bounds.x and safe.y <= bounds.y and safe.right >= bounds.right and safe.bottom >= bounds.bottom

    @staticmethod
    def _collides(request: LayoutRequest, bounds: NormalizedRect, allocations: list[LayoutAllocation]) -> bool:
        return any(_overlap(bounds, item.bounds) and item.element_id not in request.allow_overlap_with for item in allocations)

    @staticmethod
    def _shrink(bounds: NormalizedRect, scale: float) -> NormalizedRect:
        width, height = bounds.width * scale, bounds.height * scale
        return NormalizedRect(bounds.x + (bounds.width - width) / 2, bounds.y + (bounds.height - height) / 2, width, height)


@dataclass(frozen=True)
class LayoutElementAdapter:
    allocation: LayoutAllocation
    @property
    def id(self) -> str:
        return self.allocation.element_id

    @property
    def samples(self) -> tuple[tuple[float, NormalizedRect], ...]:
        return ((0.0, self.allocation.bounds),)

    @property
    def classification(self) -> LayoutClass:
        return self.allocation.classification

    @property
    def critical_anchors(self) -> tuple[tuple[str, tuple[float, float]], ...]:
        return ()

