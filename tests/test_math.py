from config import IntersectionState, Direction, LightState
from src.math_models.matrices import congestion_norm
from src.math_models.probability import expected_arrivals, poisson_pmf


def test_norm_zero_when_empty():
    state = IntersectionState(
        densities={d: 0 for d in Direction},
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=0,
        avg_wait_time=0, total_cars_passed=0,
    )
    assert congestion_norm(state) == 0.0


def test_expected_arrivals():
    assert expected_arrivals(0.3, 10) == 3.0


def test_poisson_pmf_sums_to_one():
    s = sum(poisson_pmf(k, 0.3, 10) for k in range(40))
    assert abs(s - 1.0) < 1e-3
