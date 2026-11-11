"""Original vector assets shipped with the SDK."""

from __future__ import annotations

from pathlib import Path

from .core.constants import CYAN, RED


def f1_car_svg(primary: str = CYAN, secondary: str = RED, outline: str = "#F4F6F8") -> str:
    """Return a symmetric, top-down open-wheel car SVG centered on (0, 0).

    The car points toward positive Y. Groups are intentionally named so renderers
    can recolor or animate major visual layers independently.
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2.7 -5.5 5.4 11" width="540" height="1100">
  <defs>
    <linearGradient id="body" x1="0" x2="1" y1="0" y2="1"><stop stop-color="{primary}"/><stop offset="1" stop-color="{secondary}"/></linearGradient>
    <linearGradient id="carbon" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#536174"/><stop offset="1" stop-color="#141b29"/></linearGradient>
    <filter id="shadow"><feGaussianBlur stdDeviation="0.13"/></filter>
  </defs>
  <g id="shadow-layer" opacity=".5" filter="url(#shadow)" transform="translate(0 .16)"><path d="M0-5.05 C.55-4.55 .72-3.5 .75-2.2 L1.65-1.45 .92-.45 .7 1.65 2.2 2.25 1.75 2.85 .7 2.65 .48 4.35 .2 5.15 H-.2 L-.48 4.35-.7 2.65-1.75 2.85-2.2 2.25-.7 1.65-.92-.45-1.65-1.45-.75-2.2C-.72-3.5-.55-4.55 0-5.05Z" fill="#05080d"/></g>
  <g id="tyres" fill="#0a0d13" stroke="#697386" stroke-width=".1">
    <!-- Front wheels are 1.64 units nose-forward; rear wheels use a
         milder 0.54-unit offset. Front widths are 1.2x thicker; rear widths
         are 1.44x the original, and each pair is
         20% closer together by moving both wheels 10% toward the centerline. -->
    <rect x="-1.936" y="-3.40" width=".816" height="1.55" rx=".27"/><rect x="1.120" y="-3.40" width=".816" height="1.55" rx=".27"/>
    <rect x="-1.968" y="1.75" width="1.008" height="1.72" rx=".28"/><rect x=".960" y="1.75" width="1.008" height="1.72" rx=".28"/>
  </g>
  <g id="wings" fill="url(#carbon)" stroke="#9aa5b5" stroke-width=".08">
    <path d="M-1.7-4.55 Q0-5.3 1.7-4.55 L2.25-4.25 1.95-3.84 Q0-4.15-1.95-3.84L-2.25-4.25Z"/>
    <path d="M-2.1 3.8 Q0 3.45 2.1 3.8 L2.45 4.28 Q0 4.05-2.45 4.28Z"/>
    <path d="M-2.25 4.55 H2.25 L2.05 4.78 H-2.05Z"/>
  </g>
  <g id="suspension-arms" fill="none" stroke="#B4C0CF" stroke-width=".075" opacity=".9">
    <path d="M-1.7-2.11-0.55-1.01 M1.7-2.11.55-1.01 M-1.7 2.79-.62 1.54 M1.7 2.79.62 1.54"/>
    <path d="M-1.55-1.56-.52-.76 M1.55-1.56.52-.76 M-1.5 2.34-.55 1.39 M1.5 2.34.55 1.39"/>
  </g>
  <g id="sidepods" fill="{secondary}" stroke="{outline}" stroke-width=".07">
    <path d="M-1.35-1.45 Q-1.75-.8-1.35.15 L-.82.48-.62-.45-.8-1.55Z"/><path d="M1.35-1.45 Q1.75-.8 1.35.15 L.82.48.62-.45.8-1.55Z"/>
    <path d="M-.87-.9-.58-.7-.52.7-.83.95 Q-1.02 0-.87-.9Z" fill="#0F1826"/><path d="M.87-.9.58-.7.52.7.83.95 Q1.02 0 .87-.9Z" fill="#0F1826"/>
  </g>
  <g id="engine-cover" fill="{primary}" stroke="{outline}" stroke-width=".08">
    <path d="M0-3.85 Q.62-3.3 .68-1.3 L.52.62 .37 1.62 H-.37L-.52.62-.68-1.3Q-.62-3.3 0-3.85Z"/>
    <path d="M-.35-2.95 Q0-3.25 .35-2.95 L.28-1.25 H-.28Z" fill="#1B2A3F" stroke="none"/>
  </g>
  <g id="cockpit" fill="#07101C" stroke="#C5D3E2" stroke-width=".09">
    <ellipse cy="-.65" rx=".47" ry=".83"/><path d="M0-1.42 L0-0.02 M-.37-.68H.37" stroke="#F5C451" stroke-width=".08"/>
  </g>
  <g id="halo" fill="none" stroke="#E3EAF3" stroke-width=".13"><path d="M-.55-.3 Q0-1.58 .55-.3 M-.55-.3H.55 M0-1.48V-.3"/></g>
  <g id="nose-cone" fill="{primary}" stroke="{outline}" stroke-width=".08"><path d="M-.42-.05 Q0 .38 .42-.05 L.23 2.18 Q0 2.65-.23 2.18Z"/><path d="M-.18.55H.18" stroke="{outline}" opacity=".65"/></g>
  <g id="highlights" fill="none" stroke="#FFFFFF" stroke-width=".06" opacity=".62"><path d="M-.32-3.6Q-.5-2.2-.38-1.2"/><path d="M.85-1.2Q1.2-.5 1.0.25"/></g>
</svg>'''


def write_f1_car_svg(path: str | Path, primary: str = CYAN, secondary: str = RED, outline: str = "#F4F6F8") -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(f1_car_svg(primary, secondary, outline), encoding="utf-8")
    return destination
