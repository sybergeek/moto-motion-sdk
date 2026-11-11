# Repository structure

The repository has two boundaries: a public SDK boundary and a local
production boundary. New reusable code belongs in the public areas below;
reel-specific work, downloaded media, generated output, and inspection caches
belong in ignored local areas.

```text
src/moto_motion/          Public Python package
  core/                   Shared constants, layouts, themes, safe areas
  models/                 Renderer-neutral domain models
  geometry/               Trajectories and spatial math
  effects/                Motion and easing primitives
  renderers/              Manim and other rendering adapters
  scenes/                 Reusable portrait scenes
  carousel/               Carousel models, rendering, and quality checks
  audio/                  Narration, SFX, and audio scheduling
  creative/               Editorial planning and conversion helpers
  creative_quality/       Hook, preview, approval, and quality-gate logic
  video/                  Optional real-footage and FFmpeg helpers

tests/                    Public automated tests, grouped by package concern
examples/                 Curated public reference implementations
  explainers/             Educational F1 and MotoGP scenes
  showcases/              Component, theme, typography, and identity demos
  creative/               Creative quality and conversion demonstrations
  audio/                  Audio/SFX demonstrations
  local/                  Ignored reel and carousel production material

scripts/                  Reusable developer and rendering utilities
assets/                   Reusable source assets and registries
docs/                     Public API, asset, and creative guidance

reel_*/                  Ignored local reel workspaces
media/                    Ignored generated media, previews, and exports
output/                   Ignored generated packages and render output
data/                     Ignored private analytics and production data
.asset-inspection/        Ignored local inspection projects and caches
```

## Placement rules

- Add reusable runtime behavior to the smallest appropriate package under
  `src/moto_motion/`, with a focused test under `tests/`.
- Add a reusable visual or API demonstration to the matching `examples/`
  category. Keep narration, factual research, source mappings, and production
  manifests in the local production workspace.
- Add reusable command-line or rendering helpers to `scripts/`. One-off reel
  helpers and asset-preparation utilities stay local and ignored.
- Add stable user-facing guidance to `docs/`. Do not add downloaded media,
  licensed archives, inspection reports, or reel-specific review notes to the
  public documentation tree.
- Keep generated files out of source, examples, tests, and docs. Use `media/`
  for generated media and `output/` for generated packages.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution and provenance
rules, and [README.md](../README.md) for setup and public usage examples.
