"""Production-style portrait explainer: Why Braking Later Can Make You Slower."""

from dataclasses import dataclass
from manim import *  # noqa: F403

from moto_motion.camera import CameraRig
from moto_motion.core.themes import DEFAULT_THEME, Theme
from moto_motion.effects import smoothstep, trajectory_speed_profile
from moto_motion.geometry import Trajectory
from moto_motion.models import F1CarModel, VehicleStyle
from moto_motion.renderers.manim.annotations import TechnicalCallout
from moto_motion.renderers.manim.circuit import path_mobject, trajectory_history
from moto_motion.renderers.manim.vehicles import F1Car
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.transitions import TransitionDirector
from moto_motion.typography import HighlightedText, NumericCounter, TypographySystem


@dataclass(frozen=True)
class Beat:
    name: str
    start: float
    end: float


BEATS = (
    Beat("approach", 0.0, 3.0),
    Beat("braking_comparison", 3.0, 8.0),
    Beat("rotation_and_throttle", 8.0, 15.0),
    Beat("exit_gain", 15.0, 20.0),
    Beat("final_freeze", 20.0, 24.6),
)

TRACK_APPROACH = Trajectory(((0.0, 4.4), (0.0, 3.3), (0.0, 2.1), (0.0, 1.2)))
TRACK_CORNER = Trajectory(((0.0, 1.2), (0.0, 0.0), (0.85, -1.1), (2.2, -1.1)))
TRACK_EXIT = Trajectory(((2.2, -1.1), (3.5, -1.1), (5.0, -1.1), (6.6, -1.1)))

APPROACH_RED = Trajectory(((-0.55, 4.4), (-0.55, 3.3), (-0.55, 2.1), (-0.55, 1.2)))
APPROACH_CYAN = Trajectory(((0.55, 4.4), (0.55, 3.3), (0.55, 2.1), (0.55, 1.2)))
RED_CORNER = Trajectory(((-0.55, 1.2), (-0.55, -0.55), (0.55, -1.48), (2.2, -1.38)))
CYAN_CORNER = Trajectory(((0.55, 1.2), (0.55, 0.38), (1.16, -0.808), (2.2, -0.86)))
RED_EXIT = Trajectory(((2.2, -1.38), (2.75, -1.3467), (3.30, -1.2067), (3.70, -1.18)))
CYAN_EXIT = Trajectory(((2.2, -0.86), (3.0, -0.90), (3.85, -1.08), (4.55, -1.08)))
RED_STRAIGHT = Trajectory(((3.70, -1.18), (4.15, -1.15), (4.70, -1.12), (5.15, -1.1)))
CYAN_STRAIGHT = Trajectory(((4.55, -1.08), (5.25, -1.08), (5.95, -1.09), (6.55, -1.1)))

APPROACH_DURATION = 1.9
CORNER_DURATION = 5.0
EXIT_DURATION = 7.0
STRAIGHT_DURATION = 5.0


def _path_mobject(paths: tuple[Trajectory, ...], color: str, width: float, *, extend: bool = False):
    extension = 8.0 if extend else 0.0
    return path_mobject(paths, color, width, extend_start=extension, extend_end=extension)


def follow_path(mobject, trajectory: Trajectory, alpha: float, speed_profile=None):
    progress = speed_profile(alpha) if speed_profile else smoothstep(alpha)
    return F1Car.place_on_trajectory(mobject, trajectory, progress)


def follow_camera(frame, rig: CameraRig, primary: Trajectory, secondary: Trajectory, alpha: float, *, zoom: float, primary_profile=None, secondary_profile=None):
    primary_progress = primary_profile(alpha) if primary_profile else smoothstep(alpha)
    secondary_progress = secondary_profile(alpha) if secondary_profile else smoothstep(alpha)
    primary_point = primary.point_at_distance(primary_progress)
    secondary_point = secondary.point_at_distance(secondary_progress)
    midpoint = ((primary_point[0] + secondary_point[0]) / 2, (primary_point[1] + secondary_point[1]) / 2)
    parameter = primary.distance_to_parameter(primary_progress * primary.length)
    state = rig.follow(midpoint, primary.tangent(parameter), zoom=zoom)
    frame.set_width(9 / state.zoom).move_to((*state.center, 0))
    return frame


