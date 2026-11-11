import json
from datetime import date
from pathlib import Path

import pytest

from moto_motion.analytics import ConversionExperiment, PerformanceMetrics, PerformanceObservation, append_observation, calculate_conversion_metrics, compare_experiments, compare_observations, diagnose_conversion


def test_conversion_metrics_preserve_missing_values_and_zero_denominators():
    empty = calculate_conversion_metrics(PerformanceMetrics(follows_attributed=4, profile_visits_attributed=0, views=0))
    assert empty.follow_conversion_per_view is None
    assert empty.follows_per_1000_views is None
    assert empty.profile_visit_to_follow_ratio is None
    assert calculate_conversion_metrics(PerformanceMetrics(follows_attributed=4, profile_visits_attributed=20, views=100)).follows_per_1000_views == 40


def test_account_growth_is_not_used_as_reel_attributed_follows():
    metrics = PerformanceMetrics(views=1000, net_account_follower_change=80)
    derived = calculate_conversion_metrics(metrics)
    assert derived.follows_per_1000_views is None


def test_diagnostics_are_hypotheses_tied_to_observed_metrics():
    diagnostics = diagnose_conversion(PerformanceMetrics(views=1000, profile_visits_attributed=5, follows_attributed=0, saves=20, shares=10))
    assert diagnostics
    assert all(item.observed and item.hypothesis for item in diagnostics)


def test_experiment_comparison_is_explicitly_observational():
    result = compare_experiments([ConversionExperiment("exp-1", "reel-6", "none", "physics", "the_science", date(2026, 11, 8), "7d", PerformanceMetrics(views=1000, follows_attributed=3))])
    assert result["comparison_type"] == "observational"
    assert result["records"][0]["follows_per_1000_views"] == 3


def test_reel_005_historical_snapshot_is_loaded_without_inventing_timestamps():
    payload = json.loads(Path("data/analytics/performance_observations.json").read_text(encoding="utf-8"))
    observation = PerformanceObservation.from_dict(payload["observations"][0])
    assert observation.reel_id == "reel_005"
    assert observation.metrics.views == 2422
    assert observation.metrics.unique_viewers == 1929
    assert observation.metrics.follows_attributed == 0
    assert observation.observed_at is None
    assert observation.metrics.retention_at_seconds is None


def test_duplicate_observation_and_insufficient_comparison_are_explicit():
    observation = PerformanceObservation("reel_006", PerformanceMetrics(views=10), observation_window="7d")
    assert "At least two observations" in compare_observations([observation])["warnings"][0]
    with pytest.raises(ValueError):
        append_observation([observation], observation)
