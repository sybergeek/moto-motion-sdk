import json

import pytest

from moto_motion.core.safe_area import LayoutClass, LogicalCanvas, NormalizedRect
from moto_motion.creative_quality import (
    ApprovalStatus,
    ApprovalStore,
    HookType,
    PreviewRequest,
    SemanticRole,
    VisualElement,
    analyze_opening,
    compute_revision_id,
    evaluate_visual_prominence,
    generate_hook_variants,
)
from moto_motion.creative_quality.preview import bounded_duration


def test_hook_variants_are_distinct_and_claims_remain_verification_inputs():
    variants = generate_hook_variants(topic="Why the wide line can win", core_question="Which line exits faster?", audience="F1 strategy fans", verified_claims=("exit-speed comparison",), count=3)
    assert len({variant.variant_id for variant in variants}) == 3
    assert len({variant.hook_type for variant in variants}) == 3
    assert len({variant.narration_text for variant in variants}) == 3
    assert all(variant.factual_claims_requiring_verification == ("exit-speed comparison",) for variant in variants)
    assert variants[0].hook_type in set(HookType)


def test_hook_generation_requires_editorial_inputs():
    with pytest.raises(ValueError):
        generate_hook_variants(topic="", core_question="why", audience="fans")


def test_prominence_uses_role_specific_text_and_full_bleed_exemption():
    canvas = LogicalCanvas(1080, 1920)
    findings = evaluate_visual_prominence([
        VisualElement("headline", SemanticRole.PRIMARY_HEADLINE, LayoutClass.STRICT_SAFE, NormalizedRect(.2, .1, .6, .1), text="Hook", effective_font_size=12, contrast_ratio=2.0),
        VisualElement("background", SemanticRole.BACKGROUND, LayoutClass.FULL_BLEED, NormalizedRect(0, 0, 1, 1)),
    ], canvas=canvas)
    codes = {finding.code for finding in findings}
    assert {"text_size_review", "low_text_contrast"} <= codes
    assert "invalid_bounds" not in codes


def test_prominence_reuses_safe_area_validation_and_detects_interval_overlap():
    canvas = LogicalCanvas(1080, 1920)
    findings = evaluate_visual_prominence([
        VisualElement("title", SemanticRole.PRIMARY_HEADLINE, LayoutClass.STRICT_SAFE, NormalizedRect(.0, .1, .4, .1), start_seconds=0, end_seconds=2, text="Title", effective_font_size=30),
        VisualElement("caption", SemanticRole.CAPTION, LayoutClass.STRICT_SAFE, NormalizedRect(.2, .15, .4, .1), start_seconds=1, end_seconds=3, text="Caption", effective_font_size=22),
    ], canvas=canvas)
    codes = {finding.code for finding in findings}
    assert {"safe_area_violation", "semantic_overlap_review"} <= codes


def test_prominence_warns_about_small_subject_but_does_not_fail_it():
    canvas = LogicalCanvas(1440, 2560)
    findings = evaluate_visual_prominence([VisualElement("bike", SemanticRole.PRIMARY_SUBJECT, LayoutClass.SAFE_ANCHOR, NormalizedRect(.45, .35, .08, .08), critical_anchor=(.5, .39))], canvas=canvas)
    assert any(finding.code == "subject_prominence_review" and finding.severity.value == "WARNING" for finding in findings)


def test_opening_analysis_preserves_declared_evidence_and_flags_missing_narration():
    opening = analyze_opening({"scenes": [{"start_seconds": 0, "end_seconds": 3, "primary_subject": "racing line", "first_meaningful_motion_seconds": .2, "curiosity_gap": "Which line exits faster?"}]})
    assert opening.first_visible_subject == "racing line"
    assert opening.first_meaningful_motion_seconds == .2
    assert any(finding.code == "opening_narration_missing" for finding in opening.findings)


def test_preview_duration_is_configurable_and_bounded():
    assert bounded_duration(3.0, 2.0) == 2.0
    assert PreviewRequest("reel_006", "rev", duration_seconds=5.0).duration_seconds == 5.0
    with pytest.raises(ValueError):
        PreviewRequest("reel_006", "rev", duration_seconds=0)


def test_approval_requires_exact_revision_and_preview_and_supports_visible_bypass(tmp_path):
    store = ApprovalStore(tmp_path / "approval.json")
    revision = compute_revision_id({"opening": "v1"})
    store.mark_preview_ready(reel_id="reel_006", revision_id=revision, preview_manifest_id="preview-v1")
    assert store.check_full_render(reel_id="reel_006", revision_id=revision, preview_manifest_id="preview-v1").allowed is False
    store.approve(reel_id="reel_006", revision_id=revision, preview_manifest_id="preview-v1", approved_by="creator")
    assert store.check_full_render(reel_id="reel_006", revision_id=revision, preview_manifest_id="preview-v1").allowed is True
    assert store.check_full_render(reel_id="reel_006", revision_id="other", preview_manifest_id="preview-v1").allowed is False
    bypass = store.check_full_render(reel_id="reel_006", revision_id="other", preview_manifest_id=None, bypass_reason="debug render")
    assert bypass.allowed and bypass.bypassed
    assert json.loads((tmp_path / "approval.json").read_text())["status"] == ApprovalStatus.APPROVED.value

