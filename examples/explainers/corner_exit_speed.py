"""20-second portrait explainer: Why Corner Exit Speed Wins Races."""

from math import pi

from manim import *  # noqa: F403

from moto_motion.camera import CameraRig
from moto_motion.choreography import SceneDirector
from moto_motion.core.constants import BACKGROUND, CYAN, GOLD, GREEN, RED, TEXT, TRACK
from moto_motion.effects import smoothstep
from moto_motion.geometry import Trajectory
from moto_motion.renderers.manim.circuit import Circuit
from moto_motion.renderers.manim.vehicles import F1Car
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.transitions import TransitionDirector
from moto_motion.typography import NumericCounter, TypographySystem


APPROACH = Trajectory(((-4.2, 3.4), (-3.3, 3.0), (-2.0, 1.9), (-0.8, 0.2)))
TIGHT_EXIT = Trajectory(((-0.8, 0.2), (-0.2, -0.8), (1.6, -1.1), (4.0, -0.4)))
WIDE_EXIT = Trajectory(((-0.8, 0.2), (-0.4, -1.4), (2.0, -1.8), (4.0, -0.4)))


def follow_path(mobject, trajectory, alpha):
    progress = smoothstep(alpha)
    point = trajectory.point_at_distance(progress)
    heading = trajectory.heading(trajectory.distance_to_parameter(progress * trajectory.length)) - pi / 2
    previous = getattr(mobject, "_moto_heading", 0.0)
    mobject.rotate(heading - previous).move_to((*point, 0))
    mobject._moto_heading = heading
    return mobject


class CornerExitSpeed(PortraitScene):
    def construct(self):
        self.camera.background_color = BACKGROUND
        type_system = TypographySystem(self.layout)
        transitions = TransitionDirector()
        director = SceneDirector()
        director.preset("approach_corner", 1.0, 4.5)
        director.preset("enter_corner", 5.5, 4.5)
        director.preset("exit_corner", 12.0, 5.0)
        director.preset("reveal_technical_detail", 7.0, 2.0)
        director.validate()

        headline_top = type_system.composed_headline(["WHY", "CORNER", "EXIT", "SPEED"], highlights={"EXIT": GOLD, "SPEED": CYAN}, size=31)
        headline_bottom = type_system.composed_headline(["WINS", "RACES"], highlights={"WINS": GOLD}, size=34)
        headline = VGroup(headline_top, headline_bottom).arrange(DOWN, buff=0.08).move_to((*self.layout.point((0.5, 0.86)), 0))
        self.add_screen_ui(headline)
        self.play(type_system.word_reveal(VGroup(*headline_top, *headline_bottom), direction="up", duration=0.9))

        circuit = Circuit(WIDE_EXIT, width=1.35, kerb_spacing=10, braking_zone=(0.12, 0.3)).mobjects()
        self.add_world(circuit)
        self.play(Create(circuit), run_time=1.1)

        car = F1Car().mobject.scale(0.38).set_color(CYAN)
        car.move_to((*APPROACH.point(0), 0))
        self.add_world(car)
        camera_rig = CameraRig(look_ahead=0.75)
        camera_target = camera_rig.follow(APPROACH.point(0.55), APPROACH.tangent(0.55), zoom=1.08)
        self.play(
            UpdateFromAlphaFunc(car, lambda mob, alpha: follow_path(mob, APPROACH, alpha)),
            self.camera.frame.animate.move_to((*camera_target.center, 0)).scale(1 / camera_target.zoom),
            run_time=4.2,
        )

        braking = Line((*APPROACH.point_at_distance(0.66), 0), (*APPROACH.point_at_distance(0.78), 0), color=RED, stroke_width=9)
        braking_label = type_system.manim_text("BRAKING ZONE", type_system.body_style(22)).set_color(RED).next_to(braking, LEFT, buff=0.18)
        apex = Dot((*WIDE_EXIT.point_at_distance(0.45), 0), color=GOLD, radius=0.12)
        apex_ring = Circle(radius=0.23, color=GOLD, stroke_width=3).move_to(apex)
        apex_label = type_system.manim_text("APEX", type_system.body_style(22)).set_color(GOLD).next_to(apex, DOWN, buff=0.12)
        exit_arrow = Arrow((*WIDE_EXIT.point_at_distance(0.74), 0), (*WIDE_EXIT.point_at_distance(0.88), 0), color=GREEN, stroke_width=6, buff=0.05)
        exit_label = type_system.manim_text("EXIT / MOMENTUM", type_system.body_style(20)).set_color(GREEN).next_to(exit_arrow, DOWN, buff=0.1)
        self.add_world(braking, braking_label, apex, apex_ring, apex_label, exit_arrow, exit_label)
        self.play(Create(braking), FadeIn(braking_label, shift=RIGHT * 0.2), run_time=0.8)
        self.play(Create(apex), Create(apex_ring), FadeIn(apex_label, shift=UP * 0.15), Create(exit_arrow), FadeIn(exit_label, shift=UP * 0.12), run_time=0.7)

        tight = F1Car().mobject.scale(0.31).set_color(RED).move_to((*TIGHT_EXIT.point(0), 0))
        wide = F1Car().mobject.scale(0.31).set_color(CYAN).move_to((*WIDE_EXIT.point(0), 0))
        tight_label = type_system.manim_text("SHORTER LINE", type_system.body_style(20)).set_color(RED).to_edge(LEFT, buff=0.55).shift(DOWN * 0.8)
        wide_label = type_system.manim_text("BETTER EXIT", type_system.body_style(20)).set_color(CYAN).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.8)
        self.add_world(tight, wide)
        self.add_screen_ui(tight_label, wide_label)
        self.play(FadeIn(tight), FadeIn(wide), FadeIn(tight_label), FadeIn(wide_label), run_time=0.7)
        self.play(
            UpdateFromAlphaFunc(tight, lambda mob, alpha: follow_path(mob, TIGHT_EXIT, alpha)),
            UpdateFromAlphaFunc(wide, lambda mob, alpha: follow_path(mob, WIDE_EXIT, alpha)),
            run_time=4.2,
        )

        counter = NumericCounter(118, 164)
        telemetry = type_system.telemetry_label("Illustrative exit speed", counter.value_at(1), color=GREEN, size=25).to_edge(DOWN, buff=0.68)
        self.add_screen_ui(telemetry)
        self.play(FadeIn(telemetry, shift=UP * 0.2), run_time=0.5)
        self.wait(1.2)

        close = type_system.headline("THE EXIT MATTERS MORE.").set_color(TEXT).move_to((*self.layout.point((0.5, 0.54)), 0))
        self.play(transitions.manim_animation(transitions.camera_push(0.8), VGroup(tight, wide)), run_time=0.8)
        self.play(FadeOut(headline), FadeOut(telemetry), FadeOut(tight_label), FadeOut(wide_label), FadeIn(close, shift=UP * 0.25), run_time=1.0)
        self.wait(1.0)


if __name__ == "__main__":
    CornerExitSpeed().render()
