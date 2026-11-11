"""Standalone SFX system demonstration; does not alter existing reels."""

from pathlib import Path

from manim import *

from moto_motion.models.vehicles import F1CarModel, VehicleStyle
from moto_motion.renderers.manim.characters import DriverCharacter
from moto_motion.renderers.manim.vehicles import F1Car


config.pixel_width = 540
config.pixel_height = 960
config.frame_rate = 30

BG, WHITE, TEAL, GOLD, RED, NAVY = "#0A1019", "#F4F7FA", "#1BC7BA", "#F4C95D", "#E63832", "#0A1D4B"
TROPHY = Path(__file__).resolve().parents[2] / "assets/icons/trophy.svg"


class SFXDemo(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("SFX ON", font="Barlow Condensed", weight="BOLD", font_size=50, color=WHITE).to_edge(UP, buff=.7)
        self.play(FadeIn(title, scale=.75), run_time=.35)
        pop = Text("TEXT POP", font="Barlow Condensed", weight="BOLD", font_size=58, color=TEAL).move_to(UP * 2.3)
        self.play(GrowFromCenter(pop), run_time=.3)
        value = ValueTracker(0)
        count = always_redraw(lambda: Text(str(int(value.get_value())), font="Barlow Condensed", weight="BOLD", font_size=94, color=WHITE).move_to(UP * .75))
        self.add(count)
        self.play(value.animate.set_value(119), run_time=1.2)
        self.play(Indicate(count, color=GOLD), run_time=.25)
        kimi = DriverCharacter("kimi_antonelli", variant="celebrating", scale=1.2).move_to((0, -1.3, 0))
        self.play(FadeIn(kimi, shift=LEFT*.4), run_time=.45)
        car = F1Car(F1CarModel(position=(-5.4, -3.2), rotation=-PI / 2, scale=.46, style=VehicleStyle(NAVY, RED))).mobject
        self.add(car)
        self.play(car.animate.shift(RIGHT * 11), run_time=1.2, rate_func=rate_functions.ease_in_out_cubic)
        trophy = SVGMobject(str(TROPHY)).set_color(GOLD).scale(.85).move_to((0, 3.15, 0))
        reveal = Text("TROPHY REVEAL", font="Barlow Condensed", weight="BOLD", font_size=38, color=GOLD).next_to(trophy, DOWN, buff=.18)
        self.play(GrowFromCenter(trophy), FadeIn(reveal, shift=UP*.1), run_time=.55)
        self.wait(1.8)
