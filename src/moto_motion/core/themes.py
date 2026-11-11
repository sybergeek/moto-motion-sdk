"""Adaptive, scene-independent color themes and contrast utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class SemanticColors:
    braking: str = "#F05A45"
    acceleration: str = "#32C7D5"
    focus: str = "#F4C95D"
    positive_delta: str = "#49D9BC"
    warning: str = "#F4C95D"
    negative_delta: str = "#F05A45"


@dataclass(frozen=True)
class Theme:
    key: str
    name: str
    background: str
    surface: str
    text: str
    secondary_text: str
    accent: str
    secondary_accent: str
    track: str
    border: str
    semantic: SemanticColors = SemanticColors()

    def color(self, role: str) -> str:
        if hasattr(self, role):
            return str(getattr(self, role))
        if hasattr(self.semantic, role):
            return str(getattr(self.semantic, role))
        raise KeyError(f"unknown theme role: {role}")


MIDNIGHT_TECHNICAL = Theme(
    "midnight_technical", "Midnight Technical", "#101820", "#263746", "#F5F7FA",
    "#A5B2C2", "#35D5E5", "#FF684F", "#2E3C49", "#536779",
)
EDITORIAL_IVORY = Theme(
    "editorial_ivory", "Editorial Ivory", "#F1EFE9", "#FFFFFF", "#18232E",
    "#5C6B78", "#007D91", "#D74632", "#D6D3CC", "#9FA8AE",
)
CARBON_SIGNAL = Theme(
    "carbon_signal", "Carbon & Signal", "#090B10", "#1E2430", "#D9E0E8",
    "#8C9BAF", "#D9FF45", "#8C9BAF", "#252D39", "#465365",
)
RACING_HERITAGE = Theme(
    "racing_heritage", "Racing Heritage", "#162C39", "#264757", "#F7F1E7",
    "#A9BCC6", "#FFB84D", "#A9BCC6", "#315666", "#66808C",
)

THEMES: Mapping[str, Theme] = {
    theme.key: theme
    for theme in (MIDNIGHT_TECHNICAL, EDITORIAL_IVORY, CARBON_SIGNAL, RACING_HERITAGE)
}
# Editorial Ivory is the forward-looking default for new RaceXplained work.
# Existing reels pin their theme explicitly, so changing this default does not
# rewrite or re-render approved exports.
DEFAULT_THEME = EDITORIAL_IVORY


def _rgb(hex_color: str) -> tuple[float, float, float]:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"expected #RRGGBB, got {hex_color!r}")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))


def relative_luminance(hex_color: str) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (_rgb(hex_color))
    return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted((relative_luminance(foreground), relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def passes_text_contrast(foreground: str, background: str, *, large_text: bool = False) -> bool:
    return contrast_ratio(foreground, background) >= (3.0 if large_text else 4.5)


def best_contrast(background: str, *candidates: str) -> str:
    if not candidates:
        candidates = ("#FFFFFF", "#000000")
    return max(candidates, key=lambda color: contrast_ratio(color, background))


def vehicle_separation_color(theme: Theme, vehicle_primary: str) -> str:
    """Choose a quiet outline that separates a vehicle from the environment."""
    candidates = (theme.text, theme.border, "#FFFFFF", "#000000")
    visible = tuple(color for color in candidates if contrast_ratio(color, theme.background) >= 3.0)
    if not visible:
        return best_contrast(theme.background, *candidates)
    return max(visible, key=lambda color: (contrast_ratio(color, theme.background), contrast_ratio(color, vehicle_primary)))


def blend_hex(start: str, end: str, progress: float) -> str:
    """Blend theme colors without a white flash between light/dark environments."""
    progress = max(0.0, min(1.0, progress))
    mixed = tuple(round((a + (b - a) * progress) * 255) for a, b in zip(_rgb(start), _rgb(end)))
    return "#{:02X}{:02X}{:02X}".format(*mixed)
