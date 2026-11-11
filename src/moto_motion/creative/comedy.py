"""Reusable, reviewable comedy beats for editorial motorsport reels.

These are timing/storyboard contracts, not audience-performance predictions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ComedyTechnique(StrEnum):
    DEADPAN_PAUSE = "deadpan_pause"
    VISUAL_CONTRADICTION = "visual_contradiction"
    DELAYED_REVEAL = "delayed_reveal"
    CALLBACK = "callback"
    UNDERSTATEMENT = "understatement"
    ESCALATION = "escalation"


@dataclass(frozen=True)
class ComedyBeat:
    technique: ComedyTechnique
    pause_ms: int = 0
    visual_payoff: str | None = None
    sfx: str | None = None

    def __post_init__(self) -> None:
        if self.pause_ms < 0:
            raise ValueError("pause_ms cannot be negative")
        if self.technique is ComedyTechnique.DEADPAN_PAUSE and self.pause_ms == 0:
            raise ValueError("deadpan_pause requires a non-zero pause_ms")

    def to_dict(self) -> dict[str, object]:
        return {
            "technique": self.technique.value,
            "pause_ms": self.pause_ms,
            "visual_payoff": self.visual_payoff,
            "sfx": self.sfx,
        }
