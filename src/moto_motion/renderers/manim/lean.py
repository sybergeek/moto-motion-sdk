"""Front-view MotoGP lean rig and technical physics overlays."""

from __future__ import annotations

from math import cos, pi, radians, sin

try:
    from manim import Arc, Arrow, BackgroundRectangle, Circle, DashedLine, Dot, Ellipse, Line, ORIGIN, Polygon, RoundedRectangle, Text, VGroup
except ImportError:  # pragma: no cover
    Arc = Arrow = BackgroundRectangle = Circle = DashedLine = Dot = Ellipse = Line = Polygon = RoundedRectangle = Text = VGroup = None
    ORIGIN = (0, 0, 0)

from ...core.themes import DEFAULT_THEME, Theme
from ...models import LeanPose


class MotoGPLeanRig:
    """Articulated front-view motorcycle+rider pivoting at tyre contact."""

    layer_names = ("shadow", "tyre", "chassis", "fairing", "rider", "details")

    def __init__(self, pose: LeanPose | None = None, *, theme: Theme = DEFAULT_THEME, primary: str | None = None, secondary: str | None = None, contact_position: tuple[float, float] = (0.0, 0.0), scale: float = 1.0):
        if VGroup is None:
            raise RuntimeError("MotoGPLeanRig requires Manim")
        self.pose = pose or LeanPose()
        self.theme = theme
        self.primary = primary or theme.accent
        self.secondary = secondary or theme.semantic.acceleration
        self.contact_position = contact_position
        self.scale = scale
        self.layers: dict[str, object] = {}
        self.mobject = self._build(self.pose)

    def _build(self, pose: LeanPose):
        dark, metal = "#0A1118", self.theme.secondary_text
        tyre = RoundedRectangle(width=0.32, height=1.42, corner_radius=0.16, fill_color=dark, fill_opacity=1, stroke_color=metal, stroke_width=1.5).move_to((0, 0.71, 0))
        tyre_center = DashedLine((0, 0.09, 0), (0, 1.32, 0), color="#52616E", stroke_width=1.1, dash_length=0.10)
        mudguard = Arc(radius=0.33, start_angle=0.15, angle=pi - 0.30, color=self.primary, stroke_width=5).move_to((0, 1.20, 0))
        forks = VGroup(
            Line((-0.10, 0.92, 0), (-0.24, 1.72, 0), color=metal, stroke_width=3.4),
            Line((0.10, 0.92, 0), (0.24, 1.72, 0), color=metal, stroke_width=3.4),
        )
        chassis = Polygon(
            (-0.24, 1.12, 0), (-0.43, 1.55, 0), (-0.34, 2.05, 0),
            (-0.18, 2.33, 0), (0, 2.45, 0), (0.18, 2.33, 0),
            (0.34, 2.05, 0), (0.43, 1.55, 0), (0.24, 1.12, 0),
            fill_color=self.primary, fill_opacity=1, stroke_color=metal, stroke_width=1.2,
        )
        side_fairings = VGroup(
            Polygon((-0.31, 1.48, 0), (-0.78, 1.37, 0), (-0.44, 1.23, 0), fill_color=self.secondary, fill_opacity=0.92, stroke_width=0),
            Polygon((0.31, 1.48, 0), (0.78, 1.37, 0), (0.44, 1.23, 0), fill_color=self.secondary, fill_opacity=0.92, stroke_width=0),
        )
        intake = Polygon((-0.18, 1.55, 0), (0, 1.34, 0), (0.18, 1.55, 0), (0, 1.82, 0), fill_color=dark, fill_opacity=1, stroke_color=self.secondary, stroke_width=1.0)
        screen = RoundedRectangle(width=0.36, height=0.30, corner_radius=0.09, fill_color="#1B3442", fill_opacity=0.95, stroke_color=self.secondary, stroke_width=1.0).move_to((0, 2.15, 0))
        handlebar = Line((-0.59, 1.91, 0), (0.59, 1.91, 0), color=metal, stroke_width=3.2)
        grips = VGroup(
            Circle(radius=0.06, fill_color=dark, fill_opacity=1, stroke_color=self.secondary, stroke_width=1).move_to((-0.59, 1.91, 0)),
            Circle(radius=0.06, fill_color=dark, fill_opacity=1, stroke_color=self.secondary, stroke_width=1).move_to((0.59, 1.91, 0)),
        )
        bike = VGroup(tyre, tyre_center, mudguard, forks, chassis, side_fairings, intake, screen, handlebar, grips)
        bike.rotate(-radians(pose.bike_lean_degrees), about_point=ORIGIN)

        pelvis = pose.rider_pelvis
        rider_angle = radians(pose.rider_absolute_lean_degrees)

        def rider_point(x: float, y: float) -> tuple[float, float, float]:
            return (pelvis[0] + x * cos(rider_angle) + y * sin(rider_angle), pelvis[1] - x * sin(rider_angle) + y * cos(rider_angle), 0)

        rider_local = VGroup(
            Ellipse(width=0.50, height=0.68, fill_color=dark, fill_opacity=1, stroke_color=metal, stroke_width=1.2).move_to((0, 0.33, 0)),
            Polygon((-0.20, 0.18, 0), (0, 0.02, 0), (0.20, 0.18, 0), (0.16, 0.55, 0), (-0.16, 0.55, 0), fill_color=self.primary, fill_opacity=0.92, stroke_width=0),
            Circle(radius=0.205, fill_color=self.secondary, fill_opacity=1, stroke_color=self.theme.text, stroke_width=1.1).move_to((0, 0.84, 0)),
            RoundedRectangle(width=0.29, height=0.12, corner_radius=0.05, fill_color=dark, fill_opacity=1, stroke_width=0).move_to((0.07, 0.84, 0)),
            Line((-0.23, 0.55, 0), (0.23, 0.55, 0), color=self.primary, stroke_width=4.2),
        )
        rider_local.rotate(-rider_angle, about_point=ORIGIN).shift((pelvis[0], pelvis[1], 0))
        left_grip, right_grip = grips[0].get_center(), grips[1].get_center()
        limbs = VGroup(
            Line(rider_point(-0.18, 0.52), left_grip, color=dark, stroke_width=5.5),
            Line(rider_point(0.18, 0.52), right_grip, color=dark, stroke_width=5.5),
            Line(rider_point(-0.12, 0.04), chassis.get_corner((-1, -1, 0)), color=dark, stroke_width=6.5),
            Line(rider_point(0.12, 0.04), chassis.get_corner((1, -1, 0)), color=dark, stroke_width=6.5),
        )
        rider = VGroup(limbs, rider_local)
        contact_glow = Ellipse(width=0.45, height=0.10, fill_color=self.theme.semantic.focus, fill_opacity=0.30, stroke_width=0)
        shadow = Ellipse(width=2.3, height=0.18, fill_color="#05090D", fill_opacity=0.36, stroke_width=0).shift((0, -0.04, 0))
        result = VGroup(shadow, contact_glow, bike, rider).scale(self.scale, about_point=ORIGIN).shift((*self.contact_position, 0))
        self.layers = {"shadow": shadow, "tyre": VGroup(tyre, tyre_center, mudguard), "chassis": VGroup(forks, chassis), "fairing": VGroup(side_fairings, intake, screen), "rider": rider, "details": VGroup(handlebar, grips, contact_glow)}
        return result

    @property
    def contact_point(self) -> tuple[float, float, float]:
        return (*self.contact_position, 0)

    def world_point(self, point: tuple[float, float]) -> tuple[float, float, float]:
        return (self.contact_position[0] + point[0] * self.scale, self.contact_position[1] + point[1] * self.scale, 0)

    def set_pose(self, pose: LeanPose):
        self.pose = pose
        self.mobject.become(self._build(pose))
        return self.mobject

    def __getattr__(self, name):
        return getattr(self.mobject, name)


