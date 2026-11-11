#!/usr/bin/env bash
set -euo pipefail
MOTO_MOTION_PREVIEW=1 manim -pql src/moto_motion/scenes/typography_showcase.py TypographyShowcase
MOTO_MOTION_PREVIEW=1 manim -pql src/moto_motion/scenes/transition_showcase.py TransitionShowcase
