"""Explicit bridge from verified footage actions to the opt-in SFX scheduler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from moto_motion.audio import SFXCue, SFXScheduler

FootageAction = Literal["accelerate", "flyby", "brake", "gearshift", "kerb_contact"]

ACTION_TO_SFX_EVENT: dict[FootageAction, str] = {
    "accelerate": "vehicle.accelerate",
    "flyby": "vehicle.flyby",
    "brake": "vehicle.brake",
    "gearshift": "vehicle.gearshift",
    "kerb_contact": "vehicle.kerb_contact",
}


@dataclass(frozen=True)
class VerifiedFootageAction:
    """An action established by human frame/audio review, never inference."""

    action: FootageAction
    at: float
    confidence: Literal["high", "medium"]
    source_audio_retained: bool = False
    closest_approach_time: float | None = None


def emit_verified_footage_sfx(scheduler: SFXScheduler, action: VerifiedFootageAction, *, intensity: float = 0.7, pan: float = 0.0) -> SFXCue | None:
    """Schedule a compatible SFX cue after an editor has verified the action.

    This does not synthesize, infer, or label a mechanical action from visual
    footage.  The existing narration-first mixer subsequently decides whether a
    flexible cue is ducked, shifted, or suppressed; essential vehicle actions
    remain visually synchronized.
    """
    if action.at < 0:
        raise ValueError("footage action time must be non-negative")
    return scheduler.emit(
        ACTION_TO_SFX_EVENT[action.action],
        at=action.at,
        intensity=intensity,
        pan=pan,
        closest_approach_time=action.closest_approach_time,
    )
