"""Simulated Annealing — owned by Member 5."""
import math
import random
from config import (
    TimingPlan, Direction, IntersectionState,
    MIN_GREEN_TIME, MAX_GREEN_TIME,
    SA_ITERATIONS, SA_INITIAL_TEMP, SA_COOLING,
)


def cost_function(plan: TimingPlan, state: IntersectionState) -> float:
    total = 0.0
    for d in Direction:
        density = state.densities[d]
        green = plan.durations[d]
        total += density * (MAX_GREEN_TIME - green) / MAX_GREEN_TIME
    return total


def neighbor(plan: TimingPlan) -> TimingPlan:
    new = TimingPlan(durations=dict(plan.durations))
    d = random.choice(list(Direction))
    delta = random.choice([-3, 3])
    new.durations[d] = max(
        MIN_GREEN_TIME,
        min(MAX_GREEN_TIME, new.durations[d] + delta),
    )
    return new


def optimize(state: IntersectionState,
             iterations: int = SA_ITERATIONS,
             T0: float = SA_INITIAL_TEMP,
             alpha: float = SA_COOLING) -> TimingPlan:
    current = TimingPlan(durations={d: 30 for d in Direction})
    best = current
    best_cost = cost_function(current, state)
    T = T0

    for _ in range(iterations):
        candidate = neighbor(current)
        c_cost = cost_function(candidate, state)
        delta = c_cost - best_cost
        if delta < 0 or random.random() < math.exp(-delta / max(T, 1e-9)):
            current = candidate
            if c_cost < best_cost:
                best, best_cost = candidate, c_cost
        T *= alpha
    return best
