"""Lightweight observational CTA experiment records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .performance import PerformanceMetrics, calculate_conversion_metrics


@dataclass(frozen=True)
class ConversionExperiment:
    experiment_id: str
    reel_id: str
    cta_strategy: str
    content_category: str
    series_id: str | None
    publication_date: date
    observation_window: str
    metrics: PerformanceMetrics
    notes: str = ""


def compare_experiments(records: Iterable[ConversionExperiment]) -> dict[str, object]:
    rows = []
    for record in records:
        derived = calculate_conversion_metrics(record.metrics)
        rows.append({"experiment_id": record.experiment_id, "reel_id": record.reel_id, "cta_strategy": record.cta_strategy, "follows_per_1000_views": derived.follows_per_1000_views})
    return {
        "records": rows,
        "comparison_type": "observational",
        "warnings": ["Do not call this a randomized A/B test without random assignment.", "Compare similar topics, dates, exposure, hooks and sample sizes; reporting windows may differ."],
    }

