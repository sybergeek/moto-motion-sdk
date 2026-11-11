#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src MOTO_MOTION_PREVIEW=1 ./.venv/bin/manim -ql --disable_caching examples/showcases/font_comparison.py FontComparisonSheet
