from config import IntersectionState, Direction, LightState
from src.logic.inference import decide_priority, modus_ponens


def _make_state(densities):
    return IntersectionState(
        densities=densities,
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=1,
        avg_wait_time=0.0, total_cars_passed=0,
    )


def test_high_density_triggers_critical():
    densities = {d: 1 for d in Direction}
    densities[Direction.NORTH] = 20
    state = _make_state(densities)
    assert decide_priority(state) == Direction.NORTH


def test_modus_ponens_critical():
    assert "critical" in modus_ponens({"high_density", "not_green"})


def test_modus_ponens_no_match():
    assert modus_ponens({"low_density", "not_green"}) == set()
