"""Small, serializable contracts for optional follower-conversion decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class ConversionObjective(StrEnum):
    INTRODUCE_BRAND = "introduce_brand"
    GAIN_RELEVANT_FOLLOWERS = "gain_relevant_followers"
    PROFILE_DISCOVERY = "profile_discovery"
    RECURRING_SERIES = "recurring_series"
    RELATED_REEL = "related_reel"
    BRAND_RECOGNITION = "brand_recognition"


class CTAPlacement(StrEnum):
    NONE = "none"
    AFTER_PAYOFF = "after_payoff"
    CLOSING_BEAT = "closing_beat"
    NATURAL_PAUSE = "natural_pause"


class CTADelivery(StrEnum):
    VISUAL = "visual"
    NARRATED = "narrated"
    VISUAL_AND_NARRATED = "visual_and_narrated"


@dataclass(frozen=True)
class PlannedContent:
    """A verified future or published content reference, never free-form proof."""

    content_id: str
    topic: str
    status: str = "planned"  # planned | scheduled | published


@dataclass(frozen=True)
class SeriesMetadata:
    series_id: str
    display_name: str
    description: str
    target_audience: str
    visual_identity: str
    related_reel_ids: tuple[str, ...] = ()
    planned_future_topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class CTAConfig:
    strategy: str = "none"
    enabled: bool = False
    text: str | None = None
    placement: CTAPlacement = CTAPlacement.NONE
    delivery: CTADelivery = CTADelivery.VISUAL
    max_duration_seconds: float | None = None
    start_seconds: float | None = None
    end_seconds: float | None = None
    next_episode_id: str | None = None
    related_reel_id: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.start_seconds is None or self.end_seconds is None:
            return None
        return self.end_seconds - self.start_seconds


@dataclass(frozen=True)
class ConversionPlan:
    objective: ConversionObjective | None = None
    target_audience: str | None = None
    reason_to_follow: str | None = None
    series_id: str | None = None
    cta: CTAConfig = field(default_factory=CTAConfig)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "ConversionPlan | None":
        if data is None:
            return None
        raw_cta = data.get("cta") or {}
        return cls(
            objective=ConversionObjective(data["objective"]) if data.get("objective") else None,
            target_audience=data.get("target_audience"),
            reason_to_follow=data.get("reason_to_follow"),
            series_id=data.get("series_id"),
            cta=CTAConfig(
                strategy=str(raw_cta.get("strategy", "none")),
                enabled=bool(raw_cta.get("enabled", False)),
                text=raw_cta.get("text"),
                placement=CTAPlacement(raw_cta.get("placement", "none")),
                delivery=CTADelivery(raw_cta.get("delivery", "visual")),
                max_duration_seconds=raw_cta.get("max_duration_seconds"),
                start_seconds=raw_cta.get("start_seconds"),
                end_seconds=raw_cta.get("end_seconds"),
                next_episode_id=raw_cta.get("next_episode_id"),
                related_reel_id=raw_cta.get("related_reel_id"),
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["objective"] = self.objective.value if self.objective else None
        result["cta"]["placement"] = self.cta.placement.value
        result["cta"]["delivery"] = self.cta.delivery.value
        return result

