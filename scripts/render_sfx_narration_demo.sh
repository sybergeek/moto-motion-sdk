#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

.venv/bin/python scripts/build_sfx_demo_audio.py
VISUAL="media/sfx_demo/videos/sfx_demo/960p30/sfx_demo_visual.mp4"
OUTPUT="media/sfx_narration_demo"

ffmpeg -hide_banner -y -stream_loop -1 -i "$VISUAL" -i "$OUTPUT/baseline.wav" -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -b:a 192k "$OUTPUT/sfx_baseline_with_narration.mp4"
ffmpeg -hide_banner -y -stream_loop -1 -i "$VISUAL" -i "$OUTPUT/narration_aware.wav" -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -b:a 192k "$OUTPUT/sfx_narration_aware.mp4"
