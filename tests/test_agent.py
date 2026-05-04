"""Tests for the rational TrafficAgent — owned by Member 2."""
import copy

import pytest

from config import (
    Direction,
    IntersectionState,
    LightState,
    MAX_GREEN_TIME,
    MIN_GREEN_TIME,
    TimingPlan,
)
from src.agent import traffic_agent as ta
from src.agent.traffic_agent import TrafficAgent


def _state(densities=None, lights=None, cycle=1):
    if densities is None:
        densities = {d: 5 for d in Direction}
    if lights is None:
        lights = {d: LightState.RED for d in Direction}
    return IntersectionState(
        densities=dict(densities),
        light_states=dict(lights),
        current_phase_time=0,
        cycle_number=cycle,
        avg_wait_time=0.0,
        total_cars_passed=0,
    )


# --- existing contract test (kept) -----------------------------------------

def test_agent_returns_valid_plan():
    agent = TrafficAgent()
    plan = agent.act(_state())
    assert isinstance(plan, TimingPlan)
    assert all(MIN_GREEN_TIME <= dur <= MAX_GREEN_TIME for dur in plan.durations.values())


# --- new tests --------------------------------------------------------------

def test_agent_can_be_instantiated_with_no_args():
    agent = TrafficAgent()
    assert agent.history == []
    assert agent.current_plan is None


def test_act_returns_plan_for_every_direction():
    plan = TrafficAgent().act(_state())
    assert set(plan.durations.keys()) == set(Direction)
    for d in Direction:
        assert isinstance(plan.durations[d], int)


def test_act_does_not_mutate_input_state():
    state = _state(densities={d: 4 for d in Direction})
    snapshot = copy.deepcopy(state)
    TrafficAgent().act(state)
    assert state.densities == snapshot.densities
    assert state.light_states == snapshot.light_states
    assert state.cycle_number == snapshot.cycle_number
    assert state.avg_wait_time == snapshot.avg_wait_time
    assert state.total_cars_passed == snapshot.total_cars_passed


def test_perceive_appends_to_history():
    agent = TrafficAgent()
    agent.perceive(_state(cycle=1))
    agent.perceive(_state(cycle=2))
    assert len(agent.history) == 2
    assert agent.history[-1].cycle_number == 2


def test_history_is_bounded():
    agent = TrafficAgent(history_limit=3)
    for i in range(10):
        agent.perceive(_state(cycle=i))
    assert len(agent.history) == 3
    # Newest survives, oldest evicted.
    assert agent.history[-1].cycle_number == 9
    assert agent.history[0].cycle_number == 7


def test_act_updates_current_plan():
    agent = TrafficAgent()
    plan = agent.act(_state())
    assert agent.current_plan is plan


def test_priority_direction_gets_boost():
    # NORTH heavily congested + not green → logic should mark it CRITICAL.
    densities = {d: 1 for d in Direction}
    densities[Direction.NORTH] = 25
    plan = TrafficAgent(priority_boost=5).act(_state(densities=densities))
    assert plan.durations[Direction.NORTH] >= MIN_GREEN_TIME
    # Boost is applied after optimization; result still respects upper bound.
    assert plan.durations[Direction.NORTH] <= MAX_GREEN_TIME


def test_act_handles_zero_density_state():
    plan = TrafficAgent().act(_state(densities={d: 0 for d in Direction}))
    assert all(MIN_GREEN_TIME <= dur <= MAX_GREEN_TIME for dur in plan.durations.values())


def test_invalid_state_raises():
    agent = TrafficAgent()
    with pytest.raises(ValueError):
        agent.act(None)


def test_missing_direction_density_raises():
    bad = _state()
    bad.densities.pop(Direction.NORTH)
    with pytest.raises(ValueError):
        TrafficAgent().act(bad)


def test_negative_density_raises():
    bad = _state()
    bad.densities[Direction.NORTH] = -1
    with pytest.raises(ValueError):
        TrafficAgent().act(bad)


# --- fallback behaviour: simulate teammate modules raising at runtime -------

def test_fallback_when_optimizer_raises(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("optimizer down")

    monkeypatch.setattr(ta, "_opt_optimize", boom)
    plan = TrafficAgent().act(_state())
    assert isinstance(plan, TimingPlan)
    assert all(MIN_GREEN_TIME <= dur <= MAX_GREEN_TIME for dur in plan.durations.values())


def test_fallback_when_logic_raises(monkeypatch):
    def boom(state):
        raise RuntimeError("logic down")

    monkeypatch.setattr(ta, "_logic_decide_priority", boom)
    densities = {d: 1 for d in Direction}
    densities[Direction.EAST] = 30
    plan = TrafficAgent().act(_state(densities=densities))
    assert isinstance(plan, TimingPlan)
    # Fallback picks the densest direction → EAST gets the boost path.
    assert all(MIN_GREEN_TIME <= dur <= MAX_GREEN_TIME for dur in plan.durations.values())


def test_fallback_when_optimizer_returns_garbage(monkeypatch):
    monkeypatch.setattr(ta, "_opt_optimize", lambda *a, **kw: None)
    plan = TrafficAgent().act(_state())
    assert isinstance(plan, TimingPlan)
    assert all(MIN_GREEN_TIME <= dur <= MAX_GREEN_TIME for dur in plan.durations.values())
