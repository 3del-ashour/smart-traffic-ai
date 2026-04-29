# Member 5 — Optimization Specialist

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Implement **Simulated Annealing** to find the best green-light timings.

## You Own
- `src/optimization/simulated_annealing.py`
- `tests/test_optimization.py`

---

## Contract You Must Honor

| Function | Returns |
|----------|---------|
| `optimize(state, iterations=1000)` | `TimingPlan` |

---

## Step-by-Step Plan

### Day 1-2
- Define cost function (total wait time).
- Implement basic SA loop.

### Day 3
- Tune cooling schedule (`T0`, `alpha`).
- Plot cost-over-iterations chart.

### Day 4
- Write unit tests verifying cost decreases over time.

### Day 7-8
- Write the **Optimization chapter** of the report:
  - Pseudocode of SA
  - Cost function explanation
  - Cooling schedule plot
  - Comparison: SA vs random search

---

## Code Skeleton

```python
# src/optimization/simulated_annealing.py
import math
import random
from config import (
    TimingPlan, Direction, IntersectionState,
    MIN_GREEN_TIME, MAX_GREEN_TIME,
)


def cost_function(plan: TimingPlan, state: IntersectionState) -> float:
    """Estimated total wait time given current densities and a plan."""
    total = 0.0
    for d in Direction:
        density = state.densities[d]
        green = plan.durations[d]
        # high density + low green time = high wait
        total += density * (MAX_GREEN_TIME - green) / MAX_GREEN_TIME
    return total


def neighbor(plan: TimingPlan) -> TimingPlan:
    """Tweak one random direction's green time by +/- 3 seconds."""
    new = TimingPlan(durations=dict(plan.durations))
    d = random.choice(list(Direction))
    delta = random.choice([-3, 3])
    new.durations[d] = max(
        MIN_GREEN_TIME,
        min(MAX_GREEN_TIME, new.durations[d] + delta),
    )
    return new


def optimize(state: IntersectionState, iterations: int = 1000,
             T0: float = 10.0, alpha: float = 0.95) -> TimingPlan:
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
```

---

## Test Stub

```python
# tests/test_optimization.py
from config import IntersectionState, Direction, LightState
from src.optimization.simulated_annealing import optimize, cost_function
from config import TimingPlan

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
```

---

## Best Practices
- Keep cost function fast — it runs thousands of times.
- Plot cost-over-iterations chart for the report.
- Try different cooling schedules and document which works best.

---

## AI Prompt You Can Paste

> "Implement Simulated Annealing in Python for traffic-light timing optimization. Cost function = total expected wait time. Decision variables = green durations per direction (N, S, E, W), bounded [10, 60] seconds. Use exponential cooling (T *= alpha each iteration). Expose `optimize(state, iterations) -> TimingPlan`. Include pytest tests verifying cost improves over iterations."
