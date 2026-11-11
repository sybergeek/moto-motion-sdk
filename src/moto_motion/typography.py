"""Portrait-first kinetic typography contracts and Manim adapters."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging
from typing import Iterable, Mapping

from .core.constants import (
    FONT_BODY,
    FONT_BODY_FALLBACKS,
    FONT_DISPLAY,
    FONT_DISPLAY_FALLBACKS,
    FONT_TELEMETRY,
    FONT_TELEMETRY_FALLBACKS,
)
from .core.layout import DEFAULT_LAYOUT, SafeAreaLayout
from .core.themes import DEFAULT_THEME, Theme, passes_text_contrast


class TypographyRole(str, Enum):
    DISPLAY = "display"
    EXPLANATORY = "explanatory"
    TELEMETRY = "telemetry"


@dataclass(frozen=True)
class TypographyProfile:
    """Explicit category-specific typography contract."""

    key: str
    display_family: str
    display_weight: str
    display_fallbacks: tuple[str, ...]
    secondary_family: str
    secondary_weight: str
    secondary_fallbacks: tuple[str, ...]
    telemetry_family: str
    telemetry_weight: str
    telemetry_fallbacks: tuple[str, ...]
    display_letter_spacing: float = -0.015
    display_line_spacing: float = 0.86
    secondary_letter_spacing: float = 0.0
    telemetry_letter_spacing: float = 0.02
    emphasis_skew: float = 0.0


F1_PROFILE = TypographyProfile(
    "f1", "Oxanium", "EXTRABOLD",
    ("Oxanium", "Rajdhani", "Barlow Condensed", "Arial Narrow", "DejaVu Sans Condensed", "Arial"),
    "Saira", "SEMIBOLD",
    ("Saira", "Inter", "Saira SemiCondensed", "Helvetica Neue", "Arial", "DejaVu Sans"),
    "IBM Plex Mono", "MEDIUM", ("IBM Plex Mono", "Menlo", "DejaVu Sans Mono", "Liberation Mono"),
)

MOTOGP_PROFILE = TypographyProfile(
    "motogp", "Rajdhani", "BOLD",
    ("Rajdhani", "Oxanium", "Barlow Condensed", "Arial Narrow", "DejaVu Sans Condensed", "Arial"),
    "Barlow Condensed", "SEMIBOLD",
    ("Barlow Condensed", "Rajdhani", "Saira", "Helvetica Neue", "Arial", "DejaVu Sans"),
    "IBM Plex Mono", "MEDIUM", ("IBM Plex Mono", "Menlo", "DejaVu Sans Mono", "Liberation Mono"),
    display_letter_spacing=-0.025, display_line_spacing=0.82, emphasis_skew=-0.08,
)

TYPOGRAPHY_PROFILES = {"f1": F1_PROFILE, "motogp": MOTOGP_PROFILE}
LOGGER = logging.getLogger(__name__)
MANIM_WEIGHT_ALIASES = {"EXTRABOLD": "ULTRABOLD", "EXTRA_BOLD": "ULTRABOLD", "BLACK": "ULTRAHEAVY"}


@dataclass(frozen=True)
class TypographyStyle:
    font: str = FONT_BODY
    weight: str = "NORMAL"
    font_size: float = 32
    line_spacing: float = 0.95
    letter_spacing: float = 0.0
    color: str = DEFAULT_THEME.text
    max_width: float = 7.1
    role: TypographyRole = TypographyRole.EXPLANATORY
    fallbacks: tuple[str, ...] = ()


@dataclass(frozen=True)
class HighlightedWord:
    text: str
    color: str = DEFAULT_THEME.semantic.focus


WordHighlight = HighlightedWord


class TypographySystem:
    """Text layout + animation specs; major headlines use directional reveals."""

    def __init__(self, layout: SafeAreaLayout = DEFAULT_LAYOUT, theme: Theme = DEFAULT_THEME, profile: TypographyProfile = F1_PROFILE, category: str | None = None):
        self.layout = layout
        self.theme = theme
        self.profile = TYPOGRAPHY_PROFILES[category] if category is not None else profile

    def headline_style(self, size: float = 42) -> TypographyStyle:
        return TypographyStyle(self.profile.display_family, self.manim_weight(self.profile.display_weight), size, self.profile.display_line_spacing, self.profile.display_letter_spacing, self.theme.text, 7.2, TypographyRole.DISPLAY, self.profile.display_fallbacks)

    def body_style(self, size: float = 24) -> TypographyStyle:
        return TypographyStyle(self.profile.secondary_family, self.profile.secondary_weight, size, 1.0, self.profile.secondary_letter_spacing, self.theme.text, 7.4, TypographyRole.EXPLANATORY, self.profile.secondary_fallbacks)

    def telemetry_style(self, size: float = 24) -> TypographyStyle:
        return TypographyStyle(self.profile.telemetry_family, self.profile.telemetry_weight, size, 1.0, self.profile.telemetry_letter_spacing, self.theme.text, 7.4, TypographyRole.TELEMETRY, self.profile.telemetry_fallbacks)

    @staticmethod
    def manim_weight(weight: str) -> str:
        """Map editorial weight names to the weight names accepted by Manim/Pango."""
        return MANIM_WEIGHT_ALIASES.get(weight.upper(), weight.upper())

    @staticmethod
    def available_fonts() -> frozenset[str]:
        """Return exact Pango family names available to Manim."""
        try:
            from manimpango import list_fonts
            return frozenset(list_fonts())
        except Exception:  # pragma: no cover
            return frozenset()

    @classmethod
    def font_report(cls, profile: TypographyProfile) -> dict[str, dict[str, object]]:
        """Report exact family availability and the requested Pango weight."""
        installed = cls.available_fonts()
        report = {}
        for role, family, weight, fallbacks in (
            ("display", profile.display_family, profile.display_weight, profile.display_fallbacks),
            ("secondary", profile.secondary_family, profile.secondary_weight, profile.secondary_fallbacks),
            ("telemetry", profile.telemetry_family, profile.telemetry_weight, profile.telemetry_fallbacks),
        ):
            report[role] = {
                "requested_family": family,
                "requested_weight": weight,
                "resolved_family": cls.resolve_font(family, fallbacks),
                "family_available": family in installed,
            }
        return report

    @staticmethod
    def resolve_font(preferred: str, fallbacks: tuple[str, ...] | None = None, *, log_fallback: bool = True) -> str:
        """Choose an installed font without making a proprietary font mandatory."""
        try:
            from manimpango import list_fonts
            installed = set(list_fonts())
        except Exception:  # pragma: no cover - only used in minimal installs
            if log_fallback:
                LOGGER.warning("Cannot inspect Pango fonts; requesting '%s' directly", preferred)
            return preferred
        fallbacks = fallbacks or FONT_BODY_FALLBACKS
        for candidate in (preferred, *fallbacks):
            if candidate in installed:
                if candidate != preferred and log_fallback:
                    LOGGER.warning("Font family '%s' unavailable; using explicit fallback '%s'", preferred, candidate)
                return candidate
        sans_fallbacks = sorted(font for font in installed if "Sans" in font or font in {"Arial", "Helvetica"})
        resolved = sans_fallbacks[0] if sans_fallbacks else preferred
        if resolved != preferred and log_fallback:
            LOGGER.warning("Declared fallbacks unavailable for '%s'; using installed family '%s'", preferred, resolved)
        return resolved

    def wrap_words(self, words: Iterable[str], max_chars: int = 22) -> tuple[str, ...]:
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and len(candidate) > max_chars:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return tuple(lines)

    def safe_position(self, normalized: tuple[float, float]) -> tuple[float, float]:
        return self.layout.point(normalized, safe=True)

    def animation_spec(self, kind: str, direction: str = "up", duration: float = 0.55) -> dict[str, object]:
        allowed = {"staggered_word_reveal", "masked_slide", "character_reveal", "directional_entrance", "count_up", "smooth_replace"}
        if kind not in allowed:
            raise ValueError(f"unknown typography animation: {kind}")
        return {"kind": kind, "direction": direction, "duration": duration, "easing": "smoothstep"}

    def manim_text(self, value: str, style: TypographyStyle | None = None):
        try:
            from manim import Text
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("manim_text requires Manim") from exc
        style = style or self.body_style()
        fallbacks = style.fallbacks or {
            TypographyRole.DISPLAY: FONT_DISPLAY_FALLBACKS,
            TypographyRole.EXPLANATORY: FONT_BODY_FALLBACKS,
            TypographyRole.TELEMETRY: FONT_TELEMETRY_FALLBACKS,
        }[style.role]
        text = Text(value, font=self.resolve_font(style.font, fallbacks), weight=self.manim_weight(style.weight), font_size=style.font_size, color=style.color, line_spacing=style.line_spacing)
        return text.set_max_width(style.max_width)

    def headline(self, value: str, *, size: float = 42, max_width: float | None = None):
        style = self.headline_style(size)
        if max_width is not None:
            style = TypographyStyle(style.font, style.weight, style.font_size, style.line_spacing, style.letter_spacing, style.color, max_width, style.role, style.fallbacks)
        return self.manim_text(value.upper(), style)

    def subheading(self, value: str, *, size: float = 28, max_width: float | None = None):
        style = self.body_style(size)
        if max_width is not None:
            style = TypographyStyle(style.font, style.weight, style.font_size, style.line_spacing, style.letter_spacing, style.color, max_width, style.role, style.fallbacks)
        return self.manim_text(value.upper(), style)

    def technical_label(self, value: str, *, size: float = 18, color: str | None = None):
        style = self.body_style(size)
        style = TypographyStyle(style.font, style.weight, style.font_size, style.line_spacing, style.letter_spacing, color or self.theme.secondary_text, style.max_width, style.role, style.fallbacks)
        return self.manim_text(value.upper(), style)

    def telemetry_value(self, value: str, *, size: float = 30, color: str | None = None):
        style = self.telemetry_style(size)
        style = TypographyStyle(style.font, style.weight, style.font_size, style.line_spacing, style.letter_spacing, color or self.theme.accent, style.max_width, style.role, style.fallbacks)
        return self.manim_text(value, style)

    def composed_headline(self, words: Iterable[str], *, highlights: dict[str, str] | None = None, size: float = 42):
        """Build a readable word-level headline with intentional emphasis."""
        from manim import RIGHT, Text, VGroup

        highlights = highlights or {}
        style = self.headline_style(size)
        font = self.resolve_font(style.font, style.fallbacks)
        tokens = [Text(word.upper(), font=font, weight=self.manim_weight(style.weight), font_size=style.font_size, color=highlights.get(word.upper(), style.color)) for word in words]
        return VGroup(*tokens).arrange(RIGHT, buff=0.14).set_max_width(style.max_width)

    def word_reveal(self, headline, *, direction: str = "up", duration: float = 0.75):
        """Reveal headline words with staggered directional motion."""
        from manim import LaggedStart, RIGHT, UP, FadeIn

        vector = UP if direction == "up" else RIGHT
        return LaggedStart(*(FadeIn(word, shift=vector * 0.18) for word in headline), lag_ratio=0.12, run_time=duration)

    def telemetry_label(self, label: str, value: str, *, color: str | None = None, size: float = 22):
        from manim import DOWN, LEFT, Text, VGroup

        color = color or self.theme.accent
        label_mob = Text(label.upper(), font=self.resolve_font(self.profile.secondary_family, self.profile.secondary_fallbacks), weight=self.profile.secondary_weight, font_size=size * 0.62, color=self.theme.secondary_text)
        value_mob = Text(value, font=self.resolve_font(self.profile.telemetry_family, self.profile.telemetry_fallbacks), weight=self.profile.telemetry_weight, font_size=size, color=color)
        return VGroup(label_mob, value_mob).arrange(DOWN, aligned_edge=LEFT, buff=0.06)

    def assert_readable(self, color: str | None = None, background: str | None = None, *, large_text: bool = False) -> None:
        foreground = color or self.theme.text
        surface = background or self.theme.background
        if not passes_text_contrast(foreground, surface, large_text=large_text):
            raise ValueError(f"insufficient text contrast: {foreground} on {surface}")

    def animated(self, value: str, kind: str = "directional_entrance", direction: str = "up", duration: float = 0.55):
        """Return a non-default major-headline reveal animation when Manim is present."""
        from manim import AnimationGroup, FadeIn, LaggedStart, Transform, UP, RIGHT
        text = self.headline(value)
        if kind == "character_reveal":
            return LaggedStart(*(FadeIn(character, shift=UP * 0.16) for character in text), lag_ratio=0.055, run_time=duration), text
        shift = UP * 0.28 if direction == "up" else RIGHT * 0.28
        return FadeIn(text, shift=shift, run_time=duration), text

    def masked_slide_reveal(self, text_mobject, *, direction: str = "right", duration: float = 0.65):
        return MaskedTextReveal(text_mobject, theme=self.theme, direction=direction).build()[1]

    def staggered_word_reveal(self, text_mobject, *, direction: str = "up", duration: float = 0.75):
        return self.word_reveal(text_mobject, direction=direction, duration=duration)

    def directional_headline_entrance(self, text_mobject, *, direction: str = "right", duration: float = 0.6):
        from manim import DOWN, FadeIn, LEFT, RIGHT, UP
        vectors = {"right": LEFT, "left": RIGHT, "up": DOWN, "down": UP}
        return FadeIn(text_mobject, shift=vectors.get(direction, LEFT) * 0.28, run_time=duration)

    def smooth_headline_replacement(self, old, new, *, direction: str = "left", duration: float = 0.65):
        from manim import AnimationGroup, FadeIn, FadeOut, LEFT, RIGHT
        outgoing = LEFT if direction == "left" else RIGHT
        incoming = RIGHT if direction == "left" else LEFT
        return AnimationGroup(FadeOut(old, shift=outgoing * 0.22), FadeIn(new, shift=incoming * 0.22), lag_ratio=0.0, run_time=duration)

    def telemetry_count_up(self, mobject, label: str, counter: "NumericCounter", *, duration: float = 0.8, color: str | None = None):
        from manim import UpdateFromAlphaFunc
        center = mobject.get_center()
        return UpdateFromAlphaFunc(mobject, lambda mob, alpha: mob.become(self.telemetry_label(label, counter.value_at(alpha), color=color, size=28).move_to(center)), run_time=duration)

    def highlight_sweep(self, mobject, *, color: str | None = None, duration: float = 0.55):
        from manim import Rectangle, ShowPassingFlash
        sweep = Rectangle(width=mobject.width + 0.24, height=mobject.height + 0.18, stroke_color=color or self.theme.accent, stroke_width=3, fill_opacity=0).move_to(mobject)
        return ShowPassingFlash(sweep, time_width=0.25, run_time=duration)


class NumericCounter:
    """Deterministic telemetry number formatter for illustrative values."""

    def __init__(self, start: float, end: float, suffix: str = " km/h"):
        self.start, self.end, self.suffix = start, end, suffix

    def value_at(self, progress: float) -> str:
        value = self.start + (self.end - self.start) * max(0.0, min(1.0, progress))
        return f"{value:03.0f}{self.suffix}"


class KineticHeadline:
    """Theme-aware word-level headline and synchronized reveal."""

    def __init__(self, text: str, *, highlights: Mapping[str, str] | None = None, size: float = 44, system: TypographySystem | None = None):
        self.text = text
        self.highlights = {key.upper(): value for key, value in (highlights or {}).items()}
        self.size = size
        self.system = system or TypographySystem()

    def mobject(self):
        return self.system.composed_headline(self.text.split(), highlights=self.highlights, size=self.size)

    def reveal(self, mobject, *, direction: str = "up", duration: float = 0.8):
        return self.system.word_reveal(mobject, direction=direction, duration=duration)


class Headline(KineticHeadline):
    """Profile-aware display headline for a category-specific broadcast package."""

    def __init__(self, text: str, *, category: str = "f1", size: float = 44, system: TypographySystem | None = None, highlights: Mapping[str, str] | None = None):
        super().__init__(text, highlights=highlights, size=size, system=system or TypographySystem(category=category))


class Subheading:
    def __init__(self, text: str, *, category: str = "f1", size: float = 28, system: TypographySystem | None = None):
        self.text = text
        self.system = system or TypographySystem(category=category)
        self.size = size

    def mobject(self):
        return self.system.subheading(self.text, size=self.size)


class TechnicalLabel:
    def __init__(self, text: str, *, category: str = "f1", size: float = 18, system: TypographySystem | None = None):
        self.text = text
        self.system = system or TypographySystem(category=category)
        self.size = size

    def mobject(self):
        return self.system.technical_label(self.text, size=self.size)


class TelemetryValue:
    def __init__(self, value: str, *, category: str = "f1", size: float = 30, system: TypographySystem | None = None):
        self.value = value
        self.system = system or TypographySystem(category=category)
        self.size = size

    def mobject(self):
        return self.system.telemetry_value(self.value, size=self.size)


class HighlightedText:
    """Word-level emphasis that keeps the accent budget explicit."""

    def __init__(self, words: Iterable[str], *, highlights: Mapping[str, str] | None = None, category: str = "f1", size: float = 42, system: TypographySystem | None = None):
        self.words = tuple(words)
        self.highlights = {key.upper(): value for key, value in (highlights or {}).items()}
        self.system = system or TypographySystem(category=category)
        self.size = size

    def mobject(self):
        return self.system.composed_headline(self.words, highlights=self.highlights, size=self.size)


class MaskedTextReveal:
    """Surface-colored travelling mask for editorial text reveals."""

    def __init__(self, text_mobject, *, theme: Theme = DEFAULT_THEME, direction: str = "right"):
        self.text = text_mobject
        self.theme = theme
        self.direction = direction

    def build(self):
        from manim import AnimationGroup, FadeIn, LEFT, Rectangle, RIGHT, VGroup

        vector = RIGHT if self.direction == "right" else LEFT
        mask = Rectangle(width=self.text.width + 0.2, height=self.text.height + 0.15, fill_color=self.theme.background, fill_opacity=1, stroke_width=0).move_to(self.text)
        group = VGroup(self.text, mask)
        animation = AnimationGroup(FadeIn(self.text, shift=vector * 0.12), mask.animate.shift(vector * (self.text.width + 0.35)), lag_ratio=0.05, run_time=0.65)
        return group, animation


class TelemetryCounter(NumericCounter):
    """Monospaced telemetry counter with an explicit illustrative-data label."""

    def mobject(self, progress: float = 0.0, *, system: TypographySystem | None = None, color: str | None = None, label: str = "ILLUSTRATIVE"):
        system = system or TypographySystem()
        return system.telemetry_label(label, self.value_at(progress), color=color or system.theme.accent, size=28)


@dataclass(frozen=True)
class NumericDelta:
    value: float
    unit: str = "s"

    def formatted(self) -> str:
        return f"{self.value:+.2f} {self.unit}"

    def color(self, theme: Theme = DEFAULT_THEME) -> str:
        return theme.semantic.positive_delta if self.value <= 0 else theme.semantic.negative_delta

    def mobject(self, *, system: TypographySystem | None = None):
        system = system or TypographySystem()
        return system.manim_text(self.formatted(), TypographyStyle(FONT_TELEMETRY, "MEDIUM", 28, color=self.color(system.theme), role=TypographyRole.TELEMETRY))


class AnimatedCaption:
    """Safe-area caption with a quiet broadcast surface and directional entrance."""

    def __init__(self, text: str, *, system: TypographySystem | None = None):
        self.text = text
        self.system = system or TypographySystem()

    def build(self):
        from manim import FadeIn, LEFT, Rectangle, VGroup

        label = self.system.manim_text(self.text, self.system.body_style(22))
        panel = Rectangle(width=min(label.width + 0.55, self.system.layout.safe.width), height=label.height + 0.32, fill_color=self.system.theme.surface, fill_opacity=0.94, stroke_width=0)
        label.move_to(panel)
        group = VGroup(panel, label).move_to((*self.system.layout.point((0.5, 0.1)), 0))
        return group, FadeIn(group, shift=LEFT * 0.22, run_time=0.5)
