# Resolution-independent layout and safe areas

## Important interpretation

The safe area is an **exclusion zone for semantic overlays**, not a page margin. Keep backgrounds, footage, roads, scenery and other environmental layers full-bleed. Only titles, labels, captions, result cards and critical diagram markers are constrained to the protected rectangle. Before rendering a production scene, validate that its Manim camera matches the logical canvas with `validate_camera_canvas`; a mismatch can otherwise create an unintended outer matte.

Reserve the caption lane as a strict-safe rectangle in each scene, then validate it against lower charts, tables and labels with `validate_element_collisions`. The safe rectangle alone cannot prevent a caption from colliding with another correctly-safe element.

The layout engine lives in [`src/moto_motion/core/safe_area.py`](../../src/moto_motion/core/safe_area.py). Scene authors compose in normalized coordinates with a top-left origin:

```python
from moto_motion.core.safe_area import LogicalCanvas, INSTAGRAM_REELS_V1

canvas = LogicalCanvas(1080, 1920, INSTAGRAM_REELS_V1)
title_point = canvas.normalized_to_manim((0.5, 0.15))
caption_band = canvas.caption_band()
```

`instagram_reels_v1` stores normalized margins only: left/right `0.1056`, top `0.09375`, bottom `0.1953`. Pixel bounds are derived for each render size. `archival_master` has no UI margins and is intended for clean masters, not platform publishing.

## Collision allocator limitation and future use

The shared [`LayoutAllocator`](../../src/moto_motion/core/layout_allocator.py)
can choose alternate normalized regions, apply controlled shrinking, and report
an unresolved collision as an export-blocking error. It is used by the carousel
quality report and is available to Manim scenes through
`PortraitScene.register_layout_request()` and
`PortraitScene.resolve_layout_requests()`.

The allocator is intentionally explicit. It cannot discover the semantic role
or final bounds of arbitrary Manim objects, custom SVG children, camera-driven
transforms, or objects moved after registration. A rendered object is therefore
not automatically collision-safe merely because it is on screen. Future scene
components must register a `LayoutRequest` (or a `VisualElement`/`LayoutElement`
contract consumed by the Creative Quality Gate) using final normalized bounds.

For reusable components such as [`FollowCTA`](../../src/moto_motion/renderers/manim/branding.py),
call `layout_element()` for the legacy sampled check and also register a
`LayoutRequest` when the component participates in an allocator-managed scene.
If a component is transformed later, update the request or contract after the
transform. Do not use a global ignore list to hide an unknown overlap; classify
intentional background/anchor relationships with `FULL_BLEED`, `SAFE_ANCHOR`, or
an explicit allowed-overlap relationship instead.

This means the system prevents collisions for registered components and blocks
known unresolved layouts, but it cannot promise zero collisions for unregistered
or continuously transformed custom artwork. The production workflow should
still include a rendered mobile preview and debug-bound overlay for subjective
visual review.

## Classify every element

- `STRICT_SAFE`: titles, captions, equations, statistics and essential callouts. Full bounds are validated.
- `SAFE_ANCHOR`: tracks, paths and arrows may leave the frame, but registered critical anchors are validated.
- `FULL_BLEED`: backgrounds, footage and scenery are exempt from ordinary safe-area errors.

Use `LayoutElement` samples at meaningful animation timestamps and call `validate_scene_layout`. Sampling catches common translation/scale/reveal mistakes; it is not a mathematical guarantee for arbitrary continuous transforms. Violations include the sampled bounds and boundary for concrete correction. Strict violations should fail production validation.

## Captions

Pass `layout=canvas` to [`RaceXplainedCaption`](../../src/moto_motion/renderers/manim/captions.py). The caption uses a safe-area-relative band and scales its maximum width from the logical canvas. Existing calls without a layout remain backward-compatible; new production scenes should opt in explicitly.

## Debug preview

Run the demonstration scene with a debug overlay:

```bash
MOTO_MOTION_DEBUG_LAYOUT=1 MOTO_MOTION_DEMO_WIDTH=1080 MOTO_MOTION_DEMO_HEIGHT=1920 \
  PYTHONPATH=src .venv/bin/python -m manim examples/showcases/layout_safe_area_demo.py LayoutSafeAreaDemo -s -ql
```

For a 4K still, use `MOTO_MOTION_DEMO_WIDTH=2160 MOTO_MOTION_DEMO_HEIGHT=3840` and `-qh`. The debug overlay is conditional and is not added to normal exports; with element registrations it also draws classification-colored bounds and critical-anchor dots.

## Export profiles

`EXPORT_PROFILES` currently contains `instagram_reels_v1` and `archival_master`. Add future platform profiles without changing normalized scene coordinates. Platform safe areas are configuration, not universal guarantees; verify current platform UI guidance before publishing.
