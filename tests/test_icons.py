from xml.etree import ElementTree

import pytest

from moto_motion.icons import ICON_NAMES, IconState, icon_svg


@pytest.mark.parametrize("name", ICON_NAMES)
def test_icon_svg_is_valid_and_transparent(name):
    svg = icon_svg(name)
    ElementTree.fromstring(svg)
    assert 'viewBox="0 0 64 64"' in svg
    assert "<rect width=\"64\" height=\"64\"" not in svg


def test_unknown_icon_is_rejected():
    with pytest.raises(KeyError):
        icon_svg("generic_flag")


def test_icon_state_clamps_progress():
    assert IconState(-1).normalized_progress == 0
    assert IconState(2).normalized_progress == 1
