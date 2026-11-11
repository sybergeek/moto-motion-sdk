# RaceXplained retention playbook

Version: 1.0 · 2026-11-07

This is a reusable planning and QA guide for Moto Motion / RaceXplained. It improves editorial consistency; it does not predict reach, completion rate or virality. Apply judgment, inspect the rendered frames and record what was learned.

For the optional follower-conversion layer, use [`follower_conversion_playbook.md`](./follower_conversion_playbook.md). It adds audience and return-value checks without replacing this retention or technical-accuracy gate.

## Core principles

1. **Visual-first hook.** Open on the most interesting action, contradiction or result. Avoid logo intros and generic greetings.
2. **Specific curiosity gap.** Ask one answerable question whose payoff the reel actually contains.
3. **Prediction challenge.** When the topic supports it, let the viewer choose an outcome before showing the mechanism.
4. **Early partial payoff.** Give the first useful fact early; do not withhold all value for the final seconds.
5. **Progressive revelation.** Introduce one mechanism, comparison or variable at a time.
6. **Visual proof.** Map every important claim to footage, a diagram, a calculation or a clearly labeled simulation.

## Production visual-legibility gate

Before a preview can be approved, review representative frames at mobile scale with the sound off.

- The primary subject must be identifiable on first appearance through a name, role or explicit label; do not expect viewers to decode anonymous icons or silhouettes.
- Historical comparisons must show named people and their compared measure in a readable rank or table format.
- Championship data must use a standings-style hierarchy: rank, rider, team and points.
- The opening frame must itself express the hook or question. A visually attractive but semantically unrelated shot is not a hook.
- Safe-area margins protect semantic overlays only. Backgrounds, footage and environmental geometry should fill the frame unless letterboxing is intentional and editorially justified.

Automated preflight can detect declared semantic omissions and camera/layout errors; it cannot judge cultural recognition or visual meaning reliably. A human sound-off review remains mandatory.
7. **Meaningful pattern interruption.** Use a freeze, crop, camera move, sound contrast or scene change when the story changes—not on an arbitrary timer.
8. **Cognitive simplicity.** Remove nonessential visual information. Keep labels close to the object they describe and avoid competing text treatments.
9. **Narration-first audio.** Narration remains intelligible; SFX mark meaningful events and may be suppressed when they compete with speech.
10. **Satisfying payoff.** Resolve the opening question and leave one memorable takeaway.

## Evidence boundaries

| Classification | What we may claim | Source / practice |
|---|---|---|
| Research-supported multimedia learning | Complementary visuals, signaling, segmenting, coherence/weeding and spatial contiguity can reduce extraneous load and support learning. | [Effective Educational Videos](https://pmc.ncbi.nlm.nih.gov/articles/PMC5132380/) and [Five Strategies for Optimizing Instructional Materials](https://pmc.ncbi.nlm.nih.gov/articles/PMC7940870/). These support instructional design principles, not Instagram virality. |
| Platform-published guidance | Use platform analytics to inspect dips, spikes, top moments and intro retention; compare similar-length videos where the platform supports it. | [YouTube audience retention guidance](https://support.google.com/youtube/answer/9314415). This is a measurement workflow, not evidence that a particular hook will win. |
| Platform-published guidance | Instagram’s Best Practices hub provides evolving, personalized advice on creation, engagement, reach, monetization and guidelines. | [Instagram Best Practices announcement](https://about.fb.com/news/2024/10/best-practices-education-hub-creators-instagram/). It does not establish fixed reel durations or formulas. |
| Editorial heuristic | Curiosity gaps, prediction challenges, short scene units and contrastive reveals are useful hypotheses for testing. | RaceXplained editorial practice; test against actual retention data. |
| RaceXplained-specific finding | A recurring hook, scene interval, SFX choice or visual treatment is a finding only after it is logged and compared in similar contexts. | [`reel_catalog.md`](./reel_catalog.md) and [`performance_log.schema.json`](./performance_log.schema.json). |

Never label an editorial heuristic as scientifically proven. Never infer causation from one successful reel.

## Editorial constraints

- Use 25–40 seconds as an initial range, not a hard rule.
- Estimate speaking time from word count and realistic delivery speed; do not compress narration unnaturally.
- Do not claim word-level synchronization until actual audio has been aligned.
- Do not invent timestamps, telemetry, creators, licenses or footage maneuvers.
- Keep Reel #2’s lean-physics topic distinct from Reel #4’s racing-line comparison.
- Preserve approved topics and narration through rendering.
- Keep every important piece of information visible, readable and synchronized with its explanation. Classify text and essential callouts as strict-safe; allow continuous tracks and backgrounds to extend beyond the safe area.

## Required approval gate

Before production, approve: topic novelty check, one hook concept, narrative structure, script, verified-facts list, visual-narration map, retention review and asset/license gaps. The renderer consumes approved manifests; it does not rewrite them.

## Future workflow

1. Check [`reel_catalog.md`](./reel_catalog.md) for duplication.
2. Identify the strongest verified visual or factual angle.
3. Draft three different hooks using [`hook_patterns.md`](./hook_patterns.md).
4. Select a structure from [`narrative_structures.md`](./narrative_structures.md).
5. Complete [`script_planning_template.md`](./script_planning_template.md).
6. Map each claim to a scene and visual proof.
7. Score and revise with [`script_review_rubric.md`](./script_review_rubric.md).
8. Validate facts, provenance and licensing.
9. Request editorial approval.
10. Pass approved manifests to the existing renderer, caption and SFX systems.
