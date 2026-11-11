"""Conservative conversion planner: explicit decisions, no automatic CTA append."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ConversionPlan, PlannedContent, SeriesMetadata
from .validator import ConversionReview, review_conversion


@dataclass(frozen=True)
class ConversionPlanner:
    series: dict[str, SeriesMetadata]
    planned_content: dict[str, PlannedContent]
    published_reels: frozenset[str] = frozenset()

    @classmethod
    def racexplained_defaults(cls) -> "ConversionPlanner":
        return cls(
            series={
                "the_science": SeriesMetadata("the_science", "The Science", "Racing physics explained visually.", "F1 and MotoGP fans curious about engineering", "technical diagrams with signal accents", (), ("trail braking", "traction on corner exit")),
                "the_stories": SeriesMetadata("the_stories", "The Stories", "Championships, rivalries and motorsport history.", "fans who enjoy the people and stakes behind racing", "editorial timelines and named comparisons"),
                "the_breakdown": SeriesMetadata("the_breakdown", "The Breakdown", "The decisions and incidents that change a race.", "fans who want decisive moments explained", "annotated race moments and comparisons"),
            },
            planned_content={
                "trail_braking": PlannedContent("trail_braking", "Why MotoGP riders trail brake", "planned"),
                "traction_exit": PlannedContent("traction_exit", "How riders protect traction on corner exit", "planned"),
            },
        )

    def review(self, plan: ConversionPlan | None, *, payoff_end_seconds: float | None = None, reel_duration_seconds: float | None = None) -> ConversionReview:
        return review_conversion(plan, series=self.series, planned_content=self.planned_content, published_reels=self.published_reels, payoff_end_seconds=payoff_end_seconds, reel_duration_seconds=reel_duration_seconds)

