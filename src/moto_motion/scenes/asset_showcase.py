"""Large-format F1 asset inspection scene."""

try:
    from manim import Create, Text, UP
except ImportError:  # pragma: no cover
    Create = Text = UP = None

from .portrait import PortraitScene
from ..core.constants import TEXT
from ..renderers.manim.vehicles import F1Car


class F1AssetShowcase(PortraitScene):
    def construct(self):
        car = F1Car()
        title = Text("F1 CAR / VECTOR ASSET", color=TEXT, font_size=32).to_edge(UP, buff=0.6)
        self.add(title)
        self.play(Create(car.mobject), run_time=2)
        self.wait(1)
