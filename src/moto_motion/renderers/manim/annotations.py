"""Studio-style world-space technical annotations for Manim scenes."""

from __future__ import annotations

from typing import Sequence

try:
    from manim import BackgroundRectangle, Dot, VMobject, VGroup
except ImportError:  # pragma: no cover
    BackgroundRectangle = Dot = VMobject = VGroup = None


class TechnicalCallout:
    """A label connected to an exact world anchor by a restrained elbow leader.

    Labels stay clear of technical geometry while the leader preserves their
    relationship. Optional elbow points provide art-directed routing around
    tracks, vehicles, and other annotations.
    """

    def __init__(
        self,
        label,
        *,
        anchor: tuple[float, float],
        position: tuple[float, float],
        color: str,
        background: str,
        elbow_points: Sequence[tuple[float, float]] = (),
        target_radius: float = 0.045,
        stroke_width: float = 1.8,
    ):
        if VGroup is None:
            raise RuntimeError("TechnicalCallout requires Manim")

        plate = BackgroundRectangle(label, fill_color=background, fill_opacity=0.96, buff=0.12, stroke_width=0)
        label_group = VGroup(plate, label).move_to((*position, 0))
        dx, dy = position[0] - anchor[0], position[1] - anchor[1]
        if abs(dx) >= abs(dy):
            landing = label_group.get_left() if dx > 0 else label_group.get_right()
        else:
            landing = label_group.get_bottom() if dy > 0 else label_group.get_top()

        points = [(*anchor, 0), *((*point, 0) for point in elbow_points), landing]
        leader = VMobject().set_points_as_corners(points).set_stroke(color, stroke_width, opacity=0.84)
        target = Dot((*anchor, 0), radius=target_radius, color=color)
        self.label = label_group
        self.leader = leader
        self.target = target
        self.mobject = VGroup(leader, target, label_group).set_z_index(20)

    def __getattr__(self, name):
        return getattr(self.mobject, name)
