"""Timeline-safe SFX event mapping and scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class SoundMode(StrEnum):
    OFF = "off"
    AUTO = "auto"
    MANUAL = "manual"
    HYBRID = "hybrid"


class SFXPriority(StrEnum):
    ESSENTIAL = "essential"
    FLEXIBLE = "flexible"
    DECORATIVE = "decorative"


DEFAULT_EVENT_MAP = {
    "text.pop": "ui.pop.soft",
    "text.reveal": "ui.reveal.positive",
    "object.slide": "ui.whoosh.short",
    "object.impact": "ui.impact.soft",
    "number.tick": "ui.counter.tick",
    "number.lock": "ui.counter.complete",
    "character.enter": "ui.character.entrance",
    "character.celebrate": "ui.celebration.accent",
    "comparison.resolve": "ui.reveal.positive",
    "vehicle.flyby": "motorsport.generic.vehicle_pass.fast",
    "vehicle.accelerate": "motorsport.generic.vehicle_pass.race",
    "vehicle.brake": "ui.impact.soft",
    "vehicle.gearshift": "ui.click.mechanical",
    "vehicle.kerb_contact": "ui.impact.soft",
    "trophy.reveal": "ui.trophy.reveal",
}

DEFAULT_EVENT_PRIORITIES = {
    "vehicle.flyby": SFXPriority.ESSENTIAL,
    "vehicle.accelerate": SFXPriority.ESSENTIAL,
    "vehicle.brake": SFXPriority.ESSENTIAL,
    "vehicle.gearshift": SFXPriority.ESSENTIAL,
    "vehicle.kerb_contact": SFXPriority.ESSENTIAL,
    "object.impact": SFXPriority.FLEXIBLE,
    "text.pop": SFXPriority.FLEXIBLE,
    "text.reveal": SFXPriority.FLEXIBLE,
    "object.slide": SFXPriority.FLEXIBLE,
    "character.enter": SFXPriority.FLEXIBLE,
    "character.celebrate": SFXPriority.FLEXIBLE,
    "comparison.resolve": SFXPriority.FLEXIBLE,
    "trophy.reveal": SFXPriority.FLEXIBLE,
    "number.tick": SFXPriority.DECORATIVE,
    "number.lock": SFXPriority.FLEXIBLE,
}


@dataclass(frozen=True)
class SFXCue:
    sfx_id: str
    at: float
    gain_db: float = -12.0
    fade_in: float = 0.01
    fade_out: float = 0.04
    pan: float = 0.0
    speed: float = 1.0
    event: str | None = None
    intensity: float = 1.0
    closest_approach_time: float | None = None
    priority: SFXPriority = SFXPriority.FLEXIBLE
    shift_tolerance: float = 0.15


class SFXScheduler:
    """Maps meaningful animation events to bounded, deterministic SFX cues."""

    def __init__(self, mode: SoundMode | str = SoundMode.HYBRID, *, cooldown_seconds: float = 0.12):
        self.mode = SoundMode(mode)
        self.cooldown_seconds = cooldown_seconds
        self.cues: list[SFXCue] = []
        self._last_by_event: dict[str, float] = {}

    def play(self, sfx_id: str, *, at: float, **kwargs: Any) -> SFXCue | None:
        if self.mode == SoundMode.OFF:
            return None
        cue = SFXCue(sfx_id=sfx_id, at=at, **kwargs)
        self.cues.append(cue)
        return cue

    def emit(self, event: str, *, at: float, intensity: float = 1.0, override: str | None = None, **kwargs: Any) -> SFXCue | None:
        if self.mode in {SoundMode.OFF, SoundMode.MANUAL}:
            return None
        if event not in DEFAULT_EVENT_MAP and override is None:
            return None
        last = self._last_by_event.get(event)
        if last is not None and at - last < self.cooldown_seconds:
            return None
        self._last_by_event[event] = at
        gain = float(kwargs.pop("gain_db", -16 + 8 * max(0.0, min(1.0, intensity))))
        priority = kwargs.pop("priority", DEFAULT_EVENT_PRIORITIES.get(event, SFXPriority.FLEXIBLE))
        return self.play(override or DEFAULT_EVENT_MAP[event], at=at, gain_db=gain, event=event, intensity=intensity, priority=SFXPriority(priority), **kwargs)

    def counter(self, *, start: float, duration: float, ticks: int = 6) -> list[SFXCue]:
        """Emit a bounded tick sequence plus one completion lock."""
        if self.mode in {SoundMode.OFF, SoundMode.MANUAL}:
            return []
        ticks = max(1, min(8, ticks))
        emitted = []
        for index in range(ticks):
            cue = self.play(DEFAULT_EVENT_MAP["number.tick"], at=start + duration * index / (ticks + 1), gain_db=-13.2, event="number.tick", intensity=0.35, priority=SFXPriority.DECORATIVE)
            if cue:
                emitted.append(cue)
        cue = self.play(DEFAULT_EVENT_MAP["number.lock"], at=start + duration, gain_db=-10.4, event="number.lock", intensity=0.7, priority=SFXPriority.FLEXIBLE)
        if cue:
            emitted.append(cue)
        return emitted
