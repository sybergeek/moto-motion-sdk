"""Design tokens and render defaults shared by every scene."""

from dataclasses import dataclass

from .themes import DEFAULT_THEME

BACKGROUND = DEFAULT_THEME.background
SURFACE = DEFAULT_THEME.surface
TRACK = DEFAULT_THEME.track
TEXT = DEFAULT_THEME.text
SECONDARY_TEXT = DEFAULT_THEME.secondary_text
CYAN = DEFAULT_THEME.semantic.acceleration
RED = DEFAULT_THEME.semantic.braking
GOLD = DEFAULT_THEME.semantic.focus
GREEN = DEFAULT_THEME.semantic.positive_delta


@dataclass(frozen=True)
class PortraitConfig:
    width: int = 1080
    height: int = 1920
    frame_rate: int = 60
    preview_width: int = 540
    preview_height: int = 960
    preview_frame_rate: int = 30
    safe_margin: float = 0.55
    caption_y: float = -5.9


PORTRAIT = PortraitConfig()
STROKE_WIDTH = 0.045
CORNER_RADIUS = 0.18
FONT_DISPLAY = "Barlow Condensed"
FONT_BODY = "Inter"
FONT_TELEMETRY = "IBM Plex Mono"
FONT_DISPLAY_FALLBACKS = ("Barlow Condensed", "Arial Narrow", "Avenir Next Condensed", "Helvetica Neue", "DejaVu Sans Condensed", "Arial")
FONT_BODY_FALLBACKS = ("Inter", "Helvetica Neue", "Arial", "Avenir Next", "Noto Sans", "Liberation Sans", "DejaVu Sans")
FONT_TELEMETRY_FALLBACKS = ("IBM Plex Mono", "DejaVu Sans Mono", "Liberation Mono", "Menlo")
FONT_FALLBACKS = FONT_BODY_FALLBACKS
