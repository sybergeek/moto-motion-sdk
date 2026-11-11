"""Validation scenes for the reusable driver character system, not Reel #3."""

from manim import DOWN, ORIGIN, RIGHT, UP, FadeIn, Scene, Text, VGroup

from moto_motion.renderers.manim import DriverCharacter


class _CharacterPreview(Scene):
    character_id = "kimi_antonelli"
    variant = "neutral"

    def construct(self):
        character = DriverCharacter(self.character_id, variant=self.variant).scale(3.6)
        self.add(character.move_to(ORIGIN))


class KimiNeutralPreview(_CharacterPreview):
    variant = "neutral"


class KimiSmilingPreview(_CharacterPreview):
    variant = "smiling"


class KimiSurprisedPreview(_CharacterPreview):
    variant = "surprised"


class KimiCelebratingPreview(_CharacterPreview):
    variant = "celebrating"


class KimiPointingPreview(_CharacterPreview):
    variant = "pointing"


class MaxNeutralPreview(_CharacterPreview):
    character_id = "max_verstappen"
    variant = "neutral"


class MaxCelebratingPreview(_CharacterPreview):
    character_id = "max_verstappen"
    variant = "celebrating"


class KimiContactSheet(Scene):
    """A labelled QA sheet; every tile comes through the production adapter."""

    def construct(self):
        self.camera.background_color = "#edf4f3"
        tiles = []
        for name in ("neutral", "smiling", "surprised", "celebrating", "pointing"):
            character = DriverCharacter("kimi_antonelli", variant=name).scale(1.36)
            label = Text(name.replace("_", " ").title(), font="Arial", weight="BOLD", color="#101820", font_size=28)
            label.next_to(character, DOWN, buff=0.12)
            tiles.append(VGroup(character, label))
        grid = VGroup(*tiles[:3]).arrange(RIGHT, buff=0.45).shift(UP * 1.7)
        lower = VGroup(*tiles[3:]).arrange(RIGHT, buff=0.75).shift(DOWN * 1.8)
        heading = Text("KIMI ANTONELLI • CHARACTER SYSTEM", font="Arial", weight="BOLD", color="#101820", font_size=32).to_edge(UP, buff=0.35)
        self.add(heading, grid, lower)


class KimiMaxContactSheet(Scene):
    """Same-scale review of the first two character-system drivers."""

    def construct(self):
        self.camera.background_color = "#edf4f3"
        kimi = DriverCharacter("kimi_antonelli", variant="neutral").scale(2.2)
        max_driver = DriverCharacter("max_verstappen", variant="neutral").scale(2.2)
        kimi_label = Text("KIMI ANTONELLI  •  12", font="Arial", weight="BOLD", color="#101820", font_size=24).next_to(kimi, DOWN, buff=0.18)
        max_label = Text("MAX VERSTAPPEN  •  3", font="Arial", weight="BOLD", color="#101820", font_size=24).next_to(max_driver, DOWN, buff=0.18)
        left = VGroup(kimi, kimi_label)
        right = VGroup(max_driver, max_label)
        pair = VGroup(left, right).arrange(RIGHT, buff=1.25).shift(DOWN * 0.2)
        heading = Text("RACEXPLAINED • SHARED CHARACTER SYSTEM", font="Arial", weight="BOLD", color="#101820", font_size=30).to_edge(UP, buff=0.4)
        subheading = Text("Identical scale • stable anchors • modular SVG layers", font="Arial", color="#36505b", font_size=20).next_to(heading, DOWN, buff=0.12)
        self.add(heading, subheading, pair)


class KimiCharacterAnimationTest(Scene):
    """Short integration check for blink, expression and celebration controls."""

    def construct(self):
        self.camera.background_color = "#101820"
        title = Text("THE DRIVER LAYER", font="Arial", weight="BOLD", color="#f4fbfa", font_size=39).to_edge(UP, buff=0.55)
        subtitle = Text("blink • expression • celebration", font="Arial", color="#19cbb8", font_size=25).next_to(title, DOWN, buff=0.16)
        character = DriverCharacter("kimi_antonelli", variant="neutral").scale(3.15).move_to(DOWN * 0.55)
        self.add(title, subtitle)
        self.play(FadeIn(character, shift=UP * 0.2), run_time=0.35)
        self.play(character.blink(), run_time=0.10)
        self.play(character.open_eyes(), run_time=0.10)
        self.play(character.change_expression("smiling"), run_time=0.25)
        self.play(character.celebrate(), run_time=0.35)
        self.wait(0.5)


class MaxCharacterAnimationTest(Scene):
    """Max compatibility check using the shared blink and celebration controls."""

    def construct(self):
        self.camera.background_color = "#101820"
        title = Text("THE DRIVER LAYER", font="Arial", weight="BOLD", color="#f4fbfa", font_size=39).to_edge(UP, buff=0.55)
        subtitle = Text("Max Verstappen • blink • celebration", font="Arial", color="#f6c642", font_size=25).next_to(title, DOWN, buff=0.16)
        character = DriverCharacter("max_verstappen", variant="neutral").scale(3.15).move_to(DOWN * 0.55)
        self.add(title, subtitle)
        self.play(FadeIn(character, shift=UP * 0.2), run_time=0.35)
        self.play(character.blink(), run_time=0.10)
        self.play(character.open_eyes(), run_time=0.10)
        self.play(character.change_expression("celebrating"), run_time=0.25)
        self.play(character.celebrate(), run_time=0.35)
        self.wait(0.5)
