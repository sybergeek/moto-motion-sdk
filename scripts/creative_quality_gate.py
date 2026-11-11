#!/usr/bin/env python3
"""Small CLI for future-reel CQG planning, previewing and approval checks.

Examples:
  python scripts/creative_quality_gate.py hooks --topic "Why the wide line wins" \
    --question "Which line exits faster?" --audience "F1 strategy fans" \
    --output media/creative_quality/hooks.json
  python scripts/creative_quality_gate.py preview --reel-id reel_006 \
    --revision-id abc123 --source-video media/reels/reel_006/full.mp4
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from moto_motion.core.safe_area import LayoutClass, LogicalCanvas, NormalizedRect
from moto_motion.creative.conversion.models import ConversionPlan
from moto_motion.creative.conversion.planner import ConversionPlanner
from moto_motion.creative_quality import ApprovalStore, OpeningPreviewRenderer, PreviewManifest, PreviewRequest, SemanticRole, VisualElement, analyze_opening, build_quality_report, evaluate_visual_prominence, generate_hook_variants


def main() -> int:
    parser = argparse.ArgumentParser(description="RaceXplained Creative Quality Gate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    hooks = subparsers.add_parser("hooks", help="generate hook planning alternatives")
    hooks.add_argument("--topic", required=True)
    hooks.add_argument("--question", required=True)
    hooks.add_argument("--audience", required=True)
    hooks.add_argument("--count", type=int, default=3)
    hooks.add_argument("--output", type=Path, required=True)

    preview = subparsers.add_parser("preview", help="trim an existing render and extract its first frame")
    preview.add_argument("--reel-id", required=True)
    preview.add_argument("--revision-id", required=True)
    preview.add_argument("--source-video", type=Path, required=True)
    preview.add_argument("--output-dir", type=Path, default=Path("media/creative_quality"))
    preview.add_argument("--duration", type=float, default=3.0)
    preview.add_argument("--width", type=int, default=1080)
    preview.add_argument("--height", type=int, default=1920)

    check = subparsers.add_parser("check-approval", help="check an exact approval before full render")
    check.add_argument("--approval-file", type=Path, required=True)
    check.add_argument("--reel-id", required=True)
    check.add_argument("--revision-id", required=True)
    check.add_argument("--preview-manifest-id")
    check.add_argument("--bypass-reason")

    report = subparsers.add_parser("report", help="combine opening, prominence and preview evidence into JSON")
    report.add_argument("--reel-id", required=True)
    report.add_argument("--revision-id", required=True)
    report.add_argument("--preview-manifest", type=Path)
    report.add_argument("--scene-manifest", type=Path)
    report.add_argument("--narration-manifest", type=Path)
    report.add_argument("--elements-json", type=Path, help="JSON array of declared VisualElement objects")
    report.add_argument("--conversion-json", type=Path)
    report.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "hooks":
        variants = generate_hook_variants(topic=args.topic, core_question=args.question, audience=args.audience, count=args.count)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps([variant.to_dict() for variant in variants], indent=2) + "\n", encoding="utf-8")
        print(args.output)
        return 0
    if args.command == "preview":
        request = PreviewRequest(args.reel_id, args.revision_id, args.duration, (args.width, args.height), output_dir=args.output_dir)
        manifest = OpeningPreviewRenderer().trim_video(args.source_video, request)
        print(json.dumps(manifest.to_dict(), indent=2))
        return 0
    if args.command == "report":
        preview_manifest = None
        if args.preview_manifest:
            preview_data = json.loads(args.preview_manifest.read_text(encoding="utf-8"))
            preview_manifest = PreviewManifest(**preview_data)
        opening = analyze_opening(args.scene_manifest, args.narration_manifest) if args.scene_manifest else None
        findings = []
        if args.elements_json:
            elements = []
            for item in json.loads(args.elements_json.read_text(encoding="utf-8")):
                bounds = item["bounds"]
                elements.append(VisualElement(item["element_id"], SemanticRole(item["role"]), LayoutClass(item["layout_class"]), NormalizedRect(bounds["x"], bounds["y"], bounds["width"], bounds["height"]), start_seconds=item.get("start_seconds", 0.0), end_seconds=item.get("end_seconds", 3.0), visible=item.get("visible", True), text=item.get("text"), effective_font_size=item.get("effective_font_size"), contrast_ratio=item.get("contrast_ratio"), background_is_uniform=item.get("background_is_uniform"), critical_anchor=tuple(item["critical_anchor"]) if item.get("critical_anchor") else None))
            resolution = preview_manifest.resolution if preview_manifest else (1080, 1920)
            findings.extend(evaluate_visual_prominence(elements, canvas=LogicalCanvas(*resolution)))
        conversion_review = None
        if args.conversion_json:
            conversion_review = ConversionPlanner.racexplained_defaults().review(ConversionPlan.from_dict(json.loads(args.conversion_json.read_text(encoding="utf-8"))))
        quality_report = build_quality_report(reel_id=args.reel_id, creative_revision=args.revision_id, preview=preview_manifest, findings=findings, opening=opening, conversion_review=conversion_review)
        quality_report.write_json(args.output)
        print(args.output)
        return 0
    gate = ApprovalStore(args.approval_file).check_full_render(reel_id=args.reel_id, revision_id=args.revision_id, preview_manifest_id=args.preview_manifest_id, bypass_reason=args.bypass_reason)
    print(json.dumps({"allowed": gate.allowed, "reason": gate.reason, "approval_status": gate.approval_status.value, "bypassed": gate.bypassed}))
    return 0 if gate.allowed else 2


if __name__ == "__main__":
    sys.exit(main())

