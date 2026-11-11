"""Structured CQG report combining objective findings and human review prompts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from moto_motion.creative.conversion.validator import ConversionReview

from .models import ApprovalStatus, HookVariant, PreviewManifest, QualityFinding
from .opening import OpeningTimeline


@dataclass(frozen=True)
class QualityReport:
    reel_id: str
    creative_revision: str
    selected_hook_variant: str | None
    preview: PreviewManifest | None
    findings: tuple[QualityFinding, ...]
    opening: OpeningTimeline | None
    conversion_review: ConversionReview | None
    approval_status: ApprovalStatus
    recommended_changes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "reel_id": self.reel_id,
            "creative_revision": self.creative_revision,
            "selected_hook_variant": self.selected_hook_variant,
            "preview": self.preview.to_dict() if self.preview else None,
            "technical_validation_results": [finding.to_dict() for finding in self.findings],
            "opening_timeline": self.opening.to_dict() if self.opening else None,
            "conversion_review": [issue.__dict__ for issue in self.conversion_review.issues] if self.conversion_review else None,
            "approval_status": self.approval_status.value,
            "recommended_changes": list(self.recommended_changes),
            "creative_review_questions": [
                "Is the subject immediately identifiable on a sound-off mobile preview?",
                "Is the curiosity gap specific and relevant to the target audience?",
                "Does the first meaningful visual event support the narration?",
                "Is the opening intentionally composed rather than merely empty or decorative?",
                "Does the full reel provide a credible reason to return without interrupting the hook?",
            ],
        }

    def write_json(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str) + "\n", encoding="utf-8")
        return path


def build_quality_report(
    *,
    reel_id: str,
    creative_revision: str,
    selected_hook_variant: HookVariant | None = None,
    preview: PreviewManifest | None = None,
    findings: Iterable[QualityFinding] = (),
    opening: OpeningTimeline | None = None,
    conversion_review: ConversionReview | None = None,
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REVIEWED,
) -> QualityReport:
    all_findings = list(findings)
    if opening:
        all_findings.extend(opening.findings)
    recommendations = tuple(finding.recommendation for finding in all_findings if finding.recommendation)
    return QualityReport(reel_id, creative_revision, selected_hook_variant.variant_id if selected_hook_variant else None, preview, tuple(all_findings), opening, conversion_review, approval_status, recommendations)

