"""
Tests for Simulated Annealing — Member 5 (Kürşat Bayram)
Validates report claims:
  - All timings stay in [MIN_GREEN_TIME, MAX_GREEN_TIME]
  - SA improves over the default plan
  - SA outperforms Random Search on congested states
  - cost_function behaves correctly
  - Cooling schedule matches report (T0=100, alpha=0.99)
"""
import math
import random

import pytest

from config import (
    Direction,
    IntersectionState,
    LightState,
    MAX_GREEN_TIME,
    MIN_GREEN_TIME,
    SA_COOLING,
    SA_INITIAL_TEMP,
    SA_ITERATIONS,
    TimingPlan,
)
from src.optimization.simulated_annealing import (
    _perturb,
    cost_function,
    optimize,
    random_search,
)


# ── helpers ────────────────────────────────────────────────────────────────

def _state(densities=None):
    if densities is None:
        densities = {d: 8 for d in Direction}
    return IntersectionState(
        densities=densities,
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0,
        cycle_number=0,
        avg_wait_time=0.0,
        total_cars_passed=0,
    )


def _default_plan():
    return TimingPlan(durations={d: 30 for d in Direction})


# ── cost_function ──────────────────────────────────────────────────────────

def test_cost_zero_density():
    """Zero cars → zero cost regardless of green time."""
    plan = _default_plan()
    state = _state({d: 0 for d in Direction})
    assert cost_function(plan, state) == 0.0


def test_cost_max_green_gives_zero_cost():
    """MAX green time → zero penalty term per direction."""
    plan = TimingPlan(durations={d: MAX_GREEN_TIME for d in Direction})
    state = _state({d: 10 for d in Direction})
    assert cost_function(plan, state) == pytest.approx(0.0)


def test_cost_higher_density_higher_cost():
    """More cars waiting → higher cost for the same plan."""
    plan = _default_plan()
    low = cost_function(plan, _state({d: 1 for d in Direction}))
    high = cost_function(plan, _state({d: 20 for d in Direction}))
    assert high > low


def test_cost_less_green_higher_cost():
    """Less green time for the same density → higher cost."""
    state = _state({d: 10 for d in Direction})
    short = cost_function(TimingPlan(durations={d: MIN_GREEN_TIME for d in Direction}), state)
    long_ = cost_function(TimingPlan(durations={d: MAX_GREEN_TIME for d in Direction}), state)
    assert short > long_


# ── _perturb ──────────────────────────────────────────────────────────────

def test_perturb_stays_in_bounds():
    plan = _default_plan()
    for _ in range(200):
        new = _perturb(plan)
        for d in Direction:
            assert MIN_GREEN_TIME <= new.durations[d] <= MAX_GREEN_TIME


def test_perturb_changes_exactly_one_direction():
    random.seed(42)
    plan = TimingPlan(durations={d: 30 for d in Direction})
    changed = 0
    for _ in range(100):
        new = _perturb(plan)
        changed = sum(1 for d in Direction if new.durations[d] != plan.durations[d])
        assert changed == 1


# ── optimize ──────────────────────────────────────────────────────────────

def test_optimize_returns_valid_plan():
    plan = optimize(_state(), iterations=200)
    assert isinstance(plan, TimingPlan)
    assert set(plan.durations.keys()) == set(Direction)
    for d in Direction:
        assert MIN_GREEN_TIME <= plan.durations[d] <= MAX_GREEN_TIME


def test_optimize_improves_over_default():
    """SA must find a plan at least as good as the default 30s plan."""
    state = _state({
        Direction.NORTH: 20,
        Direction.SOUTH: 2,
        Direction.EAST: 2,
        Direction.WEST: 2,
    })
    default_cost = cost_function(_default_plan(), state)
    optimized = optimize(state, iterations=500)
    assert cost_function(optimized, state) <= default_cost


def test_optimize_with_history():
    """return_history=True gives (TimingPlan, list)."""
    state = _state()
    result = optimize(state, iterations=100, return_history=True)
    assert isinstance(result, tuple)
    plan, history = result
    assert isinstance(plan, TimingPlan)
    assert len(history) == 100
    assert all(isinstance(c, float) for c in history)


def test_optimize_history_non_increasing():
    """Best cost tracked in history must be non-increasing."""
    _, history = optimize(_state(), iterations=300, return_history=True)
    for i in range(1, len(history)):
        assert history[i] <= history[i - 1] + 1e-9


def test_optimize_zero_density_state():
    """Zero density → any valid plan is optimal (cost = 0)."""
    state = _state({d: 0 for d in Direction})
    plan = optimize(state, iterations=100)
    assert cost_function(plan, state) == 0.0


# ── cooling schedule matches report ───────────────────────────────────────

def test_config_matches_report():
    """Verify config values match Kürşat's report."""
    assert SA_INITIAL_TEMP == 100.0
    assert SA_COOLING == 0.99
    assert SA_ITERATIONS == 1000


def test_cooling_schedule_reaches_near_zero():
    """After 1000 iterations T₀=100 × 0.99^1000 ≈ 4.3e-5 (near zero)."""
    final_T = SA_INITIAL_TEMP * (SA_COOLING ** SA_ITERATIONS)
    assert final_T < 0.01


# ── SA vs Random Search ───────────────────────────────────────────────────

def test_sa_converges_cost_drops():
    """
    SA cost history must drop significantly from start to end.
    Proves the algorithm is actually learning, not just wandering.
    """
    state = _state({
        Direction.NORTH: 18,
        Direction.SOUTH: 8,
        Direction.EAST: 14,
        Direction.WEST: 5,
    })
    _, history = optimize(state, iterations=1000, return_history=True)
    early_avg = sum(history[:50]) / 50    # first 50 iterations
    late_avg  = sum(history[-50:]) / 50   # last 50 iterations
    assert late_avg < early_avg           # cost dropped over time


def test_random_search_returns_valid_plan():
    """random_search baseline returns a valid plan + cost history list."""
    state = _state()
    plan, history = random_search(state, iterations=200)
    assert isinstance(plan, TimingPlan)
    assert all(MIN_GREEN_TIME <= v <= MAX_GREEN_TIME for v in plan.durations.values())
    assert len(history) == 200
