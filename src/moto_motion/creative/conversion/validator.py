"""Editorial and timeline checks for conversion decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .cta_library import get_cta_strategy
from .models import ConversionPlan, PlannedContent, SeriesMetadata


@dataclass(frozen=True)
class ConversionIssue:
    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class ConversionReview:
    issues: tuple[ConversionIssue, ...]

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def review_conversion(
    plan: ConversionPlan | None,
    *,
    series: Mapping[str, SeriesMetadata] = {},
    planned_content: Mapping[str, PlannedContent] = {},
    published_reels: frozenset[str] = frozenset(),
    payoff_end_seconds: float | None = None,
    reel_duration_seconds: float | None = None,
) -> ConversionReview:
    if plan is None:
        return ConversionReview(())
    issues: list[ConversionIssue] = []
    if not plan.target_audience:
        issues.append(ConversionIssue("missing_audience", "target_audience is required for a conversion-aware plan"))
    if not plan.reason_to_follow:
        issues.append(ConversionIssue("missing_reason_to_follow", "state a credible reason to return or set conversion metadata aside"))
    if plan.series_id and plan.series_id not in series:
        issues.append(ConversionIssue("unknown_series", f"series_id {plan.series_id!r} is not in the series catalog"))
    cta = plan.cta
    if not cta.enabled:
        if cta.text:
            issues.append(ConversionIssue("disabled_cta_text", "a disabled CTA must not carry placeholder text", "warning"))
        return ConversionReview(tuple(issues))
    try:
        strategy = get_cta_strategy(cta.strategy)
    except ValueError as exc:
        issues.append(ConversionIssue("unknown_cta_strategy", str(exc)))
        return ConversionReview(tuple(issues))
    if not cta.text:
        issues.append(ConversionIssue("missing_cta_text", "enabled CTA requires approved text"))
    if cta.duration_seconds is not None and cta.duration_seconds <= 0:
        issues.append(ConversionIssue("invalid_cta_window", "CTA end_seconds must be after start_seconds"))
    if cta.duration_seconds is not None and cta.max_duration_seconds is not None and cta.duration_seconds > cta.max_duration_seconds:
        issues.append(ConversionIssue("excessive_cta_duration", "CTA exceeds its configured maximum duration"))
    if cta.duration_seconds is not None and strategy.suggested_duration_seconds and cta.duration_seconds > strategy.suggested_duration_seconds[1] * 2:
        issues.append(ConversionIssue("excessive_cta_duration", "CTA is materially longer than the strategy guideline", "warning"))
    if payoff_end_seconds is not None and cta.start_seconds is not None and cta.start_seconds < payoff_end_seconds:
        issues.append(ConversionIssue("cta_before_payoff", "CTA begins before the main educational payoff"))
    if reel_duration_seconds is not None and cta.end_seconds is not None and cta.end_seconds > reel_duration_seconds:
        issues.append(ConversionIssue("cta_outside_reel", "CTA ends after the reel duration"))
    if cta.strategy == "next_episode":
        reference = planned_content.get(cta.next_episode_id or "")
        if reference is None or reference.status not in {"planned", "scheduled", "published"}:
            issues.append(ConversionIssue("unverified_future_promise", "next_episode CTA requires a planned or scheduled content reference"))
    if cta.strategy == "related_reel" and (not cta.related_reel_id or cta.related_reel_id not in published_reels):
        issues.append(ConversionIssue("unverified_related_reel", "related_reel CTA requires a published reel reference"))
    return ConversionReview(tuple(issues))

