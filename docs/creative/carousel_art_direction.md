# RaceXplained carousel art-direction defaults

This document records the production lessons from the Verstappen São Paulo
carousel and the Mercedes ninth-title carousel. These are default decisions
for future carousels, not optional cleanup after export.

## Start with the visual story

Before writing a manifest or renderer branch, decide what the viewer should
notice first on every slide:

- one dominant subject or statistic;
- one supporting explanation;
- one intentional visual relationship between them.

Do not fill a slide with components simply because the manifest has room for
them. A slide should look like an editorial page, not a collection of widgets.

## Prefer real, image-led visuals

Use owned, licensed, or verified reference photography whenever it improves
authenticity. Prefer the same photographic treatment across related slides.
Use generated silhouettes or generic vector cars only when a real asset is not
available or when the graphic itself is the explanation.

For an image-led slide:

1. Crop the image deliberately for the portrait canvas.
2. Keep faces, cars, helmets, and key objects visible.
3. Apply tonal treatment to the actual crop.
4. Place text in a designed region that supports the image.
5. Inspect the result at phone size.

Do not use an image as faint wallpaper behind a large opaque card. The image
should remain legible enough to contribute meaning and atmosphere.

## Use translucent panels, not accidental obstructions

Text over photography must use a local translucent panel, gradient, shadow,
or carefully selected tonal region. Default to translucency when the image
contains an important face or subject.

The default light-theme treatment is:

- a dark editorial title band with visible image detail where possible;
- a dark translucent information panel over the lower image;
- high-contrast text with a subtle stroke only when the crop requires it;
- no large opaque ivory rectangles covering faces or cars.

Opacity is a design variable, not a substitute for checking contrast. Adjust
the panel and the crop together. If a face disappears, reduce opacity or move
the text zone; do not simply darken the entire slide.

## Establish a slide system before varying layouts

Related slides must share brand-bar height, title size and weight, safe margins,
footer treatment, panel geometry, and image-crop conventions. Variation should
come from the story, not arbitrary changes in title placement, font scale, or
whether a slide happens to have a graphic.

The Verstappen carousel demonstrated that related evidence slides work best as
one system: consistent title treatment and a shared start-to-finish visual
grammar, with only the content changing.

## Protect the semantic hierarchy

Every slide should have one primary focal point. Keep supporting labels close
to the thing they identify:

- position labels beside the relevant driver or result;
- keep arrows and start-to-finish lines clear of position indicators;
- do not allow annotation lines to pass through text or badges;
- keep captions, titles, and diagrams in separate vertical lanes;
- keep the CTA in its own deliberate closing region.

Do not use a panel to hide a collision. Resize, move, or recompose the
elements, then render again.

## Typography and contrast defaults

- Avoid thin display text over detailed photography.
- Use bold or medium weights for cover hooks, key numbers, and final CTAs.
- Check the actual rendered crop, not the nominal background color.
- Keep line breaks intentional; never let a single word wrap accidentally.
- Keep text inside the safe region and inside its supporting panel.
- Use one emphasis color per concept, plus established team colors for team
  comparisons.
- For ranking slides, use recognizable constructor colors for labels, bars, and
  title counts, darkened enough for contrast on the light theme.

If a line is difficult to read at mobile size, fix the composition first. Do
not solve every issue with a heavy outline or shadow.

## Authenticity and factual graphics

- Prefer verified team/driver photography and approved assets.
- Do not use placeholder boxes where recognizable cars, people, or team marks
  are part of the story.
- A simplified diagram must explain a real relationship; it must not imply
  fabricated telemetry, standings, or mechanical detail.
- Use native vector symbols for core trophies, diagrams, and technical icons.
  Twemoji SVGs are allowed for restrained colorful accents such as a trophy,
  flag, weather, celebration, or CTA punctuation. Vendor only the specific
  assets used and record the required CC BY 4.0 attribution. Do not let emoji
  become the primary car, driver, ranking, or technical-illustration system.

## Covers and CTA slides

The cover needs an immediate hook, one dominant visual, and a clear reason to
swipe. Avoid spending the opening area on decorative branding.

A final CTA slide should be purposeful, not empty padding. Keep the CTA concise,
centered or strongly aligned, and readable against its background. Put it in a
dedicated translucent/dark footer or clean closing field when the image is busy.

## Mandatory visual QA

Rendering success is not creative approval. For every carousel:

1. Render all slides at full resolution.
2. Inspect the contact sheet for continuity.
3. Inspect every slide individually at mobile scale.
4. Inspect image crops for hidden faces, clipped cars, and accidental focal points.
5. Check text contrast over the actual image.
6. Check every connector, badge, label, and panel for collisions.
7. Inspect the first and final slides separately.
8. Correct the composition and rerender before export.

The quality report catches measurable technical failures, but it cannot fully
judge photographic contrast, authenticity, hierarchy, or whether a slide looks
professionally art-directed. Those remain explicit review steps.

## Default checklist for future manifests

Before rendering, confirm:

- the light editorial theme is used unless a darker treatment is justified;
- each image-backed slide declares a real asset and source;
- title and panel geometry match related slides;
- important faces and subjects remain visible after overlays;
- panels are translucent where they overlap meaningful imagery;
- no placeholder car or box is used for a primary story element;
- team colors are intentional and contrast-checked;
- slide numbering and brand bars are single, consistent treatments;
- the CTA has its own safe, readable region;
- contact-sheet and mobile review are part of the render workflow.

