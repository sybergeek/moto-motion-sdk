"""Showcase for restrained object- and camera-motivated transitions."""

try:
    from manim import Circle, FadeIn, Scene, Square, Transform, UP, VGroup
except ImportError:  # pragma: no cover
    Scene = object

from .portrait import PortraitScene
from ..core.constants import CYAN, GOLD, RED
from ..transitions import TransitionDirector


class TransitionShowcase(PortraitScene):
    def construct(self):
        director = TransitionDirector()
        block = Square(side_length=1.3, color=CYAN, fill_opacity=1).move_to((-1.3, 0, 0))
        target = Circle(radius=0.72, color=GOLD, fill_opacity=1).move_to((1.3, 0, 0))
        self.add_world(block, target)
        self.play(director.manim_animation(director.object_reveal((1, 0), 0.7), block))
        self.play(director.manim_animation(director.match_cut("object_heading", 0.45, (1, 0)), target))
        self.play(Transform(block, target), run_time=0.8)
        self.wait(1)
