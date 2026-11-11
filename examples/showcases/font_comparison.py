"""Portrait comparison sheet for candidate motorsport typography families."""

from pathlib import Path

from manim import *  # noqa: F403
from manimpango import register_font

from moto_motion.scenes.portrait import PortraitScene
from moto_motion.typography import TypographySystem


FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "candidates"


class FontComparisonSheet(PortraitScene):
    """Render one identical headline across the candidate font families."""

    candidates = (
        ("MICHROMA", "Michroma-Regular.ttf", "F1 display candidate", "NORMAL", "#35D5E5"),
        ("SAIRA", None, "F1 technical candidate", "EXTRABOLD", "#A5B2C2"),
        ("OXANIUM", None, "current F1 profile", "EXTRABOLD", "#F4C95D"),
        ("CHAKRA PETCH", None, "MotoGP display candidate", "BOLD", "#49D9BC"),
        ("EXO 2", "Exo2-wght.ttf", "MotoGP alternative", "BOLD", "#35D5E5"),
        ("RAJDHANI", None, "current MotoGP profile", "BOLD", "#F05A45"),
    )

    def construct(self):
        self._register_candidates()
        system = TypographySystem(self.layout, self.theme)
        title = system.headline("TYPEFACE CANDIDATES", size=28, max_width=7.5).move_to((*self.layout.point((0.5, 0.94)), 0))
        subtitle = system.technical_label("BRAKE LATER. LOSE TIME. / SAME COPY / ORIGINAL SPECIMEN", size=12).move_to((*self.layout.point((0.5, 0.885)), 0))
        title.set_z_index(30)
        subtitle.set_z_index(30)
        self.add_screen_ui(title, subtitle)

        rows = VGroup()
        start_y = 5.0
        for index, (family, filename, role, weight, accent) in enumerate(self.candidates):
            panel = RoundedRectangle(width=7.65, height=1.45, corner_radius=0.10, fill_color=self.theme.surface, fill_opacity=0.88, stroke_color=accent, stroke_width=1.5).move_to((0, start_y - index * 1.72, 0))
            label = Text(family, font=system.resolve_font("Inter", ("Helvetica Neue", "Arial")), weight="BOLD", font_size=12, color=self.theme.secondary_text).move_to(panel.get_left() + RIGHT * 0.38 + UP * 0.42)
            role_mob = Text(role.upper(), font=system.resolve_font("IBM Plex Mono", ("Menlo", "DejaVu Sans Mono")), weight="MEDIUM", font_size=10, color=accent).move_to(panel.get_left() + RIGHT * 0.38 + DOWN * 0.42)
            sample = Text("BRAKE LATER. LOSE TIME.", font=family, weight=TypographySystem.manim_weight(weight), font_size=25, color=self.theme.text).set_max_width(5.9).move_to(panel.get_center() + RIGHT * 0.45)
            rows.add(VGroup(panel, label, role_mob, sample))
        self.add_screen_ui(rows)
        self.play(LaggedStart(*(FadeIn(row, shift=RIGHT * 0.16) for row in rows), lag_ratio=0.08), run_time=1.8)

        footer_panel = RoundedRectangle(width=7.65, height=0.88, corner_radius=0.08, fill_color=self.theme.background, fill_opacity=1, stroke_color=self.theme.border, stroke_width=1).move_to((0, -5.60, 0))
        footer_label = Text("TITILLIUM WEB", font="Titillium Web", weight="BOLD", font_size=16, color=self.theme.text).move_to(footer_panel.get_left() + RIGHT * 1.05)
        footer_sample = Text("technical / broadcast body candidate", font="Titillium Web", weight="NORMAL", font_size=16, color=self.theme.secondary_text).move_to(footer_panel.get_right() + LEFT * 2.05)
        footer = VGroup(footer_panel, footer_label, footer_sample)
        self.add_screen_ui(footer)
        self.play(FadeIn(footer, shift=UP * 0.12), run_time=0.45)
        self.wait(1.2)

    @staticmethod
    def _register_candidates():
        for filename in ("Michroma-Regular.ttf", "Exo2-wght.ttf", "TitilliumWeb-Bold.ttf"):
            register_font(str(FONT_DIR / filename))
