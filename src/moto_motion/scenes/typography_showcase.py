"""Premium portrait typography package for Formula 1 and MotoGP."""

from manim import *  # noqa: F403

from moto_motion.renderers.manim.motogp import MotoGPBike
from moto_motion.renderers.manim.vehicles import F1Car
from moto_motion.models import MotoGPBikeModel, MotoGPBikeStyle
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.typography import F1_PROFILE, MOTOGP_PROFILE, Headline, HighlightedText, TechnicalLabel, TelemetryCounter, TelemetryValue, TypographySystem


class TypographyShowcase(PortraitScene):
    """12–15 second showcase of the category-specific typography system."""

    def construct(self):
        theme = self.theme
        f1 = TypographySystem(self.layout, theme, profile=F1_PROFILE)
        motogp = TypographySystem(self.layout, theme, profile=MOTOGP_PROFILE)
        grid = VGroup(*[Line((-4.5, y, 0), (4.5, y, 0), color=theme.border, stroke_width=1, stroke_opacity=0.22) for y in (-5.2, -2.0, 1.2, 4.4)])
        self.add_world(grid)

        f1_car = F1Car(theme=theme).mobject.scale(0.5).move_to((0, -0.8, 0))
        f1_headline = Headline("BRAKE LATER.", system=f1, size=43).mobject().move_to((*self.layout.point((0.5, 0.84)), 0))
        f1_sub = HighlightedText(("LOSE", "TIME."), highlights={"LOSE": theme.semantic.braking}, system=f1, size=34).mobject().move_to((*self.layout.point((0.5, 0.72)), 0))
        f1_value = TelemetryCounter(148, 164).mobject(system=f1, color=theme.semantic.braking, label="F1 / BRAKE PHASE").move_to((*self.layout.point((0.5, 0.16)), 0))
        f1_telemetry = VGroup(f1_value)
        f1_group = VGroup(f1_car, f1_headline, f1_sub, f1_telemetry)
        self.add_world(f1_car)
        self.add_screen_ui(f1_headline, f1_sub, f1_telemetry)
        self.play(FadeIn(f1_car, shift=DOWN * 0.25), f1.directional_headline_entrance(f1_headline, direction="up"), f1.staggered_word_reveal(f1_sub, direction="right", duration=0.6), run_time=1.2)
        self.play(FadeIn(f1_telemetry, shift=UP * 0.1), run_time=0.45)
        self.play(f1.telemetry_count_up(f1_value, "F1 / BRAKE PHASE", TelemetryCounter(148, 164), color=theme.semantic.braking), run_time=0.7)
        self.play(f1.highlight_sweep(f1_sub, color=theme.semantic.braking), run_time=0.55)
        self.wait(1.6)

        bike = MotoGPBike(MotoGPBikeModel(style=MotoGPBikeStyle(primary=theme.semantic.focus, secondary=theme.accent))).mobject.scale(0.72).move_to((0, -0.7, 0))
        gp_headline = Headline("LEAN DEEPER.", system=motogp, size=43).mobject().move_to((*self.layout.point((0.5, 0.84)), 0))
        gp_sub = HighlightedText(("FIND", "THE", "LIMIT."), highlights={"LIMIT.": theme.accent}, system=motogp, size=32).mobject().move_to((*self.layout.point((0.5, 0.72)), 0))
        gp_label = TechnicalLabel("MotoGP / LEAN ANGLE", system=motogp, size=17).mobject().move_to((*self.layout.point((0.5, 0.22)), 0))
        gp_value = TelemetryValue("54°", system=motogp, size=31).mobject().move_to((*self.layout.point((0.5, 0.16)), 0))
        gp_group = VGroup(bike, gp_headline, gp_sub, gp_label, gp_value)
        self.add_world(bike)
        self.add_screen_ui(gp_headline, gp_sub, gp_label, gp_value)
        self.play(FadeOut(f1_group, shift=LEFT * 0.35), FadeIn(gp_group, shift=RIGHT * 0.35), run_time=0.85)
        self.play(motogp.highlight_sweep(gp_sub, color=theme.accent), run_time=0.55)
        self.wait(2.1)

        f1_card = self._profile_card(f1, "FORMULA 1", "OXANIUM / SAIRA", theme.semantic.acceleration, (-1.75, 0.4, 0))
        gp_card = self._profile_card(motogp, "MOTOGP", "RAJDHANI / BARLOW", theme.semantic.focus, (1.75, 0.4, 0))
        comparison_title = TypographySystem(self.layout, theme).headline("TYPE WITH DIRECTION", size=31, max_width=7.4).move_to((*self.layout.point((0.5, 0.86)), 0))
        comparison_note = TypographySystem(self.layout, theme).technical_label("DISPLAY / SECONDARY / TELEMETRY", size=16).move_to((*self.layout.point((0.5, 0.16)), 0))
        comparison = VGroup(f1_card, gp_card)
        self.add_screen_ui(comparison_title, comparison_note)
        self.play(FadeOut(gp_group, shift=LEFT * 0.35), FadeIn(comparison, shift=RIGHT * 0.35), FadeIn(comparison_title, shift=UP * 0.12), FadeIn(comparison_note, shift=UP * 0.08), run_time=0.9)
        self.play(LaggedStart(*(FadeIn(item, shift=UP * 0.12) for item in comparison), lag_ratio=0.16), run_time=0.8)
        self.wait(2.7)

    def _profile_card(self, system: TypographySystem, title: str, stack: str, accent: str, center: tuple[float, float, float]):
        panel = RoundedRectangle(width=3.0, height=3.4, corner_radius=0.12, fill_color=self.theme.surface, fill_opacity=0.96, stroke_color=accent, stroke_width=2).move_to(center)
        title_mob = system.subheading(title, size=22, max_width=2.6).move_to(panel.get_top() + DOWN * 0.52)
        stack_mob = system.technical_label(stack, size=13, color=self.theme.secondary_text).move_to(panel.get_bottom() + UP * 0.55)
        sample = HighlightedText(("EXIT", "SPEED"), highlights={"EXIT": accent}, system=system, size=28).mobject().move_to(panel.get_center())
        return VGroup(panel, title_mob, stack_mob, sample)
