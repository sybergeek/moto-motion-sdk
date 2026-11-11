#!/usr/bin/env bash
set -euo pipefail

MOTO_MOTION_PREVIEW=1 manim -pql examples/showcases/component_showcase.py \
  LayoutComponentShowcase \
  TrajectoryComponentShowcase \
  CircuitComponentShowcase \
  VehicleComponentShowcase \
  MotionComponentShowcase \
  CameraComponentShowcase \
  TypographyComponentShowcase \
  TransitionComponentShowcase \
  EnvironmentComponentShowcase \
  ChoreographyComponentShowcase
