from config import IntersectionState, Direction, LightState, TimingPlan
from src.optimization.simulated_annealing import optimize, cost_function


def test_optimize_returns_valid_plan():
    state = IntersectionState(
        densities={d: 8 for d in Direction},
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=0,
        avg_wait_time=0, total_cars_passed=0,
    )
    plan = optimize(state, iterations=200)
    assert all(10 <= dur <= 60 for dur in plan.durations.values())


def test_optimize_improves_cost():
    state = IntersectionState(
        densities={Direction.NORTH: 20, Direction.SOUTH: 1,
                   Direction.EAST: 1, Direction.WEST: 1},
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=0,
        avg_wait_time=0, total_cars_passed=0,
    )
    default = TimingPlan(durations={d: 30 for d in Direction})
    optimized = optimize(state, iterations=500)
    assert cost_function(optimized, state) <= cost_function(default, state)
