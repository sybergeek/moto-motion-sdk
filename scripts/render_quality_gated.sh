#!/usr/bin/env bash
set -euo pipefail

# Future production renders should pass the exact revision and preview through
# the gate. Existing legacy scripts remain unchanged and can use their explicit
# legacy path without silently claiming CQG approval.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${MOTO_MOTION_APPROVAL_FILE:?Set MOTO_MOTION_APPROVAL_FILE to the CQG approval JSON}"
: "${MOTO_MOTION_REEL_ID:?Set MOTO_MOTION_REEL_ID}"
: "${MOTO_MOTION_REVISION_ID:?Set MOTO_MOTION_REVISION_ID}"
: "${MOTO_MOTION_PREVIEW_MANIFEST_ID:?Set MOTO_MOTION_PREVIEW_MANIFEST_ID}"

PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
  "$ROOT/.venv/bin/python" "$ROOT/scripts/creative_quality_gate.py" check-approval \
  --approval-file "$MOTO_MOTION_APPROVAL_FILE" \
  --reel-id "$MOTO_MOTION_REEL_ID" \
  --revision-id "$MOTO_MOTION_REVISION_ID" \
  --preview-manifest-id "$MOTO_MOTION_PREVIEW_MANIFEST_ID"

if [[ "$#" -eq 0 ]]; then
  echo "Usage: render_quality_gated.sh -- <existing render command> [args...]" >&2
  exit 64
fi
if [[ "$1" == "--" ]]; then shift; fi
exec "$@"

