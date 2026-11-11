# Reusable driver characters

Driver characters are original RaceXplained editorial SVGs. They are not likeness approvals, official team art, or traced illustrations. The current registry contains Kimi Antonelli (`12`) and Max Verstappen (`3`); both use the same canvas, layer schema, anchors, and Manim adapter.

## Layout

```text
assets/characters/
├── registry.json
└── <driver_id>/
    ├── config.json
    ├── canonical.svg
    └── variants/
```

`canonical.svg` and every variant must preserve the same `512 × 512` view box and the following stable group IDs: `torso`, `neck`, `head`, `hair`, `eyes`, `eyebrows`, `nose`, `mouth`, `left_arm`, and `right_arm`. The SVGs remain the source of truth; the Manim adapter extracts those named groups to make them independently transformable.

Each driver also has a `number` layer backed by a real font (`Barlow Condensed` in the current registry) and a `facial_geometry` block describing face width, eye width/height/gap, eye centers, and hairstyle direction/volume/part. These values are part of the identity system; suit colour alone is not considered a character distinction. Max's current hairstyle is deliberately distinct from Kimi's: a high-volume, asymmetric, hard-left-parted swept quiff with an exposed forehead and clipped sides, rather than Kimi's separated wavy fringe. The silhouette was guided by a recent public Max portrait from [Formula1.com](https://www.formula1.com/en/drivers/max-verstappen), but the SVG is an original editorial drawing rather than a traced likeness.

## Add a driver

1. Copy the Kimi source directory and choose a lower-snake-case driver ID.
2. Keep the coordinate system, anchors, layer IDs, and layer order intact. Configure hair, skin, suit colours, number, and design notes in `config.json`.
3. Register the new config in `assets/characters/registry.json` with `status: available`.
4. Generate at least the five standard variants: `neutral`, `smiling`, `surprised`, `celebrating`, and `pointing`. They must derive from the same canonical geometry.
5. Run `bash scripts/render_character_previews.sh` and visually inspect the outputs under `media/characters/<driver_id>/`.

## Use in a Manim scene

```python
from moto_motion.renderers.manim import DriverCharacter

driver = DriverCharacter("kimi_antonelli", variant="neutral").scale(3)
self.add(driver)
self.play(driver.blink())
self.play(driver.open_eyes())
self.play(driver.change_expression("smiling"))
self.play(driver.celebrate())
```

`left_arm` and `right_arm` use the shoulder coordinates declared in the config. Keep those anchors accurate when changing a pose so arm animation pivots at a physically sensible place.
