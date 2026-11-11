from moto_motion.renderers.manim.branding import RaceXplainedChapter


def test_racexplained_chapter_label_is_stable():
    marker = RaceXplainedChapter(chapter="QATAR · TITLE #8")
    assert marker.label() == "RACEXPLAINED · QATAR · TITLE #8"


def test_racexplained_chapter_without_chapter_is_brand_only():
    assert RaceXplainedChapter(chapter="").label() == "RACEXPLAINED"
