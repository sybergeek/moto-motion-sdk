#!/usr/bin/env bash
set -euo pipefail
python scripts/generate_assets.py
MOTO_MOTION_PREVIEW=1 manim -pql src/moto_motion/scenes/asset_showcase.py F1AssetShowcase
