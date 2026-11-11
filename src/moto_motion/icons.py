"""Original motorsport iconography with consistent 64×64 vector geometry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .core.themes import DEFAULT_THEME, Theme

ICON_NAMES = (
    "brake_disc", "throttle", "apex", "drs_wing", "contact_patch",
    "lap_delta", "steering_angle", "slipstream", "lean_angle",
)

_GEOMETRY = {
    "brake_disc": '''<circle cx="32" cy="32" r="20"/><circle cx="32" cy="32" r="7"/><circle cx="32" cy="14" r="2"/><circle cx="48" cy="25" r="2"/><circle cx="42" cy="45" r="2"/><circle cx="22" cy="46" r="2"/><circle cx="16" cy="27" r="2"/><path d="M48 18h8v22h-8" class="secondary"/>''',
    "throttle": '''<path d="M15 48a22 22 0 0 1 34 0"/><path d="M32 46V22"/><path d="M25 23l7-9 7 9"/><path d="M19 43h26" class="secondary"/>''',
    "apex": '''<path d="M10 48C18 20 35 12 54 16"/><path d="M10 55C22 30 38 24 55 27" class="secondary"/><circle cx="36" cy="25" r="4"/>''',
    "drs_wing": '''<path d="M9 23h46l-5 10H14z"/><path d="M15 39h34" class="secondary"/><path d="M21 33v11M43 33v11"/>''',
    "contact_patch": '''<rect x="19" y="9" width="26" height="46" rx="11"/><path d="M24 17h16M23 27h18M23 37h18M24 47h16" class="secondary"/>''',
    "lap_delta": '''<path d="M12 32h40"/><path d="M32 12v40"/><path d="M20 22l12-10 12 10" class="secondary"/><path d="M20 42l12 10 12-10" class="secondary"/>''',
    "steering_angle": '''<circle cx="32" cy="34" r="20"/><circle cx="32" cy="34" r="5"/><path d="M15 25h34M32 34l15 13"/><path d="M17 13a24 24 0 0 1 30 0" class="secondary"/>''',
    "slipstream": '''<path d="M9 20c15-10 31-10 46 0M14 32c12-7 24-7 36 0M20 44c8-4 16-4 24 0"/><path d="M49 13l6 7-9 2" class="secondary"/>''',
    "lean_angle": '''<path d="M13 52h38"/><path d="M32 50l10-34"/><circle cx="43" cy="13" r="5"/><path d="M32 50A18 18 0 0 1 17 37" class="secondary"/><path d="M17 37l1 9 8-4" class="secondary"/>''',
}


@dataclass(frozen=True)
class IconState:
    progress: float = 0.0
    active: bool = False

    @property
    def normalized_progress(self) -> float:
        return max(0.0, min(1.0, self.progress))


def icon_svg(name: str, *, theme: Theme = DEFAULT_THEME, color: str | None = None, secondary: str | None = None) -> str:
    if name not in _GEOMETRY:
        raise KeyError(f"unknown motorsport icon: {name}")
    primary = color or theme.text
    accent = secondary or theme.accent
    geometry = _GEOMETRY[name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <g fill="none" stroke="{primary}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
    <style>.secondary{{stroke:{accent}}}</style>{geometry}
  </g>
</svg>'''


def write_icon_svgs(directory: str | Path, *, theme: Theme = DEFAULT_THEME) -> tuple[Path, ...]:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in ICON_NAMES:
        path = root / f"{name}.svg"
        path.write_text(icon_svg(name, theme=theme), encoding="utf-8")
        paths.append(path)
    return tuple(paths)


class MotorsportIcon:
    """Manim-compatible icon with restrained active/progress states."""

    def __init__(self, name: str, *, theme: Theme = DEFAULT_THEME, state: IconState = IconState(), asset_dir: str | Path = "assets/generated/icons"):
        try:
            from manim import SVGMobject
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("MotorsportIcon requires Manim") from exc
        path = Path(asset_dir) / f"{name}.svg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(icon_svg(name, theme=theme), encoding="utf-8")
        self.name = name
        self.state = state
        self.mobject = SVGMobject(str(path))
        self.apply_state(state)

    def apply_state(self, state: IconState):
        self.state = state
        self.mobject.set_opacity(1.0 if state.active else 0.72)
        scale = 1.0 + 0.08 * state.normalized_progress
        self.mobject.scale(scale)
        return self.mobject
