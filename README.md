# Motorsport Motion

Motorsport Motion is a reusable Python SDK for polished, portrait 2D motorsport explainers. It supports Formula 1 and MotoGP-oriented scenes through shared trajectories, circuits, motion profiles, and portrait templates plus category-specific vehicle adapters. The distribution is `moto-motion` and every Python import is `moto_motion`.

The implementation is organized by responsibility:

- `src/moto_motion/geometry/` contains arc-length-aware cubic Bézier trajectories.
- `src/moto_motion/assets.py` generates the original layered F1 SVG asset.
- `src/moto_motion/models/` contains renderer-neutral vehicle models.
- `src/moto_motion/renderers/manim/` adapts vehicles and circuit geometry to Manim.
- `src/moto_motion/effects/` contains reusable motion/easing primitives.
- `src/moto_motion/scenes/` contains portrait templates and the asset showcase.
- `examples/` contains curated demonstration scenes and the component visual lab.

## Repository boundary

This public repository contains reusable SDK code, generic examples, tests,
design guidance, reusable assets, and asset registries. Local reel production
directories, downloaded event media, analytics observations, generated renders,
and one-off experiments are intentionally excluded by `.gitignore`. Source
URLs, factual notes, and production manifests should remain in the local
production workspace unless generalized into reusable SDK guidance.

The intended public contents are:

- `src/moto_motion/` — reusable Python models, geometry, effects, typography,
  video helpers, and Manim renderers.
- `examples/` — curated component demonstrations and reusable example scenes;
  reel-specific manifests, production examples, and one-off carousel drafts
  remain local.
- `tests/` — automated tests for the reusable SDK behavior.
- `assets/` — original or reusable SVG assets, character registries, and
  canonical asset metadata. Optional local MotoGP raster packs and superbike
  packs are excluded.
- `docs/` — reusable API, asset, SFX, and creative-production guidance. Local
  reel reviews, downloaded references, and production-specific integrations are
  excluded.
- `scripts/` — reusable generation, rendering, narration, and inspection
  helpers. One-off local preparation scripts, including
  `scripts/crop_motogp_sticker_grid.swift`, are excluded.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution boundary and
provenance rules. The reusable creative guidance is organized in the
[retention playbook](docs/creative/retention_playbook.md),
[carousel generation guide](docs/creative/carousel_generation.md),
[carousel art direction](docs/creative/carousel_art_direction.md), and
[creative quality gate](docs/creative/creative_quality_gate.md).

## Setup

From the repository root on macOS:

```bash
source .venv/bin/activate
python -m pip install -e '.[test]'
```

The portrait production canvas is 1080×1920 at 60 fps. A 540×960, 30 fps preview is available through `PortraitConfig`. The design system is defined in `moto_motion.core.constants`.

## Motion design system

The upgrade enforces a few editorial rules in reusable APIs:

- `SafeAreaLayout` keeps fixed UI in normalized portrait screen coordinates, separate from world-space vehicles and camera movement.
- `CameraRig` follows a target with look-ahead, clamped movement, smooth interpolation, and direction continuity.
- `TypographySystem` provides profile-driven display headlines, wrapping, safe positioning, counters, and directional/staggered reveal specs. Major headlines use directional reveals instead of default `Write()`.
- `TransitionDirector` creates motivated wipes, match cuts, camera pushes/pulls, object reveals, and selective whip-pan blur.
- `Environment` provides explicit world-layer ordering for tracks, racing lines, vehicles, annotations, foreground, and UI.
- `SceneDirector` composes deterministic vehicle, camera, typography, and annotation timings with named presets: `accelerate`, `brake`, `approach_corner`, `enter_corner`, `exit_corner`, and `reveal_technical_detail`.

The focal point is kept in world-space or screen-space intentionally: typography is never attached to moving vehicle objects, and motion blur is opt-in on transition specs rather than a substitute for path-following animation.

## Premium visual identity

The default visual language combines neutral engineering surfaces with one or two active semantic accents per beat. Reusable typography roles are:

