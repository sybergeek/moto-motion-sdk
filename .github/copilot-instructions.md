# Moto Motion / RaceXplained Copilot Instructions

These instructions apply to all changes in this repository. They complement the repository-level [`AGENTS.md`](../AGENTS.md) guidance and the detailed documents under [`docs/creative/`](../docs/creative/).

## Project defaults

- Preserve existing reels, finalized characters, licensed source assets and approved narration.
- Reuse the existing Manim, FFmpeg, narration, caption, video-footage and SFX infrastructure before adding new abstractions or dependencies.
- Keep reusable SDK functionality in `src/moto_motion/`; keep one-off production work in the relevant `examples/`, `scripts/` or reel directory.
- Do not rebuild the animation engine, implement a replacement vehicle loader, or redesign approved assets unless the task explicitly requires it.
- Do not claim a render, synchronization, license, maneuver, physics result or visual review succeeded without validating the generated artifact.

## Editorial gate for reels

Before renderer work:

1. Read [`docs/creative/retention_playbook.md`](../docs/creative/retention_playbook.md) and the relevant templates.
2. Check topic novelty in [`docs/creative/reel_catalog.md`](../docs/creative/reel_catalog.md).
3. Define the hook, narrative structure, verified-facts list, script and visual-narration map.
4. Run the retention review and factual/provenance checks.
5. Obtain editorial approval. The renderer must consume approved narration and must not silently rewrite the topic or script.

For future reels, run the Creative Quality Gate before a full render: generate/select a hook variant, create the opening preview and first frame, run safe-area and visual-prominence checks, record human review notes, and approve the exact revision. See [`creative_quality_gate.md`](../docs/creative/creative_quality_gate.md). A bypass must be explicit and visible; it is for tests, debug rendering, legacy workflows or an explicit creator-approved exception only.

Every important claim needs visual proof. Every important piece of information must remain visible, readable and synchronized with its explanation. Prefer a clear curiosity gap, early partial payoff, progressive revelation and a decisive final takeaway over decorative motion.

### Audience-retention defaults

- Open with the most interesting action, contradiction or result; avoid logo-only or context-only intros.
- Establish one specific viewer question or prediction challenge early and resolve it visibly.
- Deliver a useful partial explanation before the final payoff; do not withhold all information until the end.
- Use progressive revelation: one mechanism, comparison or data point at a time.
- Pair each important spoken claim with visual proof, not merely decorative text.
- Never make the viewer decode an anonymous icon, abstract figure or unlabeled shape. A primary subject must have a clear on-screen name/role label at first appearance; a historical comparison should use a ranked, named comparison board.
- For motorsport rider identification, prefer a recognizable side-view motorcycle with rider or a team-colored, numbered helmet badge. Use top-view motorcycles for track geometry and racing-line explanations; do not use abstract bike/rider silhouettes as identity graphics.
- Present live championship data as a readable standings table (rank, rider, team and points), not disconnected decorative counters.
- Use meaningful pattern interruptions—freeze frames, motivated cuts, zooms or sound contrast—only when they clarify the story.
- Remove competing labels, repeated animations and unnecessary detail; optimize for mobile comprehension.
- Keep narration intelligible and use SFX/music to emphasize story beats rather than fill every pause.
- End by resolving the opening question with one memorable takeaway.
- Treat these as editorial defaults and testable hypotheses, not guarantees of reach or virality. Record observed performance separately in the creative performance log.

## Resolution-independent layout

Use [`moto_motion.core.safe_area`](../../src/moto_motion/core/safe_area.py) for new production scenes.

- Compose in normalized coordinates (`0.0..1.0`, top-left origin), never with hard-coded 1080×1920 positions.
- Convert through `LogicalCanvas`; do not scatter pixel-to-Manim formulas through scene code.
- Use `instagram_reels_v1` for the project safe-area profile and [`assets/layout/export_profiles.json`](../assets/layout/export_profiles.json) for export metadata.
- Treat the safe area as an overlay exclusion zone, not a global inset. Backgrounds, footage and environmental geometry remain full-bleed; only semantic content belongs inside the protected rectangle.
- Before production rendering, call `validate_camera_canvas` and `validate_scene_visual_contracts`. They catch camera mattes and missing declared subject/label/proof contracts; then conduct a human sound-off, mobile-size visual review.
- Classify every visual element:
  - `STRICT_SAFE`: titles, captions, statistics, equations, legends and essential callouts. Full bounds must stay inside the safe rectangle.
  - `SAFE_ANCHOR`: continuous tracks, trajectories, arrows and connectors may leave the frame, but registered semantic anchors must remain protected.
  - `FULL_BLEED`: backgrounds, footage, scenery and decorative environment may be cropped.
