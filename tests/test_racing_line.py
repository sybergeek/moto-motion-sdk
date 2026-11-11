from moto_motion.models.racing_line import RacingLineSimulation


def test_wider_racing_line_is_longer_but_wins_illustrative_time_model():
    simulation = RacingLineSimulation.build()
    assert simulation.blue and simulation.red
    assert simulation.red.route.length > simulation.blue.route.length
    assert simulation.red.corner_speed_limit > simulation.blue.corner_speed_limit
    assert simulation.red.elapsed_seconds < simulation.blue.elapsed_seconds
    assert simulation.red.corner_exit_speed > simulation.blue.corner_exit_speed
    assert simulation.report()["comparison"]["winner"] == "red"
