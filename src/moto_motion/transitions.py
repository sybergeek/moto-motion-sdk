"""Direction-aware transition specifications and optional Manim builders."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
from .core.layout import Point
from .core.themes import DEFAULT_THEME, Theme, blend_hex


@dataclass(frozen=True)
class TransitionSpec:
    kind: str
    duration: float
    direction: Point = (0.0, 1.0)
    source: str = "vehicle"
    blur: bool = False


class TransitionDirector:
    """Creates restrained transitions motivated by a moving object or viewpoint."""

    def __init__(self):
        self.history: list[TransitionSpec] = []

    def _add(self, spec: TransitionSpec) -> TransitionSpec:
        if spec.duration <= 0:
            raise ValueError("transition duration must be positive")
        if spec.kind not in {"directional_wipe", "directional_mask_wipe", "match_cut", "match_position_cut", "camera_push", "camera_pull", "vehicle_follow", "whip_pan", "speed_line_reveal", "technical_zoom", "telemetry_panel_slide", "object_reveal", "shape_morph"}:
            raise ValueError(f"unknown transition kind: {spec.kind}")
        self.history.append(spec)
        return spec

    def directional_wipe(self, direction: Point = (0.0, 1.0), duration: float = 0.55, *, source: str = "vehicle") -> TransitionSpec:
        return self._add(TransitionSpec("directional_wipe", duration, direction, source))

    def match_cut(self, source: str = "vehicle_heading", duration: float = 0.35, direction: Point = (1.0, 0.0)) -> TransitionSpec:
        return self._add(TransitionSpec("match_cut", duration, direction, source))

    def camera_push(self, duration: float = 0.8, *, blur: bool = False) -> TransitionSpec:
        return self._add(TransitionSpec("camera_push", duration, (0.0, 0.0), "camera", blur))

    def camera_pull(self, duration: float = 0.8, *, blur: bool = False) -> TransitionSpec:
        return self._add(TransitionSpec("camera_pull", duration, (0.0, 0.0), "camera", blur))

    def whip_pan(self, direction: Point, duration: float = 0.32) -> TransitionSpec:
        return self._add(TransitionSpec("whip_pan", duration, direction, "camera", True))

    def object_reveal(self, direction: Point, duration: float = 0.65, source: str = "vehicle") -> TransitionSpec:
        return self._add(TransitionSpec("object_reveal", duration, direction, source))

    def directional_mask_wipe(self, direction: Point = (1.0, 0.0), duration: float = 0.55) -> TransitionSpec:
        return self._add(TransitionSpec("directional_mask_wipe", duration, direction, "object_mask"))

    def vehicle_follow(self, direction: Point, duration: float = 0.75) -> TransitionSpec:
        return self._add(TransitionSpec("vehicle_follow", duration, direction, "vehicle_heading"))

    def speed_line_reveal(self, direction: Point, duration: float = 0.45) -> TransitionSpec:
        return self._add(TransitionSpec("speed_line_reveal", duration, direction, "vehicle_speed"))

    def match_position_cut(self, direction: Point, duration: float = 0.35) -> TransitionSpec:
        return self._add(TransitionSpec("match_position_cut", duration, direction, "object_position"))

    def technical_zoom_in(self, duration: float = 0.7) -> TransitionSpec:
        return self._add(TransitionSpec("technical_zoom", duration, (0.0, 0.0), "technical_anchor"))

    def telemetry_panel_slide(self, direction: Point = (1.0, 0.0), duration: float = 0.5) -> TransitionSpec:
        return self._add(TransitionSpec("telemetry_panel_slide", duration, direction, "screen_ui"))

    def object_driven_scene_reveal(self, direction: Point, duration: float = 0.65, source: str = "vehicle") -> TransitionSpec:
        return self.object_reveal(direction, duration, source)

    @staticmethod
    def theme_transition_colors(source: Theme, target: Theme, steps: int = 8) -> tuple[str, ...]:
        if steps < 2:
            raise ValueError("theme transitions require at least two color steps")
        return tuple(blend_hex(source.background, target.background, index / (steps - 1)) for index in range(steps))

    def manim_animation(self, spec: TransitionSpec, mobject):
        from manim import FadeIn, FadeOut, RIGHT, UP
        vector = RIGHT * spec.direction[0] + UP * spec.direction[1]
        if spec.kind in {"directional_wipe", "directional_mask_wipe", "object_reveal", "match_cut", "match_position_cut", "speed_line_reveal", "telemetry_panel_slide"}:
            return FadeIn(mobject, shift=vector * 0.45, run_time=spec.duration)
        if spec.kind in {"whip_pan", "vehicle_follow"}:
            return mobject.animate.shift(vector * 0.8).set_run_time(spec.duration)
        if spec.kind in {"camera_push", "technical_zoom"}:
            return mobject.animate.scale(1.08).set_run_time(spec.duration)
        if spec.kind == "camera_pull":
            return mobject.animate.scale(0.92).set_run_time(spec.duration)
        return FadeOut(mobject, run_time=spec.duration)


def fade_out_scene_foreground(scene, *, preserve: Iterable[object] = (), run_time: float = 0.28):
    """Build a scene-clear animation without exposing the camera background.

    Light editorial themes rely on an explicit backdrop mobject. Fading every
    root mobject during a scene change can briefly expose Manim's default
    background between scenes. Callers should preserve the active backdrop and
    replace it only after this animation has completed.
    """
    if run_time <= 0:
        raise ValueError("scene-clear duration must be positive")
    preserved = {id(item) for item in preserve}
    from manim import FadeOut

    return [
        FadeOut(item, run_time=run_time)
        for item in list(scene.mobjects)
        if id(item) not in preserved
    ]
