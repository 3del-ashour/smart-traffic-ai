"""
Tests for Member 6 (Abdulrahman) — simulation engine.

Covers:
  - Single-step state shape
  - Timing-plan injection from the optimiser
  - High-frequency stability under heavy traffic
  - Lane-capacity cap (MAX_CARS_PER_LANE)
  - Live arrival-rate updates from the dashboard
  - Vehicle wait-time accumulation
"""
import random

from config import (
    Direction,
    LightState,
    MAX_CARS_PER_LANE,
    TimingPlan,
)
from src.simulation.intersection import Intersection
from src.simulation.traffic_generator import generate_arrivals
from src.simulation.vehicle import Vehicle


# ── Intersection ──────────────────────────────────────────────────────────

def test_intersection_step_returns_state():
    random.seed(42)
    inter = Intersection()
    s = inter.step(0.1)
    assert s.total_cars_passed >= 0
    assert sum(s.densities.values()) >= 0


def test_apply_timing():
    inter = Intersection()
    plan = TimingPlan(durations={d: 25 for d in Direction})
    inter.apply_timing(plan)
    assert inter.timing[Direction.NORTH] == 25


def test_peak_load_stability():
    """Engine must remain stable under 100 fast steps."""
    random.seed(99)
    inter = Intersection()
    for _ in range(100):
        inter.step(0.1)
    state = inter.get_state()
    assert state.cycle_number >= 0
    assert all(d in state.densities for d in Direction)


def test_lane_capacity_cap():
    """No lane queue may ever exceed MAX_CARS_PER_LANE."""
    random.seed(7)
    inter = Intersection(arrival_rate=10.0)  # extreme rate
    for _ in range(500):
        inter.step(0.1)
    for d in Direction:
        assert len(inter.queues[d]) <= MAX_CARS_PER_LANE


def test_set_arrival_rate_live():
    """Dashboard slider (Member 8) must be able to change arrival rate live."""
    inter = Intersection(arrival_rate=0.3)
    inter.set_arrival_rate(0.9)
    assert inter.arrival_rate == 0.9


def test_initial_light_state():
    """North starts GREEN, all others RED."""
    inter = Intersection()
    assert inter.lights[Direction.NORTH] == LightState.GREEN
    for d in (Direction.SOUTH, Direction.EAST, Direction.WEST):
        assert inter.lights[d] == LightState.RED


def test_phase_transition_rotates_green():
    """After phase_time exceeds the timing, green moves to the next direction."""
    inter = Intersection()
    inter.timing = {d: 1 for d in Direction}  # very short timer
    initial = inter.current_phase_dir
    for _ in range(20):
        inter.step(0.5)
    # The current green should have moved at least once
    assert inter.current_phase_dir != initial or inter.cycle > 0


def test_cycle_complete_flag():
    """cycle_complete() returns True exactly on the tick a full rotation finishes."""
    inter = Intersection()
    inter.timing = {d: 1 for d in Direction}
    completed_once = False
    for _ in range(50):
        inter.step(0.5)
        if inter.cycle_complete():
            completed_once = True
    assert completed_once


# ── Smart phase selection (the bug fix) ──────────────────────────────────

def test_empty_lane_yields_to_busy_lane():
    """An empty green lane must yield to a busy lane after MIN_GREEN_TIME."""
    from config import LightState, MIN_GREEN_TIME
    from src.simulation.vehicle import Vehicle

    inter = Intersection(arrival_rate=0.0)  # no random arrivals
    inter.current_phase_dir = Direction.EAST
    for d in Direction:
        inter.lights[d] = LightState.RED
    inter.lights[Direction.EAST] = LightState.GREEN
    inter.queues[Direction.NORTH] = [Vehicle(Direction.NORTH, 0.0) for _ in range(8)]

    # Step through enough time to pass MIN_GREEN_TIME
    for _ in range(MIN_GREEN_TIME + 2):
        inter.step(1.0)

    assert inter.lights[Direction.NORTH] == LightState.GREEN
    assert inter.lights[Direction.EAST] == LightState.RED


def test_next_phase_picks_busiest_lane():
    """When the timer expires, the chosen direction should be the one with the most cars."""
    from src.simulation.vehicle import Vehicle

    inter = Intersection(arrival_rate=0.0)
    inter.current_phase_dir = Direction.NORTH
    inter.queues[Direction.SOUTH] = [Vehicle(Direction.SOUTH, 0.0) for _ in range(2)]
    inter.queues[Direction.WEST] = [Vehicle(Direction.WEST, 0.0) for _ in range(9)]
    inter.queues[Direction.EAST] = [Vehicle(Direction.EAST, 0.0) for _ in range(4)]

    inter._next_phase()

    assert inter.current_phase_dir == Direction.WEST   # 9 > 4 > 2


def test_all_empty_falls_back_to_round_robin():
    """If every lane is empty, just rotate to keep the simulation alive."""
    inter = Intersection(arrival_rate=0.0)
    inter.current_phase_dir = Direction.NORTH
    # all queues empty
    inter._next_phase()
    # Round-robin: NORTH → SOUTH next
    assert inter.current_phase_dir == Direction.SOUTH


# ── Vehicle ──────────────────────────────────────────────────────────────

def test_vehicle_basic_fields():
    v = Vehicle(Direction.NORTH, spawn_time=12.5)
    assert v.direction == Direction.NORTH
    assert v.spawn_time == 12.5
    assert v.wait_time == 0.0
    assert isinstance(v.id, int)


def test_vehicle_update_wait_only_when_stopped():
    v = Vehicle(Direction.EAST, spawn_time=0.0)
    v.update_wait(1.0, is_moving=False)
    v.update_wait(1.0, is_moving=True)   # should NOT increment
    v.update_wait(2.0, is_moving=False)
    assert v.wait_time == 3.0


# ── traffic_generator ────────────────────────────────────────────────────

def test_generate_arrivals_returns_non_negative():
    random.seed(0)
    n = generate_arrivals(0.3, 1.0)
    assert isinstance(n, int)
    assert n >= 0


def test_generate_arrivals_burst_mode_higher_on_average():
    """Burst mode triples lambda — over many samples its mean must exceed normal."""
    random.seed(1)
    normal_total = sum(generate_arrivals(0.5, 1.0) for _ in range(500))
    random.seed(1)
    burst_total = sum(generate_arrivals(0.5, 1.0, burst=True) for _ in range(500))
    assert burst_total > normal_total
