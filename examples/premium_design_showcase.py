"""Premium 12–15 second motorsport technical-explainer showcase."""

from math import pi

from manim import *  # noqa: F403

from moto_motion.core.themes import MIDNIGHT_TECHNICAL
from moto_motion.effects import smoothstep
from moto_motion.geometry import Trajectory
from moto_motion.icons import IconState, MotorsportIcon
from moto_motion.renderers.manim.vehicles import F1Car
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.transitions import TransitionDirector
from moto_motion.typography import AnimatedCaption, KineticHeadline, NumericDelta, TelemetryCounter, TypographySystem


ENTRY = Trajectory(((-3.8, 2.6), (-2.2, 2.2), (-0.9, 0.5), (-0.1, -0.7)))
EARLY_BRAKE = Trajectory(((-0.1, -0.7), (0.6, -1.4), (2.0, -1.0), (3.6, 0.3)))
LATE_BRAKE = Trajectory(((-0.1, -0.7), (0.2, -1.8), (2.1, -1.75), (3.8, 0.3)))


def follow_vehicle(mobject, trajectory: Trajectory, alpha: float):
    progress = smoothstep(alpha)
    point = trajectory.point_at_distance(progress)
    parameter = trajectory.distance_to_parameter(progress * trajectory.length)
    heading = trajectory.heading(parameter) - pi / 2
    previous = getattr(mobject, "_premium_heading", 0.0)
    mobject.rotate(heading - previous).move_to((*point, 0))
    mobject._premium_heading = heading


