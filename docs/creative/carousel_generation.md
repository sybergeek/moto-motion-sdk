# RaceXplained carousel generation

Before creating or reviewing a carousel, read
[`carousel_art_direction.md`](./carousel_art_direction.md). It defines the
production defaults learned from the Verstappen and Mercedes carousels:
image-led composition, translucent overlays, shared slide systems, contrast,
authenticity, collision avoidance, and mandatory rendered visual QA.

Carousels reuse the Reel design system: the same `Theme` palette, F1 typography
profile, safe-area conventions, and editorial ivory light theme are used by
default. Carousel rendering is separate from Manim Reel rendering so existing
Reel commands and outputs remain unchanged.

## Quick start

Carousel manifests are production inputs and should live with the local
carousel workspace, not in the public SDK examples directory. Use the public
renderer API with a local manifest:

```python
from moto_motion.carousel import CarouselManifest, CarouselRenderer

manifest = CarouselManifest.from_json("path/to/local/carousel_manifest.json")
renderer = CarouselRenderer(manifest)
renderer.render()                 # all slides and contact sheet
renderer.render(slide_index=3)    # regenerate one slide only
renderer.export()                 # ordered ZIP package
```

Set `aspect_ratio` to `"4:5"` for 1080×1350 output or `"1:1"` for 1080×1080 output. The manifest is the single
source of truth and rejects unsupported ratios, inconsistent dimensions,
non-consecutive slide numbers, empty headlines, and missing asset identifiers.

Supported layouts are `hero`, `technical_diagram`, `comparison`, `timeline`,
`data`, `myth_fact`, `full_bleed`, and `conclusion`. Use `visual.type`
`existing_asset` plus an `asset_id` when a registered SVG or raster asset is
required; the renderer must not silently invent a substitute for a missing
asset. Human inspection of `preview.png` remains required for final art
direction, especially for complex asset-backed slides.

## Production visual guardrails

The carousel renderer treats visual QA as part of composition, not as a
last-minute padding exercise:

- Related slides must use a shared composition primitive. The Verstappen
  comeback slides use one photo-led panel and one vertical start-to-finish
  evidence module, with only the content changing.
- Text is bounded by explicit layout boxes. Wrapped text that exceeds its
  declared line count raises an error instead of being silently truncated.
- Text over photography requires a local translucent panel or tonal treatment;
  a global dark overlay is not a substitute for checking the actual crop.
- Position markers, arrows, labels and pills must have independent bounds. A
  connector must not pass through the label or indicator it is explaining.
- Before export, inspect the full-resolution contact sheet and the mobile
  preview. Check title weight, contrast on the actual image crop, safe margins,
  and whether any text crosses a panel boundary.

When a slide needs a new visual grammar, add a reusable renderer primitive and
test it before creating another one-off composition. The quality report checks
technical dimensions and registered layout allocations; human inspection is
still required for photographic contrast and editorial quality.

