"""Original top-down MotoGP bike adapter with a proportioned vector silhouette."""

from __future__ import annotations

try:
    from manim import Circle, Ellipse, Line, Polygon, RoundedRectangle, VGroup
except ImportError:  # pragma: no cover
    Circle = Ellipse = Line = Polygon = RoundedRectangle = VGroup = None

from ...models import MotoGPBikeModel


class MotoGPBike:
    layer_names = ("shadow", "wheels", "chassis", "fairings", "rider", "cockpit", "details")

    def __init__(self, model: MotoGPBikeModel | None = None):
        if VGroup is None:
            raise RuntimeError("MotoGPBike requires Manim; install the project dependencies first")
        self.model = model or MotoGPBikeModel()
        style = self.model.style
        dark = "#0B1118"
        metal = "#718090"

        shadow = Ellipse(width=0.92, height=3.05, fill_color="#05080C", fill_opacity=0.30, stroke_width=0)
        front = RoundedRectangle(width=0.27, height=0.86, corner_radius=0.12, fill_color=dark, fill_opacity=1, stroke_color=metal, stroke_width=0.035).move_to((0, 1.43, 0))
        rear = RoundedRectangle(width=0.31, height=0.92, corner_radius=0.13, fill_color=dark, fill_opacity=1, stroke_color=metal, stroke_width=0.035).move_to((0, -1.42, 0))
        front_hub = Line((-0.09, 1.43, 0), (0.09, 1.43, 0), color=metal, stroke_width=1.5)
        rear_hub = Line((-0.10, -1.42, 0), (0.10, -1.42, 0), color=metal, stroke_width=1.5)

        chassis = Polygon(
            (0, 1.16, 0), (-0.20, 0.90, 0), (-0.30, 0.42, 0), (-0.18, 0.10, 0),
            (-0.24, -0.55, 0), (0, -1.12, 0), (0.24, -0.55, 0), (0.18, 0.10, 0),
            (0.30, 0.42, 0), (0.20, 0.90, 0),
            fill_color=style.primary, fill_opacity=1, stroke_color=metal, stroke_width=0.035,
        )
        left_fairing = Polygon((-0.18, 0.70, 0), (-0.56, 0.45, 0), (-0.48, 0.16, 0), (-0.18, 0.04, 0), fill_color=style.secondary, fill_opacity=0.95, stroke_color=style.primary, stroke_width=0.025)
        right_fairing = Polygon((0.18, 0.70, 0), (0.56, 0.45, 0), (0.48, 0.16, 0), (0.18, 0.04, 0), fill_color=style.secondary, fill_opacity=0.95, stroke_color=style.primary, stroke_width=0.025)
        tank = Ellipse(width=0.43, height=0.66, fill_color=style.primary, fill_opacity=1, stroke_color=metal, stroke_width=0.025).move_to((0, 0.48, 0))
        tail = Polygon((-0.18, -0.40, 0), (0, -0.92, 0), (0.18, -0.40, 0), fill_color=style.primary, fill_opacity=1, stroke_width=0)

        helmet = Circle(radius=0.16, fill_color=dark, fill_opacity=1, stroke_color=style.secondary, stroke_width=0.045).move_to((0, 0.14, 0))
        rider = Ellipse(width=0.28, height=0.56, fill_color=dark, fill_opacity=1, stroke_color=metal, stroke_width=0.025).move_to((0, -0.20, 0))
        cockpit = RoundedRectangle(width=0.25, height=0.30, corner_radius=0.07, fill_color="#263746", fill_opacity=1, stroke_color=style.secondary, stroke_width=0.025).move_to((0, 0.55, 0))
        handlebar = Line((-0.43, 0.78, 0), (0.43, 0.78, 0), color=metal, stroke_width=0.045)
        left_grip = Circle(radius=0.055, fill_color=style.secondary, fill_opacity=1, stroke_width=0).move_to((-0.43, 0.78, 0))
        right_grip = Circle(radius=0.055, fill_color=style.secondary, fill_opacity=1, stroke_width=0).move_to((0.43, 0.78, 0))
        left_wing = Polygon((-0.27, 0.72, 0), (-0.60, 0.62, 0), (-0.38, 0.53, 0), fill_color=style.primary, fill_opacity=1, stroke_color=metal, stroke_width=0.02)
        right_wing = Polygon((0.27, 0.72, 0), (0.60, 0.62, 0), (0.38, 0.53, 0), fill_color=style.primary, fill_opacity=1, stroke_color=metal, stroke_width=0.02)
        exhaust = Line((0.25, -0.30, 0), (0.48, -0.72, 0), color=metal, stroke_width=0.06)
        centerline = Line((0, -0.98, 0), (0, 1.05, 0), color=style.secondary, stroke_width=0.025, stroke_opacity=0.7)

        wheels = VGroup(front, rear, front_hub, rear_hub)
        fairings = VGroup(left_fairing, right_fairing, tank, tail)
        details = VGroup(handlebar, left_grip, right_grip, left_wing, right_wing, exhaust, centerline)
        self.mobject = VGroup(shadow, wheels, chassis, fairings, VGroup(rider, helmet), VGroup(cockpit), details)
        self.mobject.scale(self.model.scale).rotate(self.model.rotation).move_to((*self.model.position, 0))

    def __getattr__(self, name):
        return getattr(self.mobject, name)
