"""Synthetic CQG demonstration; it is intentionally not a production reel."""

from __future__ import annotations

import json
from pathlib import Path

from manim import DOWN, UP, Circle, Create, Scene, Text, Write

from moto_motion.core.safe_area import LayoutClass, LogicalCanvas, NormalizedRect
from moto_motion.creative_quality import (
    ApprovalStore,
    ApprovalStatus,
    PreviewManifest,
    SemanticRole,
    VisualElement,
    build_quality_report,
    compute_revision_id,
    analyze_opening,
    evaluate_visual_prominence,
    generate_hook_variants,
)


class CreativeQualityDemo(Scene):
    """A three-second synthetic opening used to exercise preview plumbing."""

    def construct(self):
        title = Text("WHY DOES THE WIDE LINE WIN?", font_size=34, color="#F5F7FA").to_edge(UP, buff=.7)
        subject = Circle(radius=1.25, color="#35D5E5").shift(DOWN * .4)
        label = Text("EXIT SPEED", font_size=24, color="#F4C95D").next_to(subject, DOWN, buff=.3)
        self.add(title)
        self.play(Create(subject), Write(label), run_time=1.0)
        self.wait(2.0)


def build_demo(output_dir: str | Path = "media/creative_quality_demo") -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    variants = generate_hook_variants(topic="Why the wide line can win", core_question="Which line exits faster?", audience="F1 strategy fans", verified_claims=("The comparison uses the declared exit-speed measure.",), required_assets=("racing_line_diagram",))
    selected = variants[1]
    revision_id = compute_revision_id({"topic": "wide_line", "selected_hook": selected.to_dict(), "opening": "wide_line_demo_v1"})
    canvas = LogicalCanvas(1080, 1920)
    elements = (
        VisualElement("headline", SemanticRole.PRIMARY_HEADLINE, LayoutClass.STRICT_SAFE, NormalizedRect(.18, .12, .64, .10), text=selected.narration_text, effective_font_size=34, contrast_ratio=8.0),
        VisualElement("racing_line", SemanticRole.PRIMARY_SUBJECT, LayoutClass.SAFE_ANCHOR, NormalizedRect(.25, .25, .50, .32), critical_anchor=(.5, .45)),
        VisualElement("caption", SemanticRole.CAPTION, LayoutClass.STRICT_SAFE, canvas.caption_band(), text="Which line exits faster?", effective_font_size=22, contrast_ratio=7.0),
    )
    findings = evaluate_visual_prominence(elements, canvas=canvas)
    opening = analyze_opening({"scenes": [{"id": "opening", "start_seconds": 0.0, "end_seconds": 3.0, "primary_subject": "racing line comparison", "first_meaningful_motion_seconds": .35, "curiosity_gap": "Which line exits faster?"}]})
    preview_path = output_dir / "preview" / "synthetic_cqg_demo" / revision_id / "preview_manifest.json"
    preview = PreviewManifest(**json.loads(preview_path.read_text(encoding="utf-8"))) if preview_path.exists() else None
    report = build_quality_report(reel_id="synthetic_cqg_demo", creative_revision=revision_id, selected_hook_variant=selected, preview=preview, findings=findings, opening=opening, approval_status=ApprovalStatus.NOT_REVIEWED)
    (output_dir / "hook_variants.json").write_text(json.dumps([variant.to_dict() for variant in variants], indent=2) + "\n", encoding="utf-8")
    store = ApprovalStore(output_dir / "approval.json")
    store.mark_preview_ready(reel_id="synthetic_cqg_demo", revision_id=revision_id, preview_manifest_id=revision_id)
    store.approve(reel_id="synthetic_cqg_demo", revision_id=revision_id, preview_manifest_id=revision_id, approved_by="demo-reviewer")
    gate = store.check_full_render(reel_id="synthetic_cqg_demo", revision_id=revision_id, preview_manifest_id=revision_id)
    report = build_quality_report(reel_id="synthetic_cqg_demo", creative_revision=revision_id, selected_hook_variant=selected, preview=preview, findings=findings, opening=opening, approval_status=ApprovalStatus.APPROVED)
    report.write_json(output_dir / "quality_report.json")
    (output_dir / "full_render_gate.json").write_text(json.dumps({"allowed": gate.allowed, "reason": gate.reason, "bypassed": gate.bypassed}, indent=2) + "\n", encoding="utf-8")
    return output_dir


if __name__ == "__main__":
    print(build_demo())

