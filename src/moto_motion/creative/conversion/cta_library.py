"""Approved CTA strategy metadata; wording remains editorially reviewable."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CTAStrategy:
    strategy_id: str
    name: str
    intended_objective: str
    suitable_categories: tuple[str, ...]
    recommended_placement: str
    suggested_duration_seconds: tuple[float, float] | None
    example_wording: str | None
    retention_risks: tuple[str, ...]
    validation_rules: tuple[str, ...]


CTA_STRATEGIES = {
    item.strategy_id: item
    for item in (
        CTAStrategy("none", "No explicit CTA", "protect_payoff", ("all",), "none", None, None, ("missed return cue",), ("must not require text",)),
        CTAStrategy("subtle_visual", "Subtle visual CTA", "brand_recognition", ("all",), "closing_beat", (1.0, 2.0), "More F1 & MotoGP explained → RaceXplained", ("competes with captions",), ("visual delivery needs no narration",)),
        CTAStrategy("direct_follow", "Direct follow CTA", "gain_relevant_followers", ("all",), "after_payoff", (1.0, 2.0), "Follow RaceXplained for more racing breakdowns.", ("generic wording", "extends the ending"), ("must follow payoff",)),
        CTAStrategy("next_episode", "Next-episode CTA", "recurring_series", ("series",), "after_payoff", (1.0, 2.0), "Next: why MotoGP riders trail brake.", ("unsupported promise", "cliffhanger pressure"), ("requires planned content reference",)),
        CTAStrategy("series", "Series CTA", "recurring_series", ("series",), "closing_beat", (1.0, 2.0), "RaceXplained: The Science — more racing physics coming.", ("overlong series intro",), ("requires known series",)),
        CTAStrategy("related_reel", "Related-reel CTA", "related_reel", ("all",), "closing_beat", (1.0, 2.0), "We've also explained why the shortest racing line isn't always fastest.", ("invented related content",), ("requires published reel reference",)),
        CTAStrategy("profile_discovery", "Profile-discovery CTA", "profile_discovery", ("all",), "closing_beat", (1.0, 2.0), "Explore more racing breakdowns on RaceXplained.", ("generic profile prompt",), ("must not invent profile features",)),
    )
}


def get_cta_strategy(strategy_id: str) -> CTAStrategy:
    try:
        return CTA_STRATEGIES[strategy_id]
    except KeyError as exc:
        raise ValueError(f"unknown CTA strategy: {strategy_id}") from exc