class PremiumMotorsportShowcase(PortraitScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, theme=MIDNIGHT_TECHNICAL, **kwargs)

    def construct(self):
        theme = self.theme
        system = TypographySystem(self.layout, theme)
        transitions = TransitionDirector()

        grid = VGroup(*(Line((-4.5, y, 0), (4.5, y, 0), color=theme.border, stroke_width=1, stroke_opacity=0.22) for y in (-5, -3, -1, 1, 3, 5)))
        speed_lines = VGroup(*(Line((-4.2, y, 0), (-1.2, y + 0.32, 0), color=theme.accent, stroke_width=2, stroke_opacity=0.24) for y in (-1.0, -0.45, 0.1, 0.65, 1.2)))
        car = F1Car(theme=theme).mobject.scale(1.15).move_to((0, 0.4, 0))
        technical_ring = Circle(radius=2.35, color=theme.border, stroke_width=2).move_to(car)
        self.add_world(grid, speed_lines, technical_ring, car)
        self.play(FadeIn(grid), Create(technical_ring), run_time=0.7)
        self.play(transitions.manim_animation(transitions.speed_line_reveal((1, 0), 0.55), speed_lines), Create(car), run_time=1.1)

        headline = KineticHeadline("BRAKE LATER. LOSE TIME.", highlights={"BRAKE": theme.semantic.braking, "TIME.": theme.semantic.focus}, size=38, system=system).mobject()
        headline.move_to((*self.layout.point((0.5, 0.86)), 0))
        self.add_screen_ui(headline)
        self.play(KineticHeadline("BRAKE LATER. LOSE TIME.", system=system).reveal(headline, duration=0.9))

        brake_icon = MotorsportIcon("brake_disc", theme=theme, state=IconState(1.0, True)).mobject.scale(0.38).move_to((-2.9, -4.65, 0))
        brake_bar_bg = RoundedRectangle(width=3.5, height=0.34, corner_radius=0.12, fill_color=theme.surface, fill_opacity=1, stroke_width=0).move_to((-0.55, -4.65, 0))
        brake_bar = Rectangle(width=0.2, height=0.18, fill_color=theme.semantic.braking, fill_opacity=1, stroke_width=0).align_to(brake_bar_bg, LEFT).shift(RIGHT * 0.14)
        brake_label = system.manim_text("BRAKE PRESSURE / ILLUSTRATIVE", system.telemetry_style(16)).next_to(brake_bar_bg, UP, aligned_edge=LEFT, buff=0.12)
        brake_group = VGroup(brake_icon, brake_bar_bg, brake_bar, brake_label)
        self.add_screen_ui(brake_group)
        self.play(FadeIn(brake_group, shift=RIGHT * 0.2), brake_bar.animate.stretch_to_fit_width(3.2).align_to(brake_bar_bg, LEFT).shift(RIGHT * 0.14), run_time=1.0)

        self.play(FadeOut(speed_lines), car.animate.scale(0.45).move_to((*ENTRY.point(0), 0)), self.camera.frame.animate.scale(0.9).move_to((-0.3, 0.0, 0)), run_time=0.8)
        road = VMobject().set_points_smoothly([(*p, 0) for p in LATE_BRAKE.sample(100)]).set_stroke(theme.track, 1.25)
        early = VMobject().set_points_smoothly([(*p, 0) for p in EARLY_BRAKE.sample(90)]).set_stroke(theme.semantic.braking, 0.07)
        late = VMobject().set_points_smoothly([(*p, 0) for p in LATE_BRAKE.sample(90)]).set_stroke(theme.accent, 0.09)
        apex = Dot((*LATE_BRAKE.point_at_distance(0.43), 0), color=theme.semantic.focus, radius=0.13)
        self.add_world(road, early, late, apex)
        self.play(Create(road), Create(early), Create(late), FadeIn(apex), run_time=1.1)

        comparison = VGroup(
            system.telemetry_label("EARLY BRAKE", "148 KM/H", color=theme.semantic.braking, size=23),
            system.telemetry_label("LATE BRAKE", "164 KM/H", color=theme.accent, size=23),
        ).arrange(RIGHT, buff=1.1).to_edge(DOWN, buff=0.55)
        delta = NumericDelta(-0.31).mobject(system=system).next_to(comparison, UP, buff=0.28)
        comparison_group = VGroup(comparison, delta)
        self.add_screen_ui(comparison_group)
        self.play(transitions.manim_animation(transitions.telemetry_panel_slide((1, 0), 0.55), comparison_group))
        self.play(UpdateFromAlphaFunc(car, lambda mob, alpha: follow_vehicle(mob, LATE_BRAKE, alpha)), run_time=2.5, rate_func=linear)

        caption, caption_in = AnimatedCaption("Exit speed compounds down the following straight.", system=system).build()
        self.add_screen_ui(caption)
        self.play(caption_in, self.camera.frame.animate.scale(1.08).move_to((*LATE_BRAKE.point_at_distance(0.82), 0)), run_time=0.75)
        exit_arrow = Arrow((*LATE_BRAKE.point_at_distance(0.74), 0), (*LATE_BRAKE.point_at_distance(0.98), 0), color=theme.semantic.positive_delta, stroke_width=8, buff=0.02)
        self.add_world(exit_arrow)
        self.play(GrowArrow(exit_arrow), run_time=0.6)

        payoff = KineticHeadline("THE EXIT PAYS.", highlights={"EXIT": theme.accent, "PAYS.": theme.semantic.focus}, size=48, system=system).mobject().move_to((*self.layout.point((0.5, 0.58)), 0))
        payoff_streaks = VGroup(
            Line((-2.5, -1.0, 0), (1.3, -1.0, 0), color=theme.accent, stroke_width=2, stroke_opacity=0.35),
            Line((-1.9, -1.25, 0), (1.8, -1.25, 0), color=theme.accent, stroke_width=2, stroke_opacity=0.2),
            Arrow((0.8, -1.55, 0), (2.5, -1.55, 0), color=theme.semantic.positive_delta, stroke_width=7, buff=0),
        )
        self.add_screen_ui(payoff, payoff_streaks)
        self.play(FadeOut(headline), FadeOut(brake_group), FadeOut(comparison_group), FadeOut(caption), FadeOut(road), FadeOut(early), FadeOut(late), FadeOut(apex), FadeOut(exit_arrow), FadeOut(car), FadeOut(grid), FadeOut(technical_ring), KineticHeadline("THE EXIT PAYS.", system=system).reveal(payoff, duration=0.8), LaggedStart(*(Create(line) for line in payoff_streaks), lag_ratio=0.12), run_time=0.9)
        self.wait(1.3)


if __name__ == "__main__":
    PremiumMotorsportShowcase().render()
