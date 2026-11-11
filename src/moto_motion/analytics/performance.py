"""Performance facts and derived conversion diagnostics.

Missing values remain None; account-level follower change is deliberately not
treated as reel-attributed follows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Iterable


@dataclass(frozen=True)
class PerformanceMetrics:
    views: int | None = None
    reach: int | None = None
    average_watch_time_seconds: float | None = None
    total_watch_time_seconds: float | None = None
    completion_rate: float | None = None
    retention_curve: tuple[dict[str, object], ...] | None = None
    replays: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    saves: int | None = None
    profile_visits_attributed: int | None = None
    follows_attributed: int | None = None
    net_account_follower_change: int | None = None
    observation_start: date | None = None
    observation_end: date | None = None
    # New optional fields are appended to preserve the legacy positional order.
    unique_viewers: int | None = None
    skip_rate: float | None = None
    retention_at_seconds: dict[str, float | None] | None = None
    reposts: int | None = None


@dataclass(frozen=True)
class ConversionMetrics:
    follow_conversion_per_view: float | None = None
    follows_per_1000_views: float | None = None
    profile_visit_rate: float | None = None
    profile_visit_to_follow_ratio: float | None = None


@dataclass(frozen=True)
class PerformanceObservation:
    """A time-bounded observation; unknown timestamps and metrics remain None."""

    reel_id: str
    metrics: PerformanceMetrics
    observed_at: str | None = None
    observation_window: str | None = None
    duration_seconds: float | None = None
    topic: str | None = None
    content_category: str | None = None
    series_id: str | None = None
    hook_type: str | None = None
    opening_visual_type: str | None = None
    approval_status: str | None = None
    preview_revision: str | None = None
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["notes"] = list(self.notes)
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PerformanceObservation":
        raw_metrics = value.get("metrics", value)
        known = {field for field in PerformanceMetrics.__dataclass_fields__}
        metrics = PerformanceMetrics(**{key: raw_metrics.get(key) for key in known if key in raw_metrics})
        return cls(
            reel_id=str(value["reel_id"]), metrics=metrics, observed_at=value.get("observed_at"), observation_window=value.get("observation_window"), duration_seconds=value.get("duration_seconds"), topic=value.get("topic"), content_category=value.get("content_category"), series_id=value.get("series_id"), hook_type=value.get("hook_type"), opening_visual_type=value.get("opening_visual_type"), approval_status=value.get("approval_status"), preview_revision=value.get("preview_revision"), notes=tuple(value.get("notes", ())),
        )


def _ratio(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def calculate_conversion_metrics(metrics: PerformanceMetrics) -> ConversionMetrics:
    per_view = _ratio(metrics.follows_attributed, metrics.views)
    return ConversionMetrics(per_view, per_view * 1000 if per_view is not None else None, _ratio(metrics.profile_visits_attributed, metrics.views), _ratio(metrics.follows_attributed, metrics.profile_visits_attributed))


@dataclass(frozen=True)
class Diagnostic:
    observed: str
    hypothesis: str


def diagnose_conversion(metrics: PerformanceMetrics) -> tuple[Diagnostic, ...]:
    derived = calculate_conversion_metrics(metrics)
    diagnostics: list[Diagnostic] = []
    if metrics.views is not None and metrics.profile_visits_attributed is not None and metrics.views > 0 and derived.profile_visit_rate is not None and derived.profile_visit_rate < 0.01:
        diagnostics.append(Diagnostic("views are recorded while attributed profile visits are below 1% of views", "Viewers may not understand why to explore the profile; test clearer identity or a more specific return cue."))
    if metrics.profile_visits_attributed is not None and metrics.follows_attributed is not None and metrics.profile_visits_attributed > 0 and derived.profile_visit_to_follow_ratio is not None and derived.profile_visit_to_follow_ratio < 0.1:
        diagnostics.append(Diagnostic("attributed profile visits are recorded while fewer than 10% become attributed follows", "The profile value proposition, branding, or content consistency may need review."))
    if metrics.saves is not None and metrics.shares is not None and metrics.follows_attributed is not None and metrics.saves + metrics.shares > 0 and metrics.follows_attributed == 0:
        diagnostics.append(Diagnostic("saves and shares are recorded while attributed follows are zero", "The reel may deliver standalone value without establishing a reason to return."))
    return tuple(diagnostics)


def append_observation(records: Iterable[PerformanceObservation], observation: PerformanceObservation) -> tuple[PerformanceObservation, ...]:
    """Append without silently replacing an observation with the same key."""
    records = tuple(records)
    duplicate = any(item.reel_id == observation.reel_id and item.observed_at == observation.observed_at and item.observation_window == observation.observation_window for item in records)
    if duplicate:
        raise ValueError("duplicate performance observation key")
    return records + (observation,)


def compare_observations(records: Iterable[PerformanceObservation]) -> dict[str, Any]:
    records = tuple(records)
    warnings: list[str] = []
    if len(records) < 2:
        warnings.append("At least two observations are required for a comparison; no performance conclusion is drawn.")
    windows = {record.observation_window for record in records if record.observation_window}
    if len(windows) > 1:
        warnings.append("Observation windows differ; compare only with caution.")
    return {"observations": [record.to_dict() for record in records], "warnings": warnings, "comparison_type": "observational"}