- `F1_PROFILE`: Oxanium ExtraBold, Saira SemiBold, and IBM Plex Mono.
- `MOTOGP_PROFILE`: Rajdhani Bold, Barlow Condensed SemiBold, and IBM Plex Mono.
- `Headline`, `Subheading`, `TechnicalLabel`, `TelemetryValue`, `HighlightedText`, and `AnimatedCaption` are reusable category-aware components.
- `KineticHeadline`, `MaskedTextReveal`, `TelemetryCounter`, and `NumericDelta` remain available for backwards compatibility.

Moto Motion reels use the F1 profile as the shared series typography by default, including MotoGP subjects. The MotoGP profile remains available for comparison and special-purpose packages, but the main reel series keeps one consistent editorial voice.

`TypographySystem.font_report()` exposes requested family names, requested Pango weights, resolved installed families, and availability. If a preferred family is absent, the resolver logs the explicit fallback it selected.

The portrait showcase is a 12–15 second F1/MotoGP package with the detailed F1 asset, an original proportioned MotoGP technical illustration, braking and lean telemetry, direction-aware profile transitions, masked/highlight sweeps, and a side-by-side hierarchy comparison.

`MaskedTextReveal`, `WordHighlight`, responsive maximum widths, safe-area positioning, and contrast validation are provided by `moto_motion.typography`. Font files are not redistributed by this repository.

The adaptive themes in `moto_motion.core.themes` are:

- Midnight Technical
- Editorial Ivory
- Carbon & Signal
- Racing Heritage

Themes control backgrounds, surfaces, text, track rendering, icons, technical overlays, and vehicle separation. Semantic braking, acceleration, focus, warning, and delta colors remain stable across themes. `contrast_ratio`, `passes_text_contrast`, and `blend_hex` support mobile readability and controlled dark/light transitions.

Original SVG icon components are available through `moto_motion.icons`: brake disc, throttle, apex, DRS wing, tyre/contact patch, lap-time delta, steering angle, slipstream, and motorcycle lean angle.

### MotoGP lean physics

`LeanPose` is the renderer-neutral model for front-view cornering geometry. It keeps the road contact point fixed while independently controlling motorcycle lean, rider offset, and rider-relative lean; it also derives the bike COM, rider COM, combined COM, and normalized road-force direction. `solve_bike_lean_for_combined()` supports like-for-like body-position comparisons at the same required combined lean.

`MotoGPLeanRig` is the Manim renderer. Its reusable overlays are `lean_angle_overlay`, `center_of_mass_overlay`, `force_vector_overlay`, and `contact_patch_closeup`. Reel #2 uses these APIs without embedding physics in the scene.

## Commands

Generate the transparent layered SVG:

```bash
python scripts/generate_assets.py
```

Render the large asset showcase preview:

```bash
bash scripts/render_showcase.sh
```

Render a low-quality reel preview:

```bash
bash scripts/render_reel.sh
```

Render typography and transition showcases:

```bash
bash scripts/render_showcases.sh
```

Render only the portrait typography showcase at 540×960/30 fps:

```bash
PYTHONPATH=src MOTO_MOTION_PREVIEW=1 ./.venv/bin/manim -ql src/moto_motion/scenes/typography_showcase.py TypographyShowcase
```

Render the candidate typeface comparison sheet:

```bash
bash scripts/render_font_comparison.sh
```

The comparison uses the same headline across Michroma, Saira, Oxanium, Chakra Petch, Exo 2, and Rajdhani. Titillium Web is included as a separate F1 technical/body sample. Candidate font files are local comparison inputs and are not part of the public SDK asset set. Production profiles remain unchanged until the comparison is reviewed.

For production 1080×1920/60 fps output, omit `MOTO_MOTION_PREVIEW=1` and use `-qh` or the project production render profile.

Render the complete reusable-component lab:

```bash
bash scripts/render_components.sh
```

The lab contains focused scenes for layout, trajectories, circuit geometry, F1/MotoGP vehicles, vehicle motion, camera behavior, typography, transitions, environment z-order, and choreography timelines. Render one module while iterating with:

```bash
manim -pql examples/component_showcase.py TypographyComponentShowcase
```

Render the premium 12–15 second showcase at 540×960/30 fps:

```bash
bash scripts/render_premium_preview.sh
```

Render all four themes or the adaptive-theme transition reel:

```bash
bash scripts/render_theme_preview.sh
bash scripts/render_adaptive_theme_reel.sh
```

