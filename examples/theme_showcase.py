"""Portrait showcase for all adaptive Motorsport Motion themes."""

from manim import *  # noqa: F403

from moto_motion.core.themes import THEMES, EDITORIAL_IVORY, MIDNIGHT_TECHNICAL, blend_hex
from moto_motion.renderers.manim.vehicles import F1Car
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.typography import TypographySystem


class ThemeShowcase(PortraitScene):
    def construct(self):
        panels = VGroup()
        for index, theme in enumerate(THEMES.values()):
            panel = RoundedRectangle(width=8.1, height=3.35, corner_radius=0.12, fill_color=theme.background, fill_opacity=1, stroke_color=theme.border, stroke_width=2)
            panel.move_to((0, 5.55 - index * 3.7, 0))
            system = TypographySystem(self.layout, theme)
            title = system.manim_text(theme.name.upper(), system.headline_style(23)).move_to(panel.get_center() + LEFT * 1.45 + UP * 0.72)
            roles = VGroup(
                Dot(color=theme.accent, radius=0.09),
                Dot(color=theme.secondary_accent, radius=0.09),
                Dot(color=theme.semantic.braking, radius=0.09),
                Dot(color=theme.semantic.positive_delta, radius=0.09),
            ).arrange(RIGHT, buff=0.2).next_to(title, DOWN, aligned_edge=LEFT, buff=0.22)
            track = Arc(radius=1.1, start_angle=-PI / 2, angle=PI * 0.85, color=theme.track, stroke_width=17).move_to(panel.get_center() + RIGHT * 2.15)
            line = Arc(radius=1.1, start_angle=-PI / 2, angle=PI * 0.85, color=theme.accent, stroke_width=3).move_to(track)
            car = F1Car(theme=theme).mobject.scale(0.18).move_to(panel.get_center() + RIGHT * 2.35 + DOWN * 0.12)
            panels.add(VGroup(panel, title, roles, track, line, car))
        heading_system = TypographySystem(self.layout, self.theme)
        heading = heading_system.manim_text("ADAPTIVE MOTORSPORT THEMES", heading_system.headline_style(28)).to_edge(UP, buff=0.35)
        self.add_screen_ui(heading)
        self.add_world(panels)
        self.play(LaggedStart(*(FadeIn(panel, shift=UP * 0.15) for panel in panels), lag_ratio=0.13), run_time=1.8)
        self.wait(1.2)


class AdaptiveThemeReel(PortraitScene):
    def construct(self):
        current_content = None
        background = Rectangle(
            width=9.2,
            height=16.2,
            fill_color=self.theme.background,
            fill_opacity=1,
            stroke_width=0,
        )
        self.add(background)
        for theme in THEMES.values():
            system = TypographySystem(self.layout, theme)
            surface = RoundedRectangle(width=7.6, height=3.1, corner_radius=0.14, fill_color=theme.surface, fill_opacity=1, stroke_color=theme.border, stroke_width=2).move_to((0, -3.6, 0))
            title = system.manim_text(theme.name.upper(), system.headline_style(34)).move_to((0, 4.9, 0))
            track = Arc(radius=2.6, start_angle=PI, angle=-PI * 0.78, color=theme.track, stroke_width=34).move_to((0.2, 0.5, 0))
            racing = Arc(radius=2.6, start_angle=PI, angle=-PI * 0.78, color=theme.accent, stroke_width=4).move_to(track)
            data = system.telemetry_label("illustrative exit", "164 KM/H", color=theme.accent, size=29).move_to(surface)
            next_content = VGroup(track, racing, surface, title, data)
            if current_content is None:
                background.set_fill(theme.background)
                self.add(next_content)
                self.play(FadeIn(next_content, shift=RIGHT * 0.25), run_time=0.6)
            else:
                wipe = Rectangle(
                    width=9.4,
                    height=16.4,
                    fill_color=theme.background,
                    fill_opacity=1,
                    stroke_width=0,
                ).move_to(RIGHT * 9.4).set_z_index(20)
                self.add(wipe)
                self.play(
                    FadeOut(current_content, shift=LEFT * 0.5),
                    wipe.animate.move_to(ORIGIN),
                    run_time=0.38,
                    rate_func=smooth,
                )
                background.set_fill(theme.background)
                self.remove(wipe)
                self.play(
                    FadeIn(next_content, shift=RIGHT * 0.5),
                    run_time=0.42,
                    rate_func=smooth,
                )
            current_content = next_content
            self.wait(0.55)