def _brake_marker(path: Trajectory, fraction: float, color: str):
    point = path.point_at_distance(fraction)
    tangent = path.tangent(path.distance_to_parameter(fraction * path.length))
    normal = (-tangent[1], tangent[0])
    return Line(
        (point[0] - normal[0] * 0.62, point[1] - normal[1] * 0.62, 0),
        (point[0] + normal[0] * 0.62, point[1] + normal[1] * 0.62, 0),
        color=color,
        stroke_width=7,
    )


class BrakingLaterExplainer(PortraitScene):
    """Timed, narration-ready F1 explainer with illustrative telemetry only."""

    def __init__(self, *args, theme: Theme = DEFAULT_THEME, **kwargs):
        super().__init__(*args, theme=theme, **kwargs)
        self.beats = BEATS

    def construct(self):
        theme = self.theme
        typography = TypographySystem(self.layout, theme, category="f1")
        for sequence in (
            (APPROACH_RED, RED_CORNER, RED_EXIT, RED_STRAIGHT),
            (APPROACH_CYAN, CYAN_CORNER, CYAN_EXIT, CYAN_STRAIGHT),
        ):
            for current, following in zip(sequence, sequence[1:]):
                current.validate_smooth_join(following, heading_tolerance=1e-3)
        # Preserve non-zero velocity across adjacent trajectory clips. Each
        # car can have a different illustrative strategy while the cyan car,
        # used as the camera lead, remains C1-continuous at every beat cut.
        red_profiles = {
            "approach": trajectory_speed_profile(APPROACH_RED, APPROACH_DURATION, start_speed=0.0, end_speed=0.75),
            "corner": trajectory_speed_profile(RED_CORNER, CORNER_DURATION, start_speed=0.75, end_speed=0.30),
            "exit": trajectory_speed_profile(RED_EXIT, EXIT_DURATION, start_speed=0.30, end_speed=0.22),
            "straight": trajectory_speed_profile(RED_STRAIGHT, STRAIGHT_DURATION, start_speed=0.22, end_speed=0.0),
        }
        cyan_profiles = {
            "approach": trajectory_speed_profile(APPROACH_CYAN, APPROACH_DURATION, start_speed=0.0, end_speed=0.75),
            "corner": trajectory_speed_profile(CYAN_CORNER, CORNER_DURATION, start_speed=0.75, end_speed=0.42),
            "exit": trajectory_speed_profile(CYAN_EXIT, EXIT_DURATION, start_speed=0.42, end_speed=0.34),
            "straight": trajectory_speed_profile(CYAN_STRAIGHT, STRAIGHT_DURATION, start_speed=0.34, end_speed=0.0),
        }
        # A single, readable 90-degree turn keeps the lesson spatially clear.
        track_paths = (TRACK_APPROACH, TRACK_CORNER, TRACK_EXIT)
        road_shadow = _path_mobject(track_paths, "#070B10", 172, extend=True)
        road = _path_mobject(track_paths, theme.track, 150, extend=True)
        road_lane = _path_mobject(track_paths, "#344150", 108, extend=True)
        border = _path_mobject(track_paths, theme.border, 4.5, extend=True)
        centerline = _path_mobject(track_paths, theme.secondary_text, 1.6, extend=True).set_stroke(opacity=0.34)
        racing_surface = _path_mobject(track_paths, theme.accent, 2.4, extend=True).set_stroke(opacity=0.22)
        grid = VGroup(*[Line((-3.0, y, 0), (7.0, y, 0), color=theme.border, stroke_width=1, stroke_opacity=0.13) for y in (-2.4, 0.0, 2.4)])
        apex = Dot((*CYAN_CORNER.point_at_distance(0.56), 0), color=theme.semantic.focus, radius=0.11)
        apex_ring = Circle(radius=0.24, color=theme.semantic.focus, stroke_width=2).move_to(apex)
        apex_callout = TechnicalCallout(
            typography.technical_label("APEX", size=15, color=theme.semantic.focus),
            anchor=apex.get_center()[:2],
            position=(1.95, -2.72),
            color=theme.semantic.focus,
            background=theme.background,
            elbow_points=((1.72, -1.08), (1.72, -2.32)),
        )
        entry_callout = TechnicalCallout(
            typography.technical_label("TURN-IN", size=14, color=theme.secondary_text),
            anchor=(-0.25, 1.55),
            position=(-2.12, 2.72),
            color=theme.secondary_text,
            background=theme.background,
            elbow_points=((-0.88, 1.55), (-1.24, 2.72)),
        )
        self.add_world(grid, road_shadow, road, road_lane, border, centerline, racing_surface, apex_ring, apex, apex_callout.mobject, entry_callout.mobject)

        red_car = self._car(theme.semantic.braking, "#7A211F", theme).scale(0.34)
        cyan_car = self._car(theme.semantic.acceleration, "#087A86", theme).scale(0.34)
        F1Car.place_on_trajectory(red_car, APPROACH_RED, 0.0)
        F1Car.place_on_trajectory(cyan_car, APPROACH_CYAN, 0.0)
        self.add_world(red_car, cyan_car)

        rig = CameraRig(look_ahead=0.55)
        start_midpoint = ((APPROACH_RED.point(0)[0] + APPROACH_CYAN.point(0)[0]) / 2, (APPROACH_RED.point(0)[1] + APPROACH_CYAN.point(0)[1]) / 2)
        start_state = rig.follow(start_midpoint, APPROACH_CYAN.tangent(0), zoom=1.45)
        self.camera.frame.set_width(9 / start_state.zoom).move_to((*start_state.center, 0))

        headline = self._headline(typography, ("BRAKE", "LATER.", "LOSE", "TIME?"), {"BRAKE": theme.semantic.braking, "TIME?": theme.semantic.focus}, 32)
        headline.move_to((*self.layout.point((0.5, 0.87)), 0))
        self.add_screen_ui(headline)

        # 0–3s: establish movement first, then push the camera into the corner.
        self.play(
            FadeIn(road_shadow, shift=UP * 0.12),
            FadeIn(road, shift=UP * 0.12),
            FadeIn(road_lane, shift=UP * 0.12),
            FadeIn(border),
            FadeIn(centerline),
            FadeIn(racing_surface),
            FadeIn(red_car, shift=RIGHT * 0.18),
            FadeIn(cyan_car, shift=RIGHT * 0.18),
            # The screen-space updater owns the final position while the camera
            # starts moving; a pure fade avoids updater/shift contention.
            FadeIn(headline),
            run_time=1.1,
        )
        self.play(
            UpdateFromAlphaFunc(red_car, lambda mob, alpha: follow_path(mob, APPROACH_RED, alpha, red_profiles["approach"]), rate_func=linear),
            UpdateFromAlphaFunc(cyan_car, lambda mob, alpha: follow_path(mob, APPROACH_CYAN, alpha, cyan_profiles["approach"]), rate_func=linear),
            UpdateFromAlphaFunc(self.camera.frame, lambda frame, alpha: follow_camera(frame, rig, APPROACH_CYAN, APPROACH_RED, alpha, zoom=1.45, primary_profile=cyan_profiles["approach"], secondary_profile=red_profiles["approach"]), rate_func=linear),
            run_time=APPROACH_DURATION,
        )

        # 3–8s: make the two braking choices explicit and keep both paths visible.
        compare = self._headline(typography, ("LATE BRAKE", "EARLY ROTATION"), {"LATE BRAKE": theme.semantic.braking, "EARLY ROTATION": theme.semantic.acceleration}, 28)
        compare.move_to((*self.layout.point((0.5, 0.86)), 0))
        legend = self._strategy_legend(typography, theme)
        legend.move_to((*self.layout.point((0.5, 0.77)), 0))
        self.add_screen_ui(compare)
        self.add_screen_ui(legend)
        red_line = _path_mobject((APPROACH_RED, RED_CORNER, RED_EXIT), theme.semantic.braking, 0.11)
        cyan_line = _path_mobject((APPROACH_CYAN, CYAN_CORNER, CYAN_EXIT), theme.semantic.acceleration, 0.11)
        red_history = trajectory_history((APPROACH_RED, RED_CORNER, RED_EXIT), theme.semantic.braking, width=1.2, opacity=0.55, dashes=92)
        cyan_history = trajectory_history((APPROACH_CYAN, CYAN_CORNER, CYAN_EXIT), theme.semantic.acceleration, width=1.2, opacity=0.55, dashes=92)
        red_brake = _brake_marker(RED_CORNER, 0.08, theme.semantic.braking)
        cyan_brake = _brake_marker(CYAN_CORNER, 0.02, theme.semantic.acceleration)
        red_brake_label = self._world_label(typography.technical_label("LATE BRAKE", size=14, color=theme.semantic.braking), red_brake, LEFT, buff=0.42)
        cyan_brake_label = self._world_label(typography.technical_label("EARLY BRAKE", size=14, color=theme.semantic.acceleration), cyan_brake, RIGHT, buff=0.42)
        self.add_world(red_history, cyan_history, red_line, cyan_line, red_brake, cyan_brake, red_brake_label, cyan_brake_label)
        # The entire five-second beat is one world/camera move. Screen and
        # annotation changes are layered over it, so editorial timing cannot
        # introduce a pause into vehicle or camera motion.
        self.play(
            UpdateFromAlphaFunc(red_car, lambda mob, alpha: follow_path(mob, RED_CORNER, alpha, red_profiles["corner"]), run_time=CORNER_DURATION, rate_func=linear),
            UpdateFromAlphaFunc(cyan_car, lambda mob, alpha: follow_path(mob, CYAN_CORNER, alpha, cyan_profiles["corner"]), run_time=CORNER_DURATION, rate_func=linear),
            UpdateFromAlphaFunc(self.camera.frame, lambda frame, alpha: follow_camera(frame, rig, CYAN_CORNER, RED_CORNER, alpha, zoom=1.45, primary_profile=cyan_profiles["corner"], secondary_profile=red_profiles["corner"]), run_time=CORNER_DURATION, rate_func=linear),
            Succession(
                AnimationGroup(
                    self.screen_fade_out(headline), self.screen_fade_in(compare), self.screen_fade_in(legend),
                    FadeIn(red_history), FadeIn(cyan_history), Create(red_line), Create(cyan_line),
                    lag_ratio=0, run_time=0.9,
                ),
                AnimationGroup(
                    FadeIn(red_brake_label), FadeIn(cyan_brake_label), Create(red_brake), Create(cyan_brake),
                    lag_ratio=0, run_time=0.75,
                ),
                Wait(3.35),
            ),
        )

        # 8–15s: entry speed versus rotation and throttle timing.
        detail = typography.technical_label("ENTRY SPEED IS NOT LAP TIME", size=16, color=theme.secondary_text).move_to((*self.layout.point((0.5, 0.78)), 0))
        red_panel = self._telemetry_panel(typography, "RED / ENTRY", "182 KM/H", theme.semantic.braking, (0.27, 0.27))
        cyan_panel = self._telemetry_panel(typography, "CYAN / EXIT", "164 KM/H", theme.semantic.acceleration, (0.73, 0.27))
        red_throttle = self._bar("THROTTLE DELAY", 0.28, theme.semantic.braking, (0.5, 0.17))
        cyan_throttle = self._bar("THROTTLE EARLIER", 0.82, theme.semantic.acceleration, (0.5, 0.10))
        self.add_screen_ui(detail, red_panel, cyan_panel, red_throttle, cyan_throttle)
        # Keep the camera rolling for the full seven-second technical beat.
        self.play(
            UpdateFromAlphaFunc(red_car, lambda mob, alpha: follow_path(mob, RED_EXIT, alpha, red_profiles["exit"]), run_time=EXIT_DURATION, rate_func=linear),
            UpdateFromAlphaFunc(cyan_car, lambda mob, alpha: follow_path(mob, CYAN_EXIT, alpha, cyan_profiles["exit"]), run_time=EXIT_DURATION, rate_func=linear),
            UpdateFromAlphaFunc(self.camera.frame, lambda frame, alpha: follow_camera(frame, rig, CYAN_EXIT, RED_EXIT, alpha, zoom=1.45, primary_profile=cyan_profiles["exit"], secondary_profile=red_profiles["exit"]), run_time=EXIT_DURATION, rate_func=linear),
            Succession(
                AnimationGroup(
                    self.screen_fade_out(compare), self.screen_fade_out(legend),
                    self.screen_fade_in(detail), self.screen_fade_in(red_panel), self.screen_fade_in(cyan_panel),
                    self.screen_fade_in(red_throttle), self.screen_fade_in(cyan_throttle),
                    lag_ratio=0, run_time=0.85,
                ),
                Wait(6.15),
            ),
        )

        # 15–20s: the cyan car exits ahead and the headline resolves the lesson.
        exit_headline = self._headline(typography, ("EXIT", "SPEED", "WINS"), {"EXIT": theme.semantic.acceleration, "WINS": theme.semantic.positive_delta}, 34)
        exit_headline = self._screen_plate(exit_headline, theme.background).move_to((*self.layout.point((0.5, 0.87)), 0))
        delta = typography.telemetry_label("EXIT GAP", "+0.31 s", color=theme.semantic.positive_delta, size=23).move_to((*self.layout.point((0.5, 0.08)), 0))
        self.add_screen_ui(exit_headline, delta)
        # The exit beat is a moving match cut: maintain the vehicle and camera
        # vector while telemetry gives way to the result. This avoids the
        # perceptual "stop, swap, go" jitter at 15 seconds.
        self.play(
            UpdateFromAlphaFunc(red_car, lambda mob, alpha: follow_path(mob, RED_STRAIGHT, alpha, red_profiles["straight"]), run_time=STRAIGHT_DURATION, rate_func=linear),
            UpdateFromAlphaFunc(cyan_car, lambda mob, alpha: follow_path(mob, CYAN_STRAIGHT, alpha, cyan_profiles["straight"]), run_time=STRAIGHT_DURATION, rate_func=linear),
            UpdateFromAlphaFunc(self.camera.frame, lambda frame, alpha: follow_camera(frame, rig, CYAN_STRAIGHT, RED_STRAIGHT, alpha, zoom=1.45, primary_profile=cyan_profiles["straight"], secondary_profile=red_profiles["straight"]), run_time=STRAIGHT_DURATION, rate_func=linear),
            Succession(
                AnimationGroup(
                    FadeOut(detail), FadeOut(red_panel), FadeOut(cyan_panel), FadeOut(red_throttle), FadeOut(cyan_throttle),
                    FadeOut(red_brake_label), FadeOut(cyan_brake_label), FadeOut(red_brake), FadeOut(cyan_brake), FadeOut(entry_callout.mobject),
                    self.screen_fade_in(exit_headline), self.screen_fade_in(delta),
                    lag_ratio=0, run_time=0.75,
                ),
                Wait(4.25),
            ),
        )

        # 20–24.6s: freeze the geometry and make the causal distinction the focal point.
        final_headline = self._headline(typography, ("ENTRY SPEED", "≠", "FASTEST LAP"), {"≠": theme.semantic.focus, "FASTEST LAP": theme.text}, 30)
        final_headline.move_to((*self.layout.point((0.5, 0.70)), 0))
        final_note = self._screen_plate(typography.technical_label("RACING-LINE COMPARISON", size=14), theme.background).move_to((*self.layout.point((0.5, 0.64)), 0))
        self.add_screen_ui(final_headline, final_note)
        self.play(
            self.screen_fade_out(exit_headline), self.screen_fade_out(delta), self.screen_fade_in(final_headline), self.screen_fade_in(final_note),
            run_time=0.85,
        )
        self.play(Indicate(cyan_line, color=theme.semantic.acceleration, scale_factor=1.04), Indicate(red_line, color=theme.semantic.braking, scale_factor=1.02), run_time=0.7)
        self.wait(2.95)

    @staticmethod
    def _car(primary: str, secondary: str, theme: Theme):
        model = F1CarModel(style=VehicleStyle(primary=primary, secondary=secondary))
        car = F1Car(model=model, theme=theme).mobject
        return car

    @staticmethod
    def _screen_plate(content, color: str):
        plate = BackgroundRectangle(content, fill_color=color, fill_opacity=0.94, buff=0.18, stroke_width=0)
        return VGroup(plate, content)

    @staticmethod
    def _strategy_legend(system: TypographySystem, theme: Theme):
        red_dot = Dot(radius=0.06, color=theme.semantic.braking)
        cyan_dot = Dot(radius=0.06, color=theme.semantic.acceleration)
        red_text = system.technical_label("RED  /  LATE BRAKE", size=11, color=theme.semantic.braking)
        cyan_text = system.technical_label("CYAN  /  EARLY BRAKE", size=11, color=theme.semantic.acceleration)
        return VGroup(VGroup(red_dot, red_text).arrange(RIGHT, buff=0.10), VGroup(cyan_dot, cyan_text).arrange(RIGHT, buff=0.10)).arrange(RIGHT, buff=0.35)

    @staticmethod
    def _world_label(label, anchor, direction, *, buff: float):
        """Keep an annotation legible without attaching it to a moving car."""
        plate = BackgroundRectangle(label, fill_color="#10151C", fill_opacity=0.92, buff=0.09, stroke_width=0)
        return VGroup(plate, label).next_to(anchor, direction, buff=buff)

    @staticmethod
    def _headline(system: TypographySystem, words: tuple[str, ...], highlights: dict[str, str], size: float):
        # The scene UI is camera-invariant. Keep a deliberate mobile margin
        # rather than letting a camera push-in turn this into edge-to-edge type.
        return system.composed_headline(words, highlights=highlights, size=size).arrange(RIGHT, buff=0.12).set_max_width(6.5)

    def _telemetry_panel(self, system: TypographySystem, label: str, value: str, color: str, normalized_position: tuple[float, float]):
        panel = RoundedRectangle(width=2.30, height=0.66, corner_radius=0.08, fill_color=self.theme.surface, fill_opacity=0.96, stroke_color=color, stroke_width=1.5)
        text = system.telemetry_label(label, value, color=color, size=17).move_to(panel)
        return VGroup(panel, text).move_to((*self.layout.point(normalized_position), 0))

    def _bar(self, label: str, fraction: float, color: str, normalized_position: tuple[float, float]):
        panel = RoundedRectangle(width=5.10, height=0.46, corner_radius=0.06, fill_color=self.theme.surface, fill_opacity=0.95, stroke_width=0)
        fill = Rectangle(width=4.20 * fraction, height=0.11, fill_color=color, fill_opacity=1, stroke_width=0).align_to(panel, LEFT).shift(RIGHT * 0.34 + DOWN * 0.09)
        text = Text(label.upper(), font="IBM Plex Mono", weight="MEDIUM", font_size=9, color=self.theme.secondary_text).align_to(panel, LEFT).shift(RIGHT * 0.30 + UP * 0.11)
        return VGroup(panel, fill, text).move_to((*self.layout.point(normalized_position), 0))


if __name__ == "__main__":
    BrakingLaterExplainer().render()