def lean_angle_overlay(
    rig: MotoGPLeanRig,
    *,
    label: str | None = None,
    show_label: bool = True,
    label_position: tuple[float, float] | None = None,
):
    """Draw bike lean about the contact point with an optionally detached label."""
    pose, radius = rig.pose, 0.82 * rig.scale
    arc = Arc(radius=radius, start_angle=pi / 2, angle=-radians(pose.bike_lean_degrees), color=rig.theme.semantic.focus, stroke_width=4).shift(rig.contact_point)
    vertical = DashedLine(rig.contact_point, (rig.contact_position[0], rig.contact_position[1] + 1.45 * rig.scale, 0), color=rig.theme.secondary_text, stroke_width=2, dash_length=0.08)
    result = VGroup(vertical, arc)
    if show_label:
        text = Text(label or f"{pose.bike_lean_degrees:.0f}°  BIKE LEAN", font="IBM Plex Mono", font_size=17, color=rig.theme.semantic.focus)
        if label_position is None:
            text.next_to(arc, (1, 0, 0), buff=0.12)
        else:
            text.move_to((*label_position, 0))
            arc_end = arc.get_end()
            leader = Line(arc_end, (text.get_left()[0] - 0.08, text.get_center()[1], 0), color=rig.theme.semantic.focus, stroke_width=1.5)
            result.add(leader)
        result.add(text)
    return result


