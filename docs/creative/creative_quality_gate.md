# RaceXplained Creative Quality Gate

The CQG catches preventable technical and presentation problems before a complete future reel render. It is a review aid, not an Instagram algorithm or virality predictor. It reuses the retention playbook, narration timing, Manim, captions, safe-area layout and follower-conversion modules.

## Architecture

The reusable code lives under [`creative_quality/`](../../src/moto_motion/creative_quality/). `hook_variants.py` creates planning alternatives; `preview.py` creates a bounded opening artifact; `visual_prominence.py` evaluates declared visual hierarchy; `opening.py` reads scene and narration manifests; `approval.py` persists exact-revision approval; and `reporting.py` combines objective findings with human review prompts.

Safe-area checks remain in [`core/safe_area.py`](../../src/moto_motion/core/safe_area.py). Follower conversion remains in [`creative/conversion/`](../../src/moto_motion/creative/conversion/). CQG inspects those decisions rather than duplicating them.

## Future-reel workflow

1. Read the [retention playbook](./retention_playbook.md), [planning template](./script_planning_template.md), and [follower-conversion playbook](./follower_conversion_playbook.md).
2. Generate three hook concepts and verify their claims and required assets.
3. Select one hook and compute a creative revision ID from the approved manifest.
4. Render only the opening preview. Prefer trimming an actual render; for a scene render, the scene must honor `MOTO_MOTION_PREVIEW_DURATION`.
5. Inspect the MP4 and extracted first frame at mobile size with sound off, then review narration/audio synchronization where available.
6. Run safe-area, prominence, opening timeline and conversion checks. Errors are objective failures; warnings are review prompts.
7. Record `PREVIEW_READY`, request changes, or approve the exact revision and preview manifest.
8. Run the gated full-render wrapper only after matching `APPROVED` status.
9. Record post-publication performance as a time-bounded observation; keep missing data as null.

## Commands

Generate hook alternatives:

```bash
PYTHONPATH=src .venv/bin/python scripts/creative_quality_gate.py hooks \
  --topic "Why the wide line can win" \
  --question "Which line exits faster?" \
  --audience "F1 strategy fans" \
  --output media/creative_quality/hooks.json
```

Create a three-second preview and first frame from an existing render:

```bash
PYTHONPATH=src .venv/bin/python scripts/creative_quality_gate.py preview \
  --reel-id reel_006 --revision-id <revision> \
  --source-video media/reels/reel_006/full.mp4
```

Combine a preview, opening manifest and declared visual elements into a JSON report:

```bash
PYTHONPATH=src .venv/bin/python scripts/creative_quality_gate.py report \
  --reel-id reel_006 --revision-id <revision> \
  --preview-manifest media/creative_quality/reel_006/<revision>/preview_manifest.json \
  --scene-manifest reel_006/scene_timing.json \
  --narration-manifest reel_006/narration.json \
  --output media/creative_quality/reel_006/<revision>/quality_report.json
```

Gate an existing render command:

```bash
MOTO_MOTION_APPROVAL_FILE=media/creative_quality/reel_006/approval.json \
MOTO_MOTION_REEL_ID=reel_006 \
MOTO_MOTION_REVISION_ID=<revision> \
MOTO_MOTION_PREVIEW_MANIFEST_ID=<preview-id> \
bash scripts/render_quality_gated.sh -- \
  env PYTHONPATH=src .venv/bin/manim -qh examples/new_reel.py NewReel
```

The existing legacy render scripts are not changed. For tests, debug renders, legacy workflows or an explicit creator-approved exception, use `ApprovalStore.check_full_render(..., bypass_reason=...)`; the resulting report must show `bypassed: true`.

## Objective checks and human review

Errors cover invalid bounds, invisible declared primary subjects, critical-anchor safe-area failures and unmatched approval. Warnings cover small subjects, role-specific text size, low or unknown contrast, short reading windows, semantic overlap, dense text, opening delays, unverified conversion references and timing uncertainty. A small subject may be correct for a wide racing comparison; the creator must review the preview rather than treating thresholds as universal rules.

The gate does not judge whether a hook is interesting, whether an animation feels professional, whether a reveal is satisfying, or whether a viewer will follow. Those remain human creative decisions documented alongside the report.

## Preview limitations

The preview is provisional when narration is unavailable or timing is not audio-derived. It does not invent final timing. Trimming an existing production render preserves its available audio; rendering a scene requires the scene to honor the preview environment variables. Platform UI exclusion zones are not hard-coded because Instagram UI can vary; inspect the portrait preview manually.

## Performance feedback

The Reel #5 historical snapshot is appended at [`data/analytics/performance_observations.json`](../../data/analytics/performance_observations.json). It preserves the supplied views, unique viewers, watch time, skip rate, engagement counts and zero attributed follows while leaving unknown timestamps, duration and retention points null. The qualitative steep initial decline is noted without inventing exact timestamps. Comparisons are observational and warn about missing samples and different observation windows.

