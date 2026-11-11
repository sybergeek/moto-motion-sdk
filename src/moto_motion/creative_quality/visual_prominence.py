"""Context-sensitive mobile prominence checks, separate from safe-area checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from moto_motion.core.safe_area import LayoutClass, LayoutElement, LogicalCanvas, NormalizedRect, validate_scene_layout

from .models import QualityFinding, QualitySeverity, SemanticRole, VisualElement


@dataclass(frozen=True)
class ProminenceThresholds:
    primary_subject_area_ratio: float = 0.035
    primary_subject_width_ratio: float = 0.18
    headline_font_size: float = 24.0
    supporting_text_font_size: float = 16.0
    caption_font_size: float = 18.0
    minimum_text_display_seconds: float = 0.7
    text_contrast_ratio: float = 4.5
    max_simultaneous_text_blocks: int = 4
    max_competing_primary_elements: int = 2


def _overlap(first: NormalizedRect, second: NormalizedRect) -> bool:
    return first.x < second.right and first.right > second.x and first.y < second.bottom and first.bottom > second.y


def evaluate_visual_prominence(
    elements: Iterable[VisualElement],
    *,
    canvas: LogicalCanvas,
    thresholds: ProminenceThresholds = ProminenceThresholds(),
) -> tuple[QualityFinding, ...]:
    elements = tuple(elements)
    findings: list[QualityFinding] = []
    active_text = [e for e in elements if e.visible and e.text and e.role not in {SemanticRole.DECORATIVE, SemanticRole.BACKGROUND}]
    active_primary = [e for e in elements if e.visible and e.role in {SemanticRole.PRIMARY_SUBJECT, SemanticRole.PRIMARY_HEADLINE, SemanticRole.CRITICAL_DIAGRAM}]
    layout_elements = [LayoutElement(element.element_id, element.layout_class, ((element.start_seconds, element.bounds), (element.end_seconds, element.bounds)), (("critical", element.critical_anchor),) if element.critical_anchor is not None else ()) for element in elements]
    for violation in validate_scene_layout(canvas, layout_elements):
        findings.append(QualityFinding("safe_area_violation", QualitySeverity.ERROR, violation.message, violation.element_id, "Fix the normalized bounds or classify the visual correctly before production.", {"boundary": violation.boundary, "timestamp": violation.timestamp}))
    if len(active_text) > thresholds.max_simultaneous_text_blocks:
        findings.append(QualityFinding("dense_text_region", QualitySeverity.WARNING, "Several text blocks are simultaneous in the opening; inspect the mobile preview for competing reading demands.", recommendation="Remove, sequence or shorten nonessential labels.", evidence={"active_text_blocks": len(active_text), "threshold": thresholds.max_simultaneous_text_blocks}))
    if len(active_primary) > thresholds.max_competing_primary_elements:
        findings.append(QualityFinding("competing_primary_elements", QualitySeverity.WARNING, "More than two elements are declared primary at once.", recommendation="Choose one dominant subject or stage the reveal.", evidence={"active_primary_elements": len(active_primary)}))
    for element in elements:
        if element.bounds.width <= 0 or element.bounds.height <= 0:
            findings.append(QualityFinding("invalid_bounds", QualitySeverity.ERROR, "Visual element has non-positive bounds.", element.element_id))
            continue
        area_ratio = element.bounds.width * element.bounds.height
        if element.role is SemanticRole.PRIMARY_SUBJECT and element.visible and (area_ratio < thresholds.primary_subject_area_ratio or element.bounds.width < thresholds.primary_subject_width_ratio):
            findings.append(QualityFinding("subject_prominence_review", QualitySeverity.WARNING, "The registered primary subject occupies a small portion of the frame; this is a review prompt, not a universal minimum.", element.element_id, "Confirm the subject is recognizable at mobile size, or document why a wide comparison intentionally uses a smaller subject.", {"area_ratio": area_ratio, "width_ratio": element.bounds.width, "threshold_area_ratio": thresholds.primary_subject_area_ratio, "threshold_width_ratio": thresholds.primary_subject_width_ratio}))
        if element.role is SemanticRole.PRIMARY_SUBJECT and not element.visible:
            findings.append(QualityFinding("primary_subject_not_visible", QualitySeverity.ERROR, "The primary subject is declared but not visible in the opening window.", element.element_id, "Show or explicitly relabel the opening subject before production."))
        if element.text and element.effective_font_size is not None:
            minimum = thresholds.headline_font_size if element.role is SemanticRole.PRIMARY_HEADLINE else thresholds.caption_font_size if element.role is SemanticRole.CAPTION else thresholds.supporting_text_font_size
            if element.effective_font_size < minimum:
                findings.append(QualityFinding("text_size_review", QualitySeverity.WARNING, "Effective text size is below the configured role-specific mobile review threshold.", element.element_id, "Inspect the downscaled frame; shorten or recompose before shrinking further.", {"effective_font_size": element.effective_font_size, "threshold": minimum, "role": element.role.value}))
        if element.text and element.end_seconds - element.start_seconds < thresholds.minimum_text_display_seconds:
            findings.append(QualityFinding("short_text_window", QualitySeverity.WARNING, "Text is displayed briefly for mobile reading.", element.element_id, "Shorten the text, extend the hold, or provide narration support.", {"duration_seconds": element.end_seconds - element.start_seconds}))
        if element.text and element.contrast_ratio is not None and element.contrast_ratio < thresholds.text_contrast_ratio:
            findings.append(QualityFinding("low_text_contrast", QualitySeverity.WARNING, "Measured text contrast is below the configured readability threshold.", element.element_id, "Increase separation or use a surface/outline; complex moving footage still requires human review.", {"contrast_ratio": element.contrast_ratio, "threshold": thresholds.text_contrast_ratio}))
        if element.text and element.background_is_uniform is False and element.contrast_ratio is None:
            findings.append(QualityFinding("complex_background_contrast_unknown", QualitySeverity.WARNING, "Text is over a complex background without a sampled contrast value.", element.element_id, "Review representative moving frames at mobile size; one sample cannot guarantee readability."))
        if element.layout_class is LayoutClass.SAFE_ANCHOR and element.critical_anchor is not None and not canvas.safe_rect.contains(element.critical_anchor):
            findings.append(QualityFinding("critical_anchor_outside_safe_area", QualitySeverity.ERROR, "A SAFE_ANCHOR element's critical anchor is outside the safe rectangle.", element.element_id, "Keep the important rider number, label or diagram anchor protected."))
    for index, first in enumerate(elements):
        for second in elements[index + 1:]:
            intervals_overlap = first.start_seconds < second.end_seconds and second.start_seconds < first.end_seconds
            if first.visible and second.visible and intervals_overlap and _overlap(first.bounds, second.bounds) and first.role not in {SemanticRole.BACKGROUND, SemanticRole.DECORATIVE} and second.role not in {SemanticRole.BACKGROUND, SemanticRole.DECORATIVE}:
                findings.append(QualityFinding("semantic_overlap_review", QualitySeverity.WARNING, "Registered semantic elements overlap at the same opening timestamp.", first.element_id, f"Inspect overlap with {second.element_id}; safe-area compliance alone does not establish visual clarity.", {"other_element_id": second.element_id}))
    return tuple(findings)

