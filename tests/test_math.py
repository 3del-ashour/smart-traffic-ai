import math

import numpy as np
import pytest

from config import Direction, IntersectionState, LightState
from src.math_models.matrices import congestion_norm, density_matrix, dominant_flow
from src.math_models.probability import (
    expected_arrivals,
    poisson_pmf,
    sample_arrivals,
)

# ── helpers ────────────────────────────────────────────────────────────────────


def _make_state(densities):
    return IntersectionState(
        densities=densities,
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0,
        cycle_number=0,
        avg_wait_time=0.0,
        total_cars_passed=0,
    )


# ── congestion_norm ────────────────────────────────────────────────────────────


def test_norm_zero_when_empty():
    state = _make_state({d: 0 for d in Direction})
    assert congestion_norm(state) == 0.0


def test_norm_known_value():
    # N=3, S=4, E=0, W=0  →  sqrt(9 + 16) = 5.0
    state = _make_state(
        {Direction.NORTH: 3, Direction.SOUTH: 4, Direction.EAST: 0, Direction.WEST: 0}
    )
    assert abs(congestion_norm(state) - 5.0) < 1e-9


# ── density_matrix ─────────────────────────────────────────────────────────────


def test_density_matrix_empty_history_shape():
    result = density_matrix([])
    assert isinstance(result, np.ndarray)
    assert result.shape == (0, 4)


def test_density_matrix_shape_and_values():
    s1 = _make_state(
        {Direction.NORTH: 1, Direction.SOUTH: 2, Direction.EAST: 3, Direction.WEST: 4}
    )
    s2 = _make_state(
        {Direction.NORTH: 5, Direction.SOUTH: 6, Direction.EAST: 7, Direction.WEST: 8}
    )
    result = density_matrix([s1, s2])
    assert result.shape == (2, 4)
    np.testing.assert_array_equal(result[0], [s1.densities[d] for d in Direction])
    np.testing.assert_array_equal(result[1], [s2.densities[d] for d in Direction])


# ── dominant_flow ──────────────────────────────────────────────────────────────


def test_dominant_flow_single_row_returns_zeros():
    result = dominant_flow(np.array([[1.0, 2.0, 3.0, 4.0]]))
    assert result.shape == (4,)
    assert np.all(result == 0.0)


def test_dominant_flow_empty_matrix_returns_zeros():
    result = dominant_flow(np.zeros((0, 4)))
    assert result.shape == (4,)
    assert np.all(result == 0.0)


def test_dominant_flow_zero_variance_returns_zeros():
    # All rows identical → covariance is zero → degenerate
    m = np.array([[5.0, 5.0, 5.0, 5.0], [5.0, 5.0, 5.0, 5.0], [5.0, 5.0, 5.0, 5.0]])
    result = dominant_flow(m)
    assert result.shape == (4,)
    assert np.all(result == 0.0)


def test_dominant_flow_valid_returns_finite_vector():
    m = np.array(
        [
            [10.0, 1.0, 2.0, 3.0],
            [12.0, 1.0, 2.0, 1.0],
            [8.0, 3.0, 1.0, 2.0],
            [15.0, 2.0, 1.0, 1.0],
        ]
    )
    result = dominant_flow(m)
    assert result.shape == (4,)
    assert np.all(np.isfinite(result))


def test_dominant_flow_wrong_column_count_returns_zeros():
    # 3 columns instead of 4
    m = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    result = dominant_flow(m)
    assert result.shape == (4,)
    assert np.all(result == 0.0)


def test_dominant_flow_non_finite_values_returns_zeros():
    m = np.array([[1.0, 2.0, np.inf, 4.0], [5.0, 6.0, 7.0, 8.0]])
    result = dominant_flow(m)
    assert result.shape == (4,)
    assert np.all(result == 0.0)


def test_dominant_flow_accepts_list_input():
    result = dominant_flow([[1, 2, 3, 4], [2, 3, 4, 5]])
    assert result.shape == (4,)
    assert np.all(np.isfinite(result))


# ── expected_arrivals ──────────────────────────────────────────────────────────


def test_expected_arrivals_basic():
    assert expected_arrivals(0.3, 10) == 3.0


def test_expected_arrivals_zero_rate():
    assert expected_arrivals(0.0, 10) == 0.0


def test_expected_arrivals_negative_rate_raises():
    with pytest.raises(ValueError):
        expected_arrivals(-0.1, 10)


def test_expected_arrivals_negative_time_raises():
    with pytest.raises(ValueError):
        expected_arrivals(0.3, -5)


# ── poisson_pmf ────────────────────────────────────────────────────────────────


def test_poisson_pmf_sums_to_one():
    total = sum(poisson_pmf(k, 0.3, 10) for k in range(40))
    assert abs(total - 1.0) < 1e-3


def test_poisson_pmf_zero_lambda_k0():
    assert poisson_pmf(0, 0.0, 1.0) == 1.0


def test_poisson_pmf_zero_lambda_k_positive():
    assert poisson_pmf(1, 0.0, 1.0) == 0.0
    assert poisson_pmf(5, 0.0, 1.0) == 0.0


def test_poisson_pmf_large_k_no_overflow():
    result = poisson_pmf(200, 0.5, 1.0)
    assert math.isfinite(result)
    assert result >= 0.0


def test_poisson_pmf_negative_k_raises():
    with pytest.raises(ValueError):
        poisson_pmf(-1, 0.3, 10)


def test_poisson_pmf_negative_rate_raises():
    with pytest.raises(ValueError):
        poisson_pmf(2, -0.3, 10)


def test_poisson_pmf_negative_time_raises():
    with pytest.raises(ValueError):
        poisson_pmf(2, 0.3, -10)


# ── sample_arrivals ────────────────────────────────────────────────────────────


def test_sample_arrivals_returns_non_negative_int():
    result = sample_arrivals(0.3, 10)
    assert isinstance(result, int)
    assert result >= 0


def test_sample_arrivals_zero_rate_returns_zero():
    result = sample_arrivals(0.0, 10)
    assert result == 0


def test_sample_arrivals_negative_rate_raises():
    with pytest.raises(ValueError):
        sample_arrivals(-0.1, 10)


def test_sample_arrivals_negative_time_raises():
    with pytest.raises(ValueError):
        sample_arrivals(0.3, -5)
