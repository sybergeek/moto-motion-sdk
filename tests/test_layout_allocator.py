import pytest

from moto_motion.core.layout_allocator import LayoutAllocator, LayoutRequest
from moto_motion.core.safe_area import LogicalCanvas, NormalizedRect, SafeAreaProfile


def canvas():
    return LogicalCanvas(1080, 1440, safe_area=SafeAreaProfile("carousel", .1, .1, .05, .05))


def test_allocator_reflows_to_an_alternative_without_overlap():
    report = LayoutAllocator(canvas()).resolve([
        LayoutRequest("headline", NormalizedRect(.2, .2, .6, .2), priority=10),
        LayoutRequest("body", NormalizedRect(.2, .2, .6, .2), alternatives=(NormalizedRect(.2, .45, .6, .15),), priority=5),
    ])
    assert report.allowed
    assert report.allocations[1].reflowed


def test_allocator_reports_unresolved_collision():
    report = LayoutAllocator(canvas()).resolve([
        LayoutRequest("headline", NormalizedRect(.2, .2, .6, .2), priority=10),
        LayoutRequest("body", NormalizedRect(.2, .2, .6, .2), priority=5),
    ])
    assert not report.allowed
    assert report.violations[0].boundary == "unresolved-overlap"

