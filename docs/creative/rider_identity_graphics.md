# Rider identity graphics

These reusable mockups are for future reels; they do not modify finalized
productions such as Reel #5.

## Use the right representation

- `MotoGPBike` remains the top-down representation for racing lines, track
  geometry, corner radius and strategy diagrams.
- `MotoGPBikeSide` is the side-view bike+rider token for braking posture,
  lean, acceleration, suspension and technique explanations.
- `RiderHelmetBadge` is the compact identity token for standings, comparisons
  and rider introductions after the name is established.

Always pair a new rider token with a readable name/number on first appearance.
Do not use anonymous abstract silhouettes for rider identity.

## Showcase

Render the future-design mockup with:

```bash
PYTHONPATH=src .venv/bin/manim -ql examples/showcases/rider_identity_showcase.py RiderIdentityShowcase
```

The source components are in
[`rider_identity.py`](../../src/moto_motion/renderers/manim/rider_identity.py).