- Register meaningful animation samples and call `validate_scene_layout`. Treat strict-safe violations as production failures.
- Reserve a scene-specific caption lane before placing charts, rider cards or result labels. Register strict-safe semantic elements with `validate_element_collisions`; do not rely on the lower safe area being empty by accident.
- Keep the selected theme background persistent across scene transitions. Fade or transform foreground groups only—never reveal the renderer's default black canvas between beats.
- Use `make_safe_area_overlay` during layout review only; never include debug graphics in final exports.
- Pass `layout=canvas` to `RaceXplainedCaption` for new narration captions. Captions are always `STRICT_SAFE`.
- Render at least a production-size preview and a higher-resolution comparison when layout changes. Verify visually, not only through code.

## Typography and mobile readability

- Reuse the existing typography system and theme profiles.
- Keep display hierarchy, contrast and line wrapping consistent across resolutions.
- Add the reusable `RaceXplainedChapter` marker (`RACEXPLAINED · <chapter>`) at the top of each scene so every reel reads as a consistent series. Keep it subtle, inside the safe area, and change only the chapter label—not the visual theme or canvas between scenes.
- Include outlines, shadows and background padding in layout bounds.
- Wrap or shorten text before shrinking it below a readable size.
- Keep critical text away from platform UI zones; do not assume platform margins are universal guarantees.

## Animation and visual continuity

- Keep continuous paths continuous across scenes; do not redraw or teleport a track merely to fit a frame.
- Derive vehicle orientation from path tangents and derive speed/distance claims from the simulation.
- Keep explanatory overlays attached to the logical scene/crop transform so they remain aligned after reframing.
- Use deliberate camera motion and motivated transitions. Avoid random zooms, arbitrary shakes and decorative effects that compete with narration.
- Inspect contact sheets and representative frames for collisions, clipping, disconnected character parts, repeated re-entry animations and off-screen labels.

## Narration-first audio and SFX

- Narration is the highest audio priority, followed by essential synchronized SFX, flexible accents, decorative SFX and music.
- Use the existing `moto_motion.audio` scheduler, registry, speech detector and mixer.
- Enable narration-aware ducking for new reels unless the project explicitly opts out. Preserve essential timing; shift or suppress flexible/decorative cues when they compete with speech.
- Generate narration in natural mode first, measure each segment, and derive scene windows from the audio. Never force a sentence into a shorter target window with `atempo` merely to preserve a storyboard estimate; fixed timing is a legacy opt-in.
- Treat the generated `rendered.json` and audio-derived scene-timing manifest as the timing source for scene holds, captions and SFX events. Review the pacing before final render.
- Do not add an SFX merely because an object is visible. Map it to a meaningful animation or verified footage event.
- Preserve isolated narration, SFX and music stems when producing comparison or validation outputs.
- Never overwrite original recordings. Keep processing metadata and source/license provenance.

## Footage, assets and licensing

- Preserve source footage and models unchanged; create derived clips/renders separately.
- Record source URL, creator, exact license, download date, restrictions, attribution and derived paths in a local manifest.
- Do not identify stock footage, generic vehicles or generic engine audio as an authentic team, series, rider or power unit without evidence.
- Respect the repository ignore policy in [`.gitignore`](../.gitignore): licensed vehicle archives, user-supplied originals, processed motorsport audio and third-party footage are not public SDK assets by default.
- Do not add a dependency, downloaded asset or font solely for convenience when an existing project asset or system is sufficient.
- Twemoji SVGs are approved for restrained colorful accents such as trophies,
  flags, weather, celebration or CTA punctuation. Vendor only the specific
  assets used, record their source and attribution, and include Twemoji's
  CC BY 4.0 notice in the project's third-party notices. Do not use Twemoji
  as the primary car, driver, diagram or technical-illustration system.

## Validation and deliverables

For changes affecting rendering or audio:

1. Run focused unit tests while iterating.
2. Run the complete test suite before handoff.
3. Validate media with FFprobe where applicable.
4. Generate a preview/contact sheet and inspect it visually.
5. Report actual duration, resolution, frame rate, audio status, missing inputs, deviations and known limitations.

Use the existing test and render commands documented in [`README.md`](../README.md). Avoid committing generated `media/`, `renders/` or `dist/` output unless the task explicitly requests a tracked artifact.

## Change discipline

- Make the smallest cohesive change that satisfies the request.
- Keep public APIs typed and backward-compatible where practical.
- Add or update tests for new geometry, audio, layout, registry or validation behavior.
- Do not use destructive git/file operations to clean up unrelated work.
- If a requirement is ambiguous or requires new authority—such as a missing license, narration file, platform asset or approved editorial decision—stop and report the blocker instead of inventing it.
