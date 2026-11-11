"""Reusable deterministic scene timelines and motion presets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .effects.motion import smoothstep


@dataclass(frozen=True)
class TimelineEvent:
    name: str
    start: float
    duration: float
    action: Callable[[float], Any] | None = None
    tag: str = "motion"

    def active(self, time: float) -> bool:
        return self.start <= time <= self.start + self.duration

    def progress(self, time: float) -> float:
        return 1.0 if self.duration == 0 else smoothstep((time - self.start) / self.duration)


class SceneDirector:
    """Composes existing animation primitives on a deterministic timeline."""

    def __init__(self):
        self.events: list[TimelineEvent] = []

    def schedule(self, name: str, start: float, duration: float, action=None, *, tag: str = "motion") -> TimelineEvent:
        event = TimelineEvent(name, start, duration, action, tag)
        self.events.append(event)
        return event

    def preset(self, name: str, start: float, duration: float, action=None) -> TimelineEvent:
        if name not in {"accelerate", "brake", "approach_corner", "enter_corner", "exit_corner", "reveal_technical_detail"}:
            raise ValueError(f"unknown motion preset: {name}")
        return self.schedule(name, start, duration, action, tag="preset")

    def events_at(self, time: float) -> tuple[TimelineEvent, ...]:
        return tuple(event for event in self.events if event.active(time))

    def validate(self) -> None:
        if any(event.duration < 0 or event.start < 0 for event in self.events):
            raise ValueError("timeline events must have non-negative start and duration")


@dataclass
class DirectionalMotionContract:
    """Small contract used by scenes to preserve focal direction and clarity."""

    vehicle_leads_camera: bool = True
    text_obscures_vehicle: bool = False
    transition_motivated: bool = True
    selective_motion_blur: bool = True
