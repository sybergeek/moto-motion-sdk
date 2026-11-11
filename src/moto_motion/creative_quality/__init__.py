"""Creative Quality Gate primitives for future RaceXplained reels."""

from .approval import ApprovalRecord, ApprovalStore, FullRenderGate, compute_revision_id
from .hook_variants import generate_hook_variants
from .models import (
    ApprovalStatus,
    HookType,
    PreviewManifest,
    QualityFinding,
    QualitySeverity,
    SemanticRole,
    VisualElement,
)
from .opening import OpeningTimeline, analyze_opening
from .preview import OpeningPreviewRenderer, PreviewRequest
from .reporting import QualityReport, build_quality_report
from .visual_prominence import ProminenceThresholds, evaluate_visual_prominence

__all__ = [
    "ApprovalRecord", "ApprovalStore", "FullRenderGate", "compute_revision_id", "generate_hook_variants",
    "ApprovalStatus", "HookType", "PreviewManifest", "QualityFinding", "QualitySeverity",
    "SemanticRole", "VisualElement", "OpeningTimeline", "analyze_opening",
    "OpeningPreviewRenderer", "PreviewRequest", "QualityReport", "build_quality_report",
    "ProminenceThresholds", "evaluate_visual_prominence",
]

