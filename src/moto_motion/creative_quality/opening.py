"""Opening timeline analysis from existing scene and narration manifests."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from .models import QualityFinding, QualitySeverity


def _load(value: Mapping[str, Any] | str | Path) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return json.loads(Path(value).read_text(encoding="utf-8"))


@dataclass(frozen=True)
class OpeningTimeline:
    duration_seconds: float
    first_visible_subject: str | None
    first_narration_start_seconds: float | None
    first_caption_start_seconds: float | None
    first_meaningful_motion_seconds: float | None
    first_factual_claim: str | None
    first_curiosity_moment: str | None
    first_scene_transition_seconds: float | None
    intentional_silence_seconds: float | None
    opening_branding: str | None
    findings: tuple[QualityFinding, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["findings"] = [finding.to_dict() for finding in self.findings]
        return value


def _first_number(items: list[Mapping[str, Any]], *keys: str) -> float | None:
    for item in items:
        for key in keys:
            candidate = item.get(key)
            if isinstance(candidate, (int, float)):
                return float(candidate)
    return None


def analyze_opening(
    scene_manifest: Mapping[str, Any] | str | Path,
    narration_manifest: Mapping[str, Any] | str | Path | None = None,
    *,
    duration_seconds: float = 3.0,
) -> OpeningTimeline:
    """Return evidence from declared manifests; missing declarations stay None."""
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")
    scenes_data = _load(scene_manifest)
    scenes = [item for item in scenes_data.get("scenes", []) if isinstance(item, Mapping) and float(item.get("start_seconds", 0.0)) < duration_seconds]
    narration_data = _load(narration_manifest) if narration_manifest is not None else {}
    segments = [item for item in narration_data.get("segments", []) if isinstance(item, Mapping) and float(item.get("start_seconds", 0.0)) < duration_seconds]
    first_scene = scenes[0] if scenes else {}
    first_segment = segments[0] if segments else {}
    first_subject = first_scene.get("primary_subject") or first_scene.get("subject")
    first_caption = _first_number(scenes, "caption_start_seconds", "caption_at_seconds")
    first_motion = _first_number(scenes, "first_meaningful_motion_seconds", "meaningful_motion_seconds", "motion_at_seconds")
    transition = _first_number(scenes[1:], "start_seconds")
    narration_start = _first_number(segments, "start_seconds")
    facts = first_segment.get("factual_claim") or first_segment.get("verified_claim") or first_scene.get("factual_claim")
    curiosity = first_scene.get("curiosity_gap") or first_scene.get("hook_question") or first_segment.get("curiosity_gap")
    branding = first_scene.get("opening_branding") or first_scene.get("branding")
    silence = narration_start if narration_start and narration_start > 0 else None
    findings: list[QualityFinding] = []
    if not first_subject:
        findings.append(QualityFinding("opening_subject_undeclared", QualitySeverity.WARNING, "The first visible subject is not declared in the opening manifest.", recommendation="Declare the primary subject so the mobile review can verify recognition."))
    if first_motion is None:
        findings.append(QualityFinding("opening_motion_undeclared", QualitySeverity.INFO, "No first meaningful motion event is declared.", recommendation="Record the first visual event for a sound-off opening review."))
    if narration_start is None:
        findings.append(QualityFinding("opening_narration_missing", QualitySeverity.WARNING, "No narration segment starts in the opening manifest.", recommendation="Use a provisional preview only and regenerate after narration timing is available."))
    elif first_motion is not None and narration_start > first_motion + 0.75:
        findings.append(QualityFinding("narration_visual_lead", QualitySeverity.WARNING, "Narration starts materially after the declared first motion event.", recommendation="Confirm the intentional pause or align the supporting visual with narration."))
    if branding and not first_subject:
        findings.append(QualityFinding("branding_before_subject", QualitySeverity.WARNING, "Opening branding is declared before a named subject is established.", recommendation="Keep branding subtle and let the hook establish the subject first."))
    if first_scene and float(first_scene.get("end_seconds", duration_seconds)) - float(first_scene.get("start_seconds", 0.0)) >= 1.5 and first_motion is None:
        findings.append(QualityFinding("static_opening_review", QualitySeverity.WARNING, "The first declared scene holds for at least 1.5 seconds without a declared meaningful motion event.", recommendation="Review whether the opening is intentionally cinematic or delays the hook."))
    return OpeningTimeline(duration_seconds, str(first_subject) if first_subject else None, narration_start, first_caption, first_motion, str(facts) if facts else None, str(curiosity) if curiosity else None, transition, silence, str(branding) if branding else None, tuple(findings))

