"""Future-design mockup for rider identity graphics; not a Reel production."""

from manim import *  # noqa: F403

from moto_motion.core.constants import CYAN, GOLD, RED
from moto_motion.core.safe_area import LogicalCanvas
from moto_motion.core.themes import EDITORIAL_IVORY
from moto_motion.models import MotoGPBikeStyle
from moto_motion.renderers.manim.branding import RaceXplainedChapter
from moto_motion.renderers.manim.rider_identity import MotoGPBikeSide, RiderHelmetBadge, RiderSideProfile
from moto_motion.scenes.portrait import PortraitScene


class RiderIdentityShowcase(PortraitScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, theme=EDITORIAL_IVORY, **kwargs)

    def construct(self):
        canvas = LogicalCanvas(1080, 1920)
        self.add_screen_ui(RaceXplainedChapter(chapter="RIDER IDENTITY MOCKUPS", color="#718090").mobject(canvas))

        side_title = Text("SIDE VIEW · TECHNIQUE", font="Barlow Condensed", weight="BOLD", font_size=26, color=self.theme.text)
        side_title.move_to((*self.layout.point((.5, .82), safe=False), 0))
        side = VGroup(
            MotoGPBikeSide(identity="marc_marquez", scale=.9).mobject,
            RiderSideProfile(identity="marc_marquez", scale=.9).mobject,
        )
        side.move_to((*self.layout.point((.5, .63), safe=False), 0))
        side_note = Text("lean · braking · acceleration", font="Barlow Condensed", font_size=19, color=self.theme.secondary_text)
        side_note.move_to((*self.layout.point((.5, .48), safe=False), 0))

        badge_title = Text("HELMET BADGES · IDENTITY", font="Barlow Condensed", weight="BOLD", font_size=26, color=self.theme.text)
        badge_title.move_to((*self.layout.point((.5, .37), safe=False), 0))
        badges = VGroup(
            RiderHelmetBadge(identity="marc_marquez", label="MARC", label_color=self.theme.text, scale=.72).mobject,
            RiderHelmetBadge(identity="jorge_martin", label="MARTÍN", label_color=self.theme.text, scale=.72).mobject,
            RiderHelmetBadge(identity="marco_bezzecchi", label="BEZZECCHI", label_color=self.theme.text, scale=.72).mobject,
        ).arrange(RIGHT, buff=.55).scale(.72)
        badges.move_to((*self.layout.point((.5, .24), safe=False), 0))
        note = Text("use top view for racing lines · use these for rider recognition", font="Barlow Condensed", font_size=17, color=self.theme.secondary_text)
        note.move_to((*self.layout.point((.5, .09), safe=False), 0))

        self.add_screen_ui(side_title, side_note, badge_title, note)
        self.add_world(side, badges)
        self.play(FadeIn(side_title), FadeIn(side), FadeIn(side_note), run_time=.7)
        self.play(FadeIn(badge_title), LaggedStart(*(FadeIn(b) for b in badges), lag_ratio=.12), FadeIn(note), run_time=1)
        self.wait(1)
