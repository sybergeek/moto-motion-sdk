import pytest

from moto_motion.core.themes import (
    CARBON_SIGNAL,
    EDITORIAL_IVORY,
    MIDNIGHT_TECHNICAL,
    RACING_HERITAGE,
    THEMES,
    blend_hex,
    contrast_ratio,
    passes_text_contrast,
    vehicle_separation_color,
)


def test_four_named_themes_are_registered():
    assert set(THEMES) == {
        "midnight_technical",
        "editorial_ivory",
        "carbon_signal",
        "racing_heritage",
    }


@pytest.mark.parametrize("theme", THEMES.values())
def test_primary_text_meets_normal_text_contrast(theme):
    assert passes_text_contrast(theme.text, theme.background)
    assert contrast_ratio(theme.secondary_text, theme.background) >= 4.5


@pytest.mark.parametrize("theme", THEMES.values())
def test_semantic_colors_remain_available(theme):
    assert theme.semantic.braking == "#F05A45"
    assert theme.semantic.acceleration == "#32C7D5"
    assert theme.semantic.focus == "#F4C95D"
    assert theme.semantic.positive_delta == "#49D9BC"


def test_dark_to_light_blend_has_no_uncontrolled_white_flash():
    colors = [blend_hex(MIDNIGHT_TECHNICAL.background, EDITORIAL_IVORY.background, index / 8) for index in range(9)]
    assert colors[0] == MIDNIGHT_TECHNICAL.background
    assert colors[-1] == EDITORIAL_IVORY.background
    assert "#FFFFFF" not in colors


@pytest.mark.parametrize("theme", THEMES.values())
def test_vehicle_separation_color_is_visible(theme):
    outline = vehicle_separation_color(theme, theme.accent)
    assert contrast_ratio(outline, theme.background) >= 3.0
