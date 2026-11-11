#!/usr/bin/env bash
# Render Kimi's review artifacts through the same Manim stack used by reels.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIM="$ROOT/.venv/bin/manim"
SOURCE="$ROOT/examples/character_system_showcase.py"
OUT="$ROOT/media/characters/kimi_antonelli"

if [[ ! -x "$MANIM" ]]; then
  echo "Expected project Manim at $MANIM" >&2
  exit 1
fi

mkdir -p "$OUT/previews" "$OUT/manim"

render_static() {
  local scene="$1"
  local slug="$2"
  "$MANIM" "$SOURCE" "$scene" --renderer=cairo --format=png --save_last_frame --transparent \
    --resolution 1024,1024 --media_dir "$OUT/manim" --output_file "$slug" --disable_caching
  local rendered
  rendered="$(find "$OUT/manim" -name "${slug}.png" -print -quit)"
  if [[ -z "$rendered" ]]; then
    echo "Could not locate PNG for $scene" >&2
    exit 1
  fi
  cp "$rendered" "$OUT/previews/${slug}.png"
}

render_static KimiNeutralPreview neutral
render_static KimiSmilingPreview smiling
render_static KimiSurprisedPreview surprised
render_static KimiCelebratingPreview celebrating
render_static KimiPointingPreview pointing

"$MANIM" "$SOURCE" KimiContactSheet --renderer=cairo --format=png --save_last_frame \
  --resolution 2048,1365 --media_dir "$OUT/manim" --output_file contact_sheet --disable_caching
CONTACT="$(find "$OUT/manim" -name 'contact_sheet.png' -print -quit)"
[[ -n "$CONTACT" ]] && cp "$CONTACT" "$OUT/contact_sheet.png"

"$MANIM" "$SOURCE" KimiCharacterAnimationTest --renderer=cairo --resolution 1080,1920 \
  --frame_rate 60 --media_dir "$OUT/manim" --output_file animation_test --disable_caching
ANIMATION="$(find "$OUT/manim" -name 'animation_test.mp4' -print -quit)"
[[ -n "$ANIMATION" ]] && cp "$ANIMATION" "$OUT/animation_test.mp4"

echo "Rendered previews: $OUT/previews"
echo "Contact sheet: $OUT/contact_sheet.png"
echo "Animation test: $OUT/animation_test.mp4"
