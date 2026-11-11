# Contributing to Moto Motion

Moto Motion is a reusable Python SDK for RaceXplained motorsport explainers.
Contributions should improve reusable code, documented contracts, generic
examples, tests, or approved SDK assets.

## Repository boundary

Keep reel-specific production work local. Do not add:

- `reel_*` production directories;
- downloaded event photography, raw footage, or source audio;
- generated `media/`, `output/`, `renders/`, or `.tmp/` artifacts;
- private analytics observations;
- one-off asset experiments or candidate-font comparisons.

The repository `.gitignore` is intentionally configured around this boundary.
If a production lesson is reusable, generalize it into `src/`, `tests/`,
`docs/creative/`, or a generic example instead of committing the production
directory that produced it.

## Development setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

Run the full test suite before submitting changes:

```bash
PYTHONPATH=src python -m pytest -q
```

## Code and asset changes

- Keep reusable SDK behavior under `src/moto_motion/`.
- Add focused tests under `tests/` for new public behavior.
- Keep examples generic and reproducible; do not reference private reel paths
  or ignored downloaded assets.
- Preserve normalized layout, safe-area, and theme conventions.
- Record asset source, license, attribution, and restrictions before adding a
  third-party asset.
- Run a rendered visual review for changes affecting composition, typography,
  layout, captions, or audio.
- Do not commit generated output unless a task explicitly requests a tracked
  fixture and the fixture is small, deterministic, and documented.

## Pull requests

Describe the reusable behavior changed, tests run, visual artifacts inspected,
and any licensing or provenance considerations. Keep reel-specific context in
the local production workspace unless it has been converted into reusable
documentation.
