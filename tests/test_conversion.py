import pytest

from moto_motion.creative.conversion import (
    CTAConfig,
    CTADelivery,
    CTAPlacement,
    ConversionObjective,
    ConversionPlan,
    ConversionPlanner,
    review_conversion,
)
from moto_motion.core.safe_area import LogicalCanvas, validate_scene_layout
from moto_motion.renderers.manim.branding import FollowCTA


def test_strategy_library_has_all_supported_conversion_choices():
    planner = ConversionPlanner.racexplained_defaults()
    assert planner.review(None).valid
    assert {"none", "subtle_visual", "direct_follow", "next_episode", "series", "related_reel", "profile_discovery"} <= __import__("moto_motion.creative.conversion", fromlist=["CTA_STRATEGIES"]).CTA_STRATEGIES.keys()


def test_existing_manifest_without_conversion_metadata_remains_compatible():
    assert ConversionPlan.from_dict(None) is None


def test_disabled_cta_is_valid_without_placeholder_text():
    plan = ConversionPlan(ConversionObjective.GAIN_RELEVANT_FOLLOWERS, "MotoGP fans", "more physics", cta=CTAConfig())
    assert review_conversion(plan).valid
    invalid = ConversionPlan(ConversionObjective.GAIN_RELEVANT_FOLLOWERS, "MotoGP fans", "more physics", cta=CTAConfig(text="placeholder"))
    assert any(issue.code == "disabled_cta_text" for issue in review_conversion(invalid).issues)


def test_unknown_series_and_unverified_future_reference_are_rejected():
    plan = ConversionPlan(
        ConversionObjective.RECURRING_SERIES,
        "MotoGP fans",
        "more physics",
        series_id="missing",
        cta=CTAConfig("next_episode", True, "Next: mystery topic", CTAPlacement.AFTER_PAYOFF, CTADelivery.VISUAL, next_episode_id="missing"),
    )
    review = ConversionPlanner.racexplained_defaults().review(plan)
    assert {issue.code for issue in review.issues} >= {"unknown_series", "unverified_future_promise"}


def test_cta_must_follow_payoff_and_fit_its_window():
    plan = ConversionPlan(
        ConversionObjective.GAIN_RELEVANT_FOLLOWERS,
        "F1 fans",
        "more explanations",
        cta=CTAConfig("direct_follow", True, "Follow RaceXplained", CTAPlacement.AFTER_PAYOFF, CTADelivery.NARRATED, 1.0, 4.0, 6.5),
    )
    review = review_conversion(plan, payoff_end_seconds=5.0, reel_duration_seconds=6.0)
    assert {issue.code for issue in review.issues} >= {"cta_before_payoff", "cta_outside_reel"}


def test_follow_cta_uses_normalized_strict_safe_layout_at_multiple_resolutions():
    cta = FollowCTA("More racing explained")
    for dimensions in ((1080, 1920), (2160, 3840)):
        canvas = LogicalCanvas(*dimensions)
        violations = validate_scene_layout(canvas, [cta.layout_element(canvas, end_seconds=2.0)])
        assert violations == []


def test_follow_cta_is_visual_only_when_no_narration_is_requested():
    cta = FollowCTA("More racing explained")
    assert cta.animations(LogicalCanvas(1080, 1920))

