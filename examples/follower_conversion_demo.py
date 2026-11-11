"""CTA-only preview scene; this is not a complete reel renderer."""

from manim import Scene

from moto_motion.core.safe_area import LogicalCanvas
from moto_motion.renderers.manim.branding import FollowCTA


class FollowerConversionDemo(Scene):
    def construct(self):
        canvas = LogicalCanvas(1080, 1920)
        cta = FollowCTA("More racing explained", series="THE SCIENCE")
        self.play(*cta.animations(canvas)[:1])
        self.wait(1.5)
        self.play(cta.animations(canvas)[1])

