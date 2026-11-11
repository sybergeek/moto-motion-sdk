#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo_root"
mkdir -p media/sfx_demo
PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}" "$repo_root/.venv/bin/manim" --media_dir media/sfx_demo --output_file sfx_demo_visual examples/sfx_demo.py SFXDemo
"$repo_root/.venv/bin/python" scripts/build_sfx_demo_audio.py
ffmpeg -hide_banner -y -i media/sfx_demo/videos/sfx_demo/960p30/sfx_demo_visual.mp4 -i media/sfx_demo/sfx_on.wav -c:v copy -c:a aac -b:a 192k -shortest media/sfx_demo/sfx_demo_with_sfx.mp4
ffmpeg -hide_banner -y -i media/sfx_demo/videos/sfx_demo/960p30/sfx_demo_visual.mp4 -i media/sfx_demo/sfx_off.wav -c:v copy -c:a aac -b:a 192k -shortest media/sfx_demo/sfx_demo_without_sfx.mp4