def center_of_mass_overlay(
    rig: MotoGPLeanRig,
    *,
    compact: bool = False,
    show_label: bool = True,
    label_text: str = "CENTER OF MASS",
    label_offset: tuple[float, float] = (0.28, 0.16),
    label_position: tuple[float, float] | None = None,
):
    """Visualize the combined bike-and-rider center of mass."""
    point = rig.world_point(rig.pose.combined_com)
    line = DashedLine(rig.contact_point, point, color=rig.theme.semantic.positive_delta, stroke_width=3, dash_length=0.09)
    dot = Dot(point, radius=0.09 if compact else 0.12, color=rig.theme.semantic.positive_delta)
    result = VGroup(line, dot)
    if show_label:
        position = label_position or (point[0] + label_offset[0], point[1] + label_offset[1])
        label = Text(label_text, font="IBM Plex Mono", font_size=13 if compact else 16, color=rig.theme.semantic.positive_delta).move_to((*position, 0))
        if label_position is not None:
            leader = Line(point, (label.get_right()[0] + 0.08, label.get_center()[1], 0), color=rig.theme.semantic.positive_delta, stroke_width=1.4)
            result.add(leader)
        result.add(label)
    return result


def force_vector_overlay(rig: MotoGPLeanRig):
    """Create high-contrast force vectors that remain legible over the rig."""
    com, contact = rig.world_point(rig.pose.combined_com), rig.contact_point
    force = rig.pose.normalized_road_force

    def outlined_arrow(start, end, color: str):
        halo = Arrow(start, end, buff=0, color="#081017", stroke_width=8.0, tip_length=0.21)
        foreground = Arrow(start, end, buff=0, color=color, stroke_width=3.2, tip_length=0.15)
        return VGroup(halo, foreground)

    gravity = outlined_arrow(com, (com[0], com[1] - 1.16 * rig.scale, 0), rig.theme.semantic.braking)
    lateral = outlined_arrow(
        (contact[0], contact[1] + 0.04, 0),
        (contact[0] + 1.18 * rig.scale, contact[1] + 0.04, 0),
        rig.theme.semantic.positive_delta,
    )
    resultant = outlined_arrow(
        contact,
        (contact[0] + force[0] * 1.48 * rig.scale, contact[1] + force[1] * 1.48 * rig.scale, 0),
        rig.theme.text,
    )

    def callout(value: str, position: tuple[float, float], color: str):
        text = Text(value, font="IBM Plex Mono", font_size=13, color=color).move_to((*position, 0))
        plate = BackgroundRectangle(text, fill_color=rig.theme.background, fill_opacity=0.90, buff=0.08, stroke_width=0)
        return VGroup(plate, text)

    return VGroup(
        gravity, lateral, resultant,
        callout("GRAVITY", (com[0] - 0.82, com[1] - 0.64), rig.theme.semantic.braking),
        callout("LATERAL TYRE FORCE", (contact[0] + 1.15, contact[1] - 0.34), rig.theme.semantic.positive_delta),
        callout("ROAD FORCE", (contact[0] + 3.90, contact[1] + 2.05), rig.theme.text),
    )


def contact_patch_closeup(theme: Theme = DEFAULT_THEME):
    """Original front-view tyre/contact-patch technical illustration."""
    road = Line((-2.75, -1.55, 0), (2.75, -1.55, 0), color=theme.border, stroke_width=8)
    tyre = RoundedRectangle(width=0.92, height=3.25, corner_radius=0.44, fill_color="#0A1118", fill_opacity=1, stroke_color=theme.secondary_text, stroke_width=2).move_to((0, -0.02, 0))
    grooves = VGroup(*[Arc(radius=0.38 + index * 0.07, start_angle=-0.35, angle=0.70, color="#52616E", stroke_width=1.2).move_to((0.07, -0.1 + index * 0.38, 0)) for index in range(-2, 4)])
    tyre_stack = VGroup(tyre, grooves).rotate(-0.16, about_point=ORIGIN)
    patch = Ellipse(width=1.10, height=0.20, fill_color=theme.semantic.focus, fill_opacity=0.92, stroke_color=theme.text, stroke_width=1.2).move_to((0.25, -1.49, 0))
    shear = VGroup(*[Arrow((x, -1.47, 0), (x + 0.50, -1.47, 0), buff=0, color=theme.semantic.acceleration, stroke_width=2.6, tip_length=0.12) for x in (-0.24, 0.08, 0.40)])
    return VGroup(road, tyre_stack, patch, shear)
