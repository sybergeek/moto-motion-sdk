# Narration-first pacing

Scene durations are estimates until narration exists. The approved script is
the content source, but the audio delivery determines how long each visual beat
must remain on screen.

## Default workflow

1. Approve the script and segment boundaries.
2. Synthesize or record narration in natural mode.
3. Measure each segment's actual duration.
4. Add deliberate phrase pauses; do not speed up long sentences to fit an old storyboard window.
5. Write an audio-derived scene-timing manifest.
6. Retime scene holds, caption windows and SFX events from that manifest.
7. Review the video with narration before final export.

Use:

```bash
python scripts/narrate_manifest.py reel_005/reel_005.narration.json \
  --timing-mode natural \
  --timing-output reel_005/reel_005_scene_timing.audio_derived.json
```

The legacy fixed mode remains available for old productions, but it may use
per-segment `atempo` fitting and should not be the default for new reels.

Every scene should also use the shared `RaceXplainedChapter` marker for a
consistent series/chapter cue at the top of the frame. Keep its chapter label
short and descriptive; it is a persistent identity element, not a substitute
for the scene's primary hook.

For Reel #5, the natural timing pass produced a 39.93-second narration with
scene windows in [`reel_005_scene_timing.audio_derived.json`](../../reel_005/reel_005_scene_timing.audio_derived.json).
