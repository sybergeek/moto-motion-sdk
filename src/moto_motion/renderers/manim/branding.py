"""Reusable RaceXplained branding and chapter markers for portrait reels."""

from __future__ import annotations

from dataclasses import dataclass

from manim import Text

from moto_motion.core.safe_area import LayoutClass, LayoutElement, LogicalCanvas, NormalizedRect, position_within_safe_area


@dataclass(frozen=True)
class RaceXplainedChapter:
    """Small, consistent series/chapter marker for the top of every scene."""

    chapter: str = "MOTORSPORT EXPLAINER"
    brand: str = "RACEXPLAINED"
    font: str = "Barlow Condensed"
    font_size: int = 15
    color: str = "#5C6B78"
    # Top-left normalized coordinates; keep the marker inside instagram_reels_v1.
    normalized_y: float = .12

    def label(self) -> str:
        return f"{self.brand} · {self.chapter}" if self.chapter else self.brand

    def mobject(self, canvas: LogicalCanvas):
        if not canvas.safe_rect.y <= self.normalized_y <= canvas.safe_rect.bottom:
            raise ValueError("chapter marker must remain inside the selected safe area")
        return Text(self.label(), font=self.font, weight="BOLD", font_size=self.font_size, color=self.color).move_to(
            (*canvas.normalized_to_manim((.5, self.normalized_y)), 0)
        )


@dataclass(frozen=True)
class FollowCTA:
    """Minimal approved CTA visual; strategy selection stays in creative.conversion.

    ``mobject()`` creates and positions the visual but does not automatically
    register its rendered bounds with the shared collision allocator. For a
    future production scene, pair it with ``layout_element()`` and register a
    corresponding ``LayoutRequest`` on the scene before the full render. This
    explicit step preserves backward compatibility for approved scenes while
    allowing the Creative Quality Gate to catch CTA/caption/diagram overlap.
    """

    text: str
    series: str | None = None
    brand: str = "RACEXPLAINED"
    normalized_center: tuple[float, float] = (.5, .28)
    normalized_size: tuple[float, float] = (.70, .075)
    font: str = "Barlow Condensed"
    font_size: int = 22
    text_color: str = "#F5F7FA"
    accent_color: str = "#35D5E5"
    surface_color: str = "#101820"

    def layout_element(self, canvas: LogicalCanvas, *, start_seconds: float = 0.0, end_seconds: float = 2.0) -> LayoutElement:
        """Return the legacy sampled contract used by collision validation.

        This describes the CTA panel, not arbitrary children added to the
        returned Manim group. If the panel is transformed after construction,
        create/update a matching ``LayoutRequest`` with the final normalized
        bounds; the validator cannot infer later custom transforms from this
        immutable contract.
        """
        center = position_within_safe_area(self.normalized_center, self.normalized_size, canvas)
        rect = NormalizedRect(center[0] - self.normalized_size[0] / 2, center[1] - self.normalized_size[1] / 2, *self.normalized_size)
        return LayoutElement("follow_cta", LayoutClass.STRICT_SAFE, ((start_seconds, rect), (end_seconds, rect)))

    def mobject(self, canvas: LogicalCanvas):
        from manim import FadeIn, FadeOut, RoundedRectangle, Text, VGroup

        center = position_within_safe_area(self.normalized_center, self.normalized_size, canvas)
        width = self.normalized_size[0] * canvas.manim_frame_width
        height = self.normalized_size[1] * canvas.manim_frame_height
        label = f"{self.brand}  ·  {self.text}" if self.brand else self.text
        if self.series:
            label = f"{label}  ·  {self.series}"
        content = Text(label, font=self.font, weight="BOLD", font_size=self.font_size, color=self.text_color)
        content.scale_to_fit_width(width - .35)
        panel = RoundedRectangle(width=width, height=height, corner_radius=.10, fill_color=self.surface_color, fill_opacity=.96, stroke_color=self.accent_color, stroke_width=1.5)
        content.move_to(panel)
        return VGroup(panel, content).move_to((*canvas.normalized_to_manim(center), 0))

    def animations(self, canvas: LogicalCanvas):
        """Return restrained entrance/exit animations for a scene author."""
        from manim import FadeIn, FadeOut

        group = self.mobject(canvas)
        return FadeIn(group, run_time=.18), FadeOut(group, run_time=.18)
