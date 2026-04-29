from config import IntersectionState, Direction, LightState
from src.agent.traffic_agent import TrafficAgent


def test_agent_returns_valid_plan():
    state = IntersectionState(
        densities={d: 5 for d in Direction},
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=1,
        avg_wait_time=0.0, total_cars_passed=0,
    )
    agent = TrafficAgent()
    plan = agent.act(state)
    assert all(10 <= dur <= 60 for dur in plan.durations.values())
