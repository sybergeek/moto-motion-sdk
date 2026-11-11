"""Meaningfully different opening concepts without claiming a predicted winner."""

from __future__ import annotations

from collections.abc import Sequence

from .models import HookType, HookVariant


_HOOK_BLUEPRINTS = (
    (HookType.VISUAL_MYSTERY, "Open on the decisive visual detail before naming the mechanism.", "What is the viewer seeing, and why does it behave that way?", "Begin with a tight, labeled detail and reveal the full context after the first motion.", "the detail moves or changes state"),
    (HookType.PREDICTION_CHALLENGE, "Ask the audience to choose between two visible outcomes.", "Which outcome would you predict before the explanation?", "Place two clearly labeled outcomes on screen, then animate the real comparison.", "the two outcomes separate or resolve"),
    (HookType.TECHNICAL_DEMONSTRATION, "Show the physical or strategic mechanism immediately.", "What variable makes this racing decision work?", "Animate one controlled variable against a stable reference before adding context.", "the measured variable changes"),
    (HookType.HISTORICAL_SURPRISE, "Lead with a named record, contrast or reversal that needs context.", "Why is the familiar story incomplete?", "Show the named comparison first, then introduce the missing historical context.", "the comparison rank changes"),
    (HookType.UNEXPECTED_RESULT, "Start with the result that conflicts with the audience's expectation.", "How can that result be possible?", "Show the result and one proof cue before explaining the mechanism.", "the proof cue appears"),
    (HookType.RACING_COMPARISON, "Put two racing lines, riders or decisions side by side from frame one.", "Which choice is faster, safer or more effective—and why?", "Use a synchronized side-by-side comparison with one shared metric.", "the shared metric resolves"),
    (HookType.CHAMPIONSHIP_STAKES, "Open with the live consequence of a championship calculation.", "What changes if this result holds?", "Show the named standings consequence before the explanatory calculation.", "the standings delta updates"),
)

_NARRATION_FRAMES = {
    HookType.VISUAL_MYSTERY: "This detail decides the story in {topic}—but why?",
    HookType.PREDICTION_CHALLENGE: "Before we explain {topic}, which outcome would you predict: {question}",
    HookType.TECHNICAL_DEMONSTRATION: "Watch the variable that changes {topic}: {question}",
    HookType.HISTORICAL_SURPRISE: "The familiar version of {topic} leaves out one twist—{question}",
    HookType.UNEXPECTED_RESULT: "The result in {topic} looks backwards: {question}",
    HookType.RACING_COMPARISON: "Two choices collide in {topic}: {question}",
    HookType.CHAMPIONSHIP_STAKES: "One consequence changes the stakes in {topic}: {question}",
}


def generate_hook_variants(
    *,
    topic: str,
    core_question: str,
    audience: str,
    verified_claims: Sequence[str] = (),
    required_assets: Sequence[str] = (),
    count: int = 3,
) -> tuple[HookVariant, ...]:
    """Generate planning alternatives; the creator still chooses and verifies one."""
    if count < 1:
        raise ValueError("count must be positive")
    if not topic.strip() or not core_question.strip() or not audience.strip():
        raise ValueError("topic, core_question and audience are required")
    variants = []
    for index, (hook_type, framing, gap, visual, event) in enumerate(_HOOK_BLUEPRINTS[:count], start=1):
        variants.append(HookVariant(
            variant_id=f"hook_{index:02d}",
            hook_type=hook_type,
            narration_text=_NARRATION_FRAMES[hook_type].format(topic=topic, question=core_question),
            opening_visual_concept=f"{visual} Audience: {audience}.",
            intended_curiosity_gap=gap,
            first_meaningful_visual_event=event,
            approximate_duration_seconds=3.0,
            required_assets=tuple(required_assets),
            factual_claims_requiring_verification=tuple(verified_claims),
            clarity_risks=(framing,),
            retention_risks=("Review whether the opening delivers an early useful fact instead of withholding the answer.",),
        ))
    return tuple(variants)

