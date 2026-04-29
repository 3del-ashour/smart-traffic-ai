from config import IntersectionState, Direction, LightState
from src.evaluation.metrics import compute_metrics


def test_metrics_empty():
    assert compute_metrics([]) == {}


def test_metrics_basic():
    s = IntersectionState(
        densities={d: 2 for d in Direction},
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=1,
        avg_wait_time=5.0, total_cars_passed=10,
    )
    m = compute_metrics([s, s, s])
    assert m["mean_wait"] == 5.0
    assert m["total_passed"] == 10