Production renders use 1080×1920/60 fps. Preview scripts set `MOTO_MOTION_PREVIEW=1` for 540×960/30 fps. Manim produces H.264 MP4 output by default.

Render the final 1080×1920 animation:

```bash
bash scripts/render_final.sh
```

Synthesize a Kokoro narration bed from the timed manifest:

```bash
python -m pip install -e '.[tts]'
python scripts/narrate_manifest.py examples/braking_later_explainer.narration.json \
  --output-dir media/audio/braking_later_explainer
```

For new reels, derive scene timing from the measured narration instead of
fitting every sentence into prewritten scene windows:

```bash
python scripts/narrate_manifest.py examples/new_reel.narration.json \
  --timing-mode natural \
  --timing-output reel_005/scene_timing.audio_derived.json
```

Natural mode preserves each segment's generated pacing and inserts configurable
phrase pauses from the manifest's `synthesis` block. `--timing-mode fixed` is
available only for legacy manifests that intentionally own their timing.

Create a high-quality Instagram delivery file from a narrated reel. This renders
the scene at 2160×3840/60 fps, downsamples with Lanczos to 1080×1920, and writes
H.264 video plus normalized 48 kHz stereo AAC audio. Install `ffmpeg` and
`ffprobe` first; the script will not overwrite an existing export.

```bash
bash scripts/render_narrated_reel_hq.sh \
  examples/new_reel.py NewReel \
  media/audio/new_reel/narration.wav new-reel
```

Replace the example scene, class, narration path, and slug with those for each
new reel. The result is `media/exports/new-reel_instagram.mp4`; the supersampled
render master is retained under `media/masters/new-reel/`. The render takes
longer and uses more disk space than a preview. Use the regular 540×960/30 fps
preview workflow for creative iteration, and this path only for a final export.
Higher source quality protects fine details through transcoding; it cannot
guarantee additional reach or ranking on Instagram. Existing reels are not
rerendered by this workflow.

Run geometry tests:

```bash
python -m pytest
```

Render Reel #2, “How MotoGP Bikes Lean So Far Without Falling,” at 540×960/30 fps:

```bash
PYTHONPATH=src MOTO_MOTION_PREVIEW=1 ./.venv/bin/manim -ql --resolution 540,960 --frame_rate 30 examples/motogp_lean_explainer.py MotoGPLeanExplainer
```

Render production 1080×1920/60 fps:

```bash
PYTHONPATH=src ./.venv/bin/manim -qh --resolution 1080,1920 --frame_rate 60 examples/motogp_lean_explainer.py MotoGPLeanExplainer
```

The timed narration handoff is `examples/motogp_lean_explainer.narration.json`; it intentionally contains no synthesized audio.

The original racing-line demo remains available at `examples/racing_line_explainer.py`. The upgraded production demo is `examples/corner_exit_speed.py`; it uses illustrative speed values only and concludes with “THE EXIT MATTERS MORE.”

## Hybrid real-footage workflow

`moto_motion.video` is an opt-in, non-destructive FFmpeg layer for real clips in
hybrid productions. It probes MP4/MOV/WebM assets, creates reviewed 9:16 crops,
renders silent footage ready for the narration-first audio mixer, and maps
original-frame annotation points to delivered portrait pixels. Third-party
originals are deliberately Git-ignored. Keep reel-specific source mappings and
review notes in the local production workspace.

The reusable Kimi Antonelli character system is documented in
[docs/characters.md](docs/characters.md). Its source SVGs are registered under
`assets/characters/kimi_antonelli/`; render the review artifacts with
`bash scripts/render_character_previews.sh`.

Reusable sound-effect conventions and provenance are documented in
[docs/sfx.md](docs/sfx.md). The rider identity graphic conventions are in
[docs/creative/rider_identity_graphics.md](docs/creative/rider_identity_graphics.md).

## Asset provenance

Reusable asset registries and canonical asset documentation are kept under
`assets/` and the reusable portions of `docs/asset-integrations/`. Downloaded
source media, licensed archives, optional MotoGP raster and superbike packs,
the one-off `scripts/crop_motogp_sticker_grid.swift` preparation utility, and
reel-specific inspection notes remain local and are excluded from the public
repository.
