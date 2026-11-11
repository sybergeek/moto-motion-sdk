"""Reusable RaceXplained portrait captions."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

from manim import MarkupText, RoundedRectangle, VGroup

from moto_motion.core.safe_area import LogicalCanvas


CAPTION_TEXT = "#F4F7FA"
CAPTION_EMPHASIS = "#F4C95D"
CAPTION_SURFACE = "#061018"


def wrap_caption_words(text: str, *, max_characters: int = 40) -> list[str]:
    """Wrap on words without dropping or reordering narration text."""
    lines: list[str] = []
    current: list[str] = []
    current_length = 0
    for word in text.split():
        next_length = current_length + (1 if current else 0) + len(word)
        if current and next_length > max_characters:
            lines.append(" ".join(current))
            current = [word]
            current_length = len(word)
        else:
            current.append(word)
            current_length = next_length
    if current:
        lines.append(" ".join(current))
    return lines


@dataclass(frozen=True)
class RaceXplainedCaption:
    """A safe-area, two-line-ready caption with optional word emphasis.

    Captions are deliberately rendered as one markup object instead of a group
    of individual words; that keeps baselines and kerning stable in video.
    """

    text: str
    highlight: str | None = None
    max_characters_per_line: int = 40
    max_width: float = 7.15
    y: float = -6.05
    font_size: int = 21
    layout: LogicalCanvas | None = None
    normalized_y: float | None = None

    def markup(self) -> str:
        lines = wrap_caption_words(self.text, max_characters=self.max_characters_per_line)
        rendered_lines: list[str] = []
        for line in lines:
            words = []
            for word in line.split():
                color = CAPTION_EMPHASIS if word.strip(".,?!") == self.highlight else CAPTION_TEXT
                words.append(f'<span foreground="{color}">{escape(word)}</span>')
            rendered_lines.append(" ".join(words))
        return "\n".join(rendered_lines)

    def mobject(self) -> VGroup:
        max_width = self.max_width
        caption_y = self.y
        if self.layout is not None:
            safe = self.layout.safe_rect
            band = self.layout.caption_band()
            max_width = safe.width * self.layout.manim_frame_width
            target_y = band.y + band.height / 2 if self.normalized_y is None else self.normalized_y
            if not safe.y <= target_y <= safe.bottom:
                raise ValueError("caption normalized_y must remain inside the selected layout safe area")
            caption_y = self.layout.normalized_to_manim((band.x + band.width / 2, target_y))[1]
        text = MarkupText(self.markup(), font="Avenir Next", weight="MEDIUM", font_size=self.font_size, line_spacing=0.82)
        if text.width > max_width - 0.42:
            text.scale_to_fit_width(max_width - 0.42)
        panel = RoundedRectangle(
            width=min(max_width, text.width + 0.42),
            height=text.height + 0.28,
            corner_radius=0.12,
            fill_color=CAPTION_SURFACE,
            fill_opacity=0.94,
            stroke_width=0,
        )
        text.move_to(panel)
        return VGroup(panel, text).move_to((0, caption_y, 0))
