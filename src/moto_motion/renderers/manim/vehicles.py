"""Manim adapters. The SDK remains importable when Manim is not installed."""

from __future__ import annotations

from math import pi
from pathlib import Path

try:
    from manim import SVGMobject
except ImportError:  # pragma: no cover - exercised only in minimal installs
    SVGMobject = None

from ...assets import write_f1_car_svg
from ...core.themes import DEFAULT_THEME, Theme, vehicle_separation_color
from ...geometry import Trajectory
from ...models import F1CarModel


class F1Car:
    """Reusable Manim vehicle with stable named layer metadata."""

    # The authored SVG is drawn nose-first toward positive local Y.  Manim's
    # world heading uses +X as zero, so this correction keeps the asset nose
    # aligned with the trajectory tangent instead of introducing a 180-degree
    # reversal on vertical approaches.
    local_forward_angle = pi / 2

    layer_names = ("shadow-layer", "tyres", "wings", "suspension-arms", "sidepods", "engine-cover", "cockpit", "halo", "nose-cone", "highlights")

    def __init__(self, model: F1CarModel | None = None, asset_dir: str | Path = "assets/generated", theme: Theme = DEFAULT_THEME):
        if SVGMobject is None:
            raise RuntimeError("F1Car requires Manim; install the project dependencies first")
        self.model = model or F1CarModel()
        outline = vehicle_separation_color(theme, self.model.style.primary)
        # A distinct asset path prevents two differently liveried cars from
        # sharing Manim's parsed SVG cache.
        palette_key = "_".join(value.replace("#", "").lower() for value in (self.model.style.primary, self.model.style.secondary, outline))
        asset = write_f1_car_svg(Path(asset_dir) / f"f1_car_{palette_key}.svg", self.model.style.primary, self.model.style.secondary, outline)
        self.mobject = SVGMobject(str(asset)).scale(self.model.scale).rotate(self.model.rotation).move_to((*self.model.position, 0))

    def __getattr__(self, name):
        return getattr(self.mobject, name)

    @classmethod
    def rotation_for_heading(cls, heading: float) -> float:
        """Return the Manim rotation that points the car along *heading*.

        Trajectory geometry reports a standard world-space heading where 0 is
        +X.  Keeping the SVG forward-axis correction here prevents each scene
        from guessing how the reusable asset is authored.
        """
        return heading - cls.local_forward_angle

    @classmethod
    def pose_on_trajectory(cls, trajectory: Trajectory, progress: float) -> tuple[tuple[float, float], float]:
        """Return a constant-distance point and asset-corrected rotation."""
        progress = max(0.0, min(1.0, float(progress)))
        point = trajectory.point_at_distance(progress)
        parameter = trajectory.distance_to_parameter(progress * trajectory.length)
        return point, cls.rotation_for_heading(trajectory.heading(parameter))

    @classmethod
    def place_on_trajectory(cls, mobject, trajectory: Trajectory, progress: float = 0.0):
        """Place and absolutely align a vehicle before its first rendered frame."""
        point, rotation = cls.pose_on_trajectory(trajectory, progress)
        previous = getattr(mobject, "_moto_heading", 0.0)
        mobject.rotate(rotation - previous).move_to((*point, 0))
        mobject._moto_heading = rotation
        return mobject

    def animate_to(self, position, rotation=None, scale=None):
        target = self.model.transform(position, rotation, scale)
        animation = self.mobject.animate.move_to((*target.position, 0)).scale(target.scale / self.model.scale)
        if rotation is not None:
            animation = animation.rotate(rotation - self.model.rotation)
        self.model = target
        return animation
