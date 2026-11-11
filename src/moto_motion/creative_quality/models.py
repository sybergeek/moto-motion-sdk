"""Serializable contracts shared by the Creative Quality Gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from moto_motion.core.safe_area import LayoutClass, NormalizedRect


class QualitySeverity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class SemanticRole(StrEnum):
    PRIMARY_SUBJECT = "primary_subject"
    PRIMARY_HEADLINE = "primary_headline"
    SUPPORTING_TEXT = "supporting_text"
    CRITICAL_DIAGRAM = "critical_diagram"
    CAPTION = "caption"
    DECORATIVE = "decorative"
    BACKGROUND = "background"


class HookType(StrEnum):
    COUNTERINTUITIVE_FACT = "counterintuitive_fact"
    PREDICTION_CHALLENGE = "prediction_challenge"
    VISUAL_MYSTERY = "visual_mystery"
    HISTORICAL_SURPRISE = "historical_surprise"
    UNEXPECTED_RESULT = "unexpected_result"
    TECHNICAL_DEMONSTRATION = "technical_demonstration"
    RACING_COMPARISON = "racing_comparison"
    CHAMPIONSHIP_STAKES = "championship_stakes"


class ApprovalStatus(StrEnum):
    NOT_REVIEWED = "NOT_REVIEWED"
    PREVIEW_READY = "PREVIEW_READY"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"


@dataclass(frozen=True)
class HookVariant:
    variant_id: str
    hook_type: HookType
    narration_text: str
    opening_visual_concept: str
    intended_curiosity_gap: str
    first_meaningful_visual_event: str
    approximate_duration_seconds: float
    required_assets: tuple[str, ...] = ()
    factual_claims_requiring_verification: tuple[str, ...] = ()
    clarity_risks: tuple[str, ...] = ()
    retention_risks: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["hook_type"] = self.hook_type.value
        return value


@dataclass(frozen=True)
class PreviewManifest:
    reel_id: str
    revision_id: str
    duration_seconds: float
    resolution: tuple[int, int]
    frame_rate: int
    video_path: str
    first_frame_path: str | None
    contact_sheet_path: str | None
    narration_status: str
    timing_status: str
    provisional: bool
    source_kind: str
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["resolution"] = list(self.resolution)
        return value


@dataclass(frozen=True)
class VisualElement:
    element_id: str
    role: SemanticRole
    layout_class: LayoutClass
    bounds: NormalizedRect
    start_seconds: float = 0.0
    end_seconds: float = 3.0
    visible: bool = True
    text: str | None = None
    effective_font_size: float | None = None
    contrast_ratio: float | None = None
    background_is_uniform: bool | None = None
    stroke_or_outline: bool = False
    critical_anchor: tuple[float, float] | None = None
    notes: str = ""


@dataclass(frozen=True)
class QualityFinding:
    code: str
    severity: QualitySeverity
    message: str
    element_id: str | None = None
    recommendation: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["severity"] = self.severity.value
        return value

