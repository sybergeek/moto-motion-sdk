"""Why the fastest racing line is not always the shortest (portrait, ~20 sec)."""

from manim import *  # noqa: F403

from moto_motion.core.constants import BACKGROUND, CYAN, GOLD, GREEN, RED, TEXT, TRACK
from moto_motion.effects import VehicleMotion
from moto_motion.geometry import Trajectory
from moto_motion.renderers.manim.vehicles import F1Car
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.typography import TypographySystem


SHORT = Trajectory(((-4.2, 2.0), (-2.0, 2.6), (1.2, 1.8), (3.8, 0.2)))
FAST = Trajectory(((-4.2, 1.3), (-2.6, 0.0), (0.8, -1.8), (3.8, 0.2)))


class RacingLineExplainer(PortraitScene):
    def construct(self):
        self.camera.background_color = BACKGROUND
        type_system = TypographySystem(self.layout)
        headline_reveal, title = type_system.animated("THE RACING LINE", "directional_entrance", "up", 0.7)
        title.move_to((*self.layout.point((0.5, 0.88)), 0))
        subtitle = type_system.manim_text("Shortest ≠ Fastest", type_system.body_style(25)).set_color(GOLD).move_to((*self.layout.point((0.5, 0.78)), 0))
        self.add_screen_ui(title, subtitle)
        self.play(headline_reveal, FadeIn(subtitle, shift=UP * 0.12), run_time=1)

        road = VMobject().set_points_smoothly([(*p, 0) for p in FAST.sample(80)]).set_stroke(TRACK, 1.25)
        short_line = VMobject().set_points_smoothly([(*p, 0) for p in SHORT.sample(80)]).set_stroke(RED, 0.08)
        fast_line = VMobject().set_points_smoothly([(*p, 0) for p in FAST.sample(80)]).set_stroke(CYAN, 0.1)
        apex = Dot((*FAST.point_at_distance(0.57), 0), color=GOLD, radius=0.12)
        labels = VGroup(Text("SHORTER", color=RED, font_size=22), Text("EXIT SPEED", color=CYAN, font_size=22)).arrange(DOWN, aligned_edge=LEFT).to_corner(UL, buff=0.5).shift(DOWN * 1.1)
        self.add_world(road)
        self.play(Create(road), run_time=1.3)
        self.play(Create(short_line), FadeIn(labels[0]), run_time=1.2)
        self.play(Create(fast_line), FadeIn(labels[1]), FadeIn(apex), run_time=1.4)

        car_a = F1Car().mobject.scale(0.42).set_color(RED).move_to((*SHORT.point(0), 0))
        car_b = F1Car().mobject.scale(0.42).set_color(CYAN).move_to((*FAST.point(0), 0))
        self.add_world(car_a, car_b)
        self.play(
            MoveAlongPath(car_a, short_line, rate_func=linear),
            MoveAlongPath(car_b, fast_line, rate_func=linear),
            run_time=8,
        )
        exit_note = Text("A wider entry preserves speed on exit", color=GREEN, font_size=25).to_edge(DOWN, buff=1.1)
        self.play(FadeIn(exit_note), run_time=1)
        conclusion = Text("Shortest distance ≠ Fastest lap", color=TEXT, font_size=38).move_to(ORIGIN)
        self.play(FadeOut(labels), FadeOut(exit_note), Transform(subtitle, conclusion), run_time=1.5)
        self.wait(2)


if __name__ == "__main__":
    RacingLineExplainer().render()
