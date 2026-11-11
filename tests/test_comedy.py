from moto_motion.creative.comedy import ComedyBeat, ComedyTechnique


def test_comedy_beat_is_serializable_and_explicit():
    beat = ComedyBeat(ComedyTechnique.CALLBACK, visual_payoff="front_grid")
    assert beat.to_dict()["technique"] == "callback"
    assert beat.to_dict()["visual_payoff"] == "front_grid"


def test_deadpan_requires_a_pause():
    try:
        ComedyBeat(ComedyTechnique.DEADPAN_PAUSE)
    except ValueError as error:
        assert "pause_ms" in str(error)
    else:
        raise AssertionError("deadpan beat without a pause should be rejected")
