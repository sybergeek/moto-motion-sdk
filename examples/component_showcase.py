"""Small visual lab for each reusable Motorsport Motion component.

Render individual classes while tuning one module at a time, for example:
`manim -pql examples/component_showcase.py TypographyComponentShowcase`.
"""

from manim import *  # noqa: F403

from moto_motion.camera import CameraRig
from moto_motion.choreography import SceneDirector
from moto_motion.core.constants import BACKGROUND, CYAN, GOLD, GREEN, RED, TEXT, TRACK
from moto_motion.core.layout import SafeAreaLayout
from moto_motion.effects import VehicleMotion
from moto_motion.environment import Environment, Layer
from moto_motion.geometry import Trajectory
from moto_motion.renderers.manim.circuit import Circuit
from moto_motion.renderers.manim.motogp import MotoGPBike
from moto_motion.renderers.manim.vehicles import F1Car
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.transitions import TransitionDirector
from moto_motion.typography import NumericCounter, TypographySystem


SHOWCASE_PATH = Trajectory(((-3.8, 3.0), (-2.0, 2.8), (0.2, 0.5), (3.5, -1.2)))


class ShowcaseBase(PortraitScene):
    def label(self, value: str):
        mob = Text(value.upper(), font="DejaVu Sans Condensed", weight="BOLD", font_size=27, color=TEXT)
        mob.move_to((*self.layout.point((0.5, 0.9)), 0))
        self.add_screen_ui(mob)
        return mob


class LayoutComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("SafeAreaLayout / screen coordinates")
        safe = Rectangle(width=self.layout.safe.width, height=self.layout.safe.height, color=GREEN, stroke_width=3).move_to((0, 0, 0))
        corner = Dot((*self.layout.point((0.08, 0.12)), 0), color=GOLD)
        center = Dot((*self.layout.point((0.5, 0.5)), 0), color=CYAN)
        legend = Text("UI stays fixed while the world camera moves", font_size=22, color=TEXT).move_to((0, -5.8, 0))
        self.add_screen_ui(legend)
        self.add_world(safe, corner, center)
        self.play(Create(safe), FadeIn(corner), FadeIn(center), run_time=0.8)
        self.wait(1)


class TrajectoryComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("Trajectory / arc-length sampling + tangent")
        path = VMobject().set_points_smoothly([(*p, 0) for p in SHOWCASE_PATH.sample(100)]).set_stroke(CYAN, 0.09)
        dots = VGroup(*(Dot((*p, 0), radius=0.045, color=GOLD) for p in SHOWCASE_PATH.sample(16)))
        point = SHOWCASE_PATH.point_at_distance(0.5)
        tangent = SHOWCASE_PATH.tangent(SHOWCASE_PATH.distance_to_parameter(0.5 * SHOWCASE_PATH.length))
        arrow = Arrow((*point, 0), (point[0] + tangent[0] * 0.8, point[1] + tangent[1] * 0.8, 0), color=GREEN, buff=0)
        annotation = Text("constant-speed samples", font_size=20, color=GOLD).move_to((0, -5.8, 0))
        self.add_screen_ui(annotation)
        self.add_world(path, dots, arrow)
        self.play(Create(path), FadeIn(dots), GrowArrow(arrow), run_time=1)
        self.wait(1)


class CircuitComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("Circuit / boundaries, kerbs, braking, apex, racing line")
        circuit = Circuit(SHOWCASE_PATH, width=1.35, kerb_spacing=8, braking_zone=(0.18, 0.34)).mobjects()
        legend = VGroup(Text("TRACK", font_size=19, color=TRACK), Text("RACING LINE", font_size=19, color=CYAN), Text("BRAKING / KERB", font_size=19, color=RED), Text("APEX", font_size=19, color=GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).to_edge(DOWN, buff=0.7)
        self.add_screen_ui(legend)
        self.add_world(circuit)
        self.play(Create(circuit), run_time=1.2)
        self.wait(1)


class VehicleComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("Vehicles / F1 + MotoGP share motion APIs")
        f1 = F1Car().mobject.scale(0.34).set_color(CYAN).move_to((-1.7, 0, 0))
        bike = MotoGPBike().mobject.scale(0.72).move_to((1.7, 0, 0))
        labels = VGroup(Text("F1", font_size=24, color=CYAN), Text("MotoGP", font_size=24, color=GOLD)).arrange(RIGHT, buff=2.5).move_to((0, -3.5, 0))
        self.add_world(f1, bike)
        self.add_screen_ui(labels)
        self.play(FadeIn(f1, shift=UP * 0.25), FadeIn(bike, shift=UP * 0.25), FadeIn(labels), run_time=0.9)
        self.wait(1)


class MotionComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("VehicleMotion / easing + path-following heading")
        path = VMobject().set_points_smoothly([(*p, 0) for p in SHOWCASE_PATH.sample(100)]).set_stroke(TRACK, 1.2)
        line = VMobject().set_points_smoothly([(*p, 0) for p in SHOWCASE_PATH.sample(100)]).set_stroke(CYAN, 0.08)
        car = F1Car().mobject.scale(0.3).set_color(CYAN).move_to((*SHOWCASE_PATH.point(0), 0))
        motion = VehicleMotion(SHOWCASE_PATH, duration=3.0)
        self.add_world(path, line, car)
        self.add_screen_ui(Text("smoothstep / constant-speed lookup", font_size=21, color=TEXT).move_to((0, -5.8, 0)))
        def update(mob, alpha):
            position, heading = motion.state_at(alpha * motion.duration)
            previous = getattr(mob, "_showcase_heading", 0.0)
            mob.rotate(heading - 1.5708 - previous).move_to((*position, 0))
            mob._showcase_heading = heading - 1.5708
        self.play(Create(path), Create(line), UpdateFromAlphaFunc(car, update), run_time=3)
        self.wait(0.5)


class CameraComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("CameraRig / follow + look-ahead + fixed UI")
        rig = CameraRig(look_ahead=0.8)
        target = SHOWCASE_PATH.point(0.65)
        state = rig.follow(target, SHOWCASE_PATH.tangent(0.65), zoom=1.1)
        road = VMobject().set_points_smoothly([(*p, 0) for p in SHOWCASE_PATH.sample(100)]).set_stroke(TRACK, 1.2)
        car = Dot((*target, 0), color=CYAN, radius=0.16)
        note = Text("screen label remains stable", font_size=22, color=GREEN).move_to((0, -5.8, 0))
        self.add_world(road, car)
        self.add_screen_ui(note)
        self.play(Create(road), FadeIn(car), run_time=0.7)
        self.play(self.camera.frame.animate.move_to((*state.center, 0)).scale(1 / state.zoom), run_time=1.2)
        self.wait(0.8)


class TypographyComponentShowcase(ShowcaseBase):
    def construct(self):
        system = TypographySystem(self.layout)
        title = system.composed_headline(["EXIT", "SPEED", "WINS"], highlights={"EXIT": GOLD, "WINS": CYAN}, size=48).move_to((*self.layout.point((0.5, 0.68)), 0))
        detail = system.telemetry_label("illustrative delta", "+0.42 s", color=GREEN, size=30).move_to((*self.layout.point((0.5, 0.43)), 0))
        count = Text(NumericCounter(118, 164).value_at(1), font="DejaVu Sans Condensed", weight="BOLD", font_size=42, color=CYAN).move_to((*self.layout.point((0.5, 0.28)), 0))
        self.add_screen_ui(title, detail, count)
        self.play(system.word_reveal(title, duration=0.9), FadeIn(detail, shift=UP * 0.15), FadeIn(count, shift=UP * 0.15), run_time=1.2)
        self.wait(1)


class TransitionComponentShowcase(ShowcaseBase):
    def construct(self):
        director = TransitionDirector()
        source = Square(side_length=1.3, color=RED, fill_opacity=1).move_to((-1.6, 0, 0))
        target = Circle(radius=0.7, color=GOLD, fill_opacity=1).move_to((1.6, 0, 0))
        note = Text("object-driven reveal → match cut", font_size=22, color=TEXT).move_to((0, -5.8, 0))
        self.add_world(source, target)
        self.add_screen_ui(note)
        self.play(director.manim_animation(director.object_reveal((1, 0), 0.6), source))
        self.play(director.manim_animation(director.match_cut("object_heading", 0.4, (1, 0)), target))
        self.play(Transform(source, target), run_time=0.8)
        self.wait(0.6)


class EnvironmentComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("Environment / explicit z-order")
        env = Environment(track=SHOWCASE_PATH, racing_lines=[SHOWCASE_PATH], vehicles=["vehicle"], apex_markers=[SHOWCASE_PATH.point_at_distance(0.5)])
        order = VGroup(*[Text(f"{layer.name}: {len([item for item_layer, item in env.ordered() if item_layer == layer])}", font_size=24, color=CYAN if layer == Layer.RACING_LINE else TEXT) for layer in Layer]).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to((0, 0, 0))
        note = Text("world layers stay ordered; UI is separate", font_size=22, color=GREEN).move_to((0, -5.8, 0))
        self.add_screen_ui(order, note)
        self.play(LaggedStart(*(FadeIn(item, shift=RIGHT * 0.2) for item in order), lag_ratio=0.12), run_time=1)
        self.wait(1)


class ChoreographyComponentShowcase(ShowcaseBase):
    def construct(self):
        self.label("SceneDirector / deterministic overlapping timeline")
        director = SceneDirector()
        director.preset("approach_corner", 0, 3)
        director.preset("reveal_technical_detail", 2, 2)
        director.preset("exit_corner", 3.5, 3)
        colors = [CYAN, GOLD, GREEN]
        bars = VGroup()
        for index, event in enumerate(director.events):
            bar = Rectangle(width=event.duration * 0.9, height=0.42, fill_opacity=1, fill_color=colors[index], stroke_width=0).move_to((-3.2 + event.start * 0.9 + event.duration * 0.45, 1.1 - index * 0.9, 0))
            label = Text(event.name.replace("_", " "), font_size=18, color=BACKGROUND).move_to(bar)
            bars.add(VGroup(bar, label))
        axis = Line((-3.2, 1.8, 0), (3.2, 1.8, 0), color=TEXT, stroke_width=2)
        self.add_world(axis, bars)
        self.add_screen_ui(Text("overlap is intentional, timing is deterministic", font_size=21, color=TEXT).move_to((0, -5.8, 0)))
        self.play(Create(axis), LaggedStart(*(FadeIn(bar, shift=UP * 0.12) for bar in bars), lag_ratio=0.12), run_time=1)
        self.wait(1)
