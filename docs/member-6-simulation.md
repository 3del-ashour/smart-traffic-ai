# Member 6 — Simulation Engineer

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Build the **simulated world** — the intersection, the cars, and the traffic generator.

## You Own
- `src/simulation/intersection.py`
- `src/simulation/vehicle.py`
- `src/simulation/traffic_generator.py`
- `tests/test_simulation.py`

---

## Contract You Must Honor

| Function | Returns |
|----------|---------|
| `Intersection().step(dt: float)` | `IntersectionState` |
| `Intersection().get_state()` | `IntersectionState` |
| `Intersection().apply_timing(plan: TimingPlan)` | `None` |
| `Intersection().cycle_complete()` | `bool` |

---

## Step-by-Step Plan

### Day 1-2
- Create `Vehicle` class.
- Build core `Intersection` class with phase rotation.
- Use Member 4's `sample_arrivals` for Poisson traffic.

### Day 3
- Implement `apply_timing` and `cycle_complete`.
- Make sure simulation is deterministic with a fixed seed.

### Day 4
- Write unit tests.
- Verify Poisson-based arrivals work.

### Day 7-8
- Help write the simulation section of the report.

---

## Code Skeleton

### `src/simulation/vehicle.py`

```python
class Vehicle:
    def __init__(self, direction, spawn_time):
        self.direction = direction
        self.spawn_time = spawn_time
        self.wait_time = 0.0
```

### `src/simulation/intersection.py`

```python
from config import (
    IntersectionState, TimingPlan, Direction, LightState,
    ARRIVAL_RATE_DEFAULT,
)
from src.math_models.probability import sample_arrivals
from src.simulation.vehicle import Vehicle


class Intersection:
    def __init__(self):
        self.queues = {d: [] for d in Direction}
        self.lights = {d: LightState.RED for d in Direction}
        self.lights[Direction.NORTH] = LightState.GREEN
        self.timing = {d: 30 for d in Direction}
        self.phase_time = 0.0
        self.cycle = 0
        self.elapsed = 0.0
        self.passed = 0
        self.total_wait = 0.0
        self.current_phase_dir = Direction.NORTH
        self._just_completed_cycle = False

    def step(self, dt: float) -> IntersectionState:
        self.elapsed += dt
        self.phase_time += dt
        self._just_completed_cycle = False

        # 1. Spawn arrivals (Poisson)
        for d in Direction:
            n = sample_arrivals(ARRIVAL_RATE_DEFAULT, dt)
            for _ in range(n):
                self.queues[d].append(Vehicle(d, self.elapsed))

        # 2. Increment wait time for waiting cars
        for d in Direction:
            for v in self.queues[d]:
                v.wait_time += dt

        # 3. Pass cars on the green light (1 per second)
        if int(self.elapsed) > int(self.elapsed - dt):
            if self.queues[self.current_phase_dir]:
                v = self.queues[self.current_phase_dir].pop(0)
                self.total_wait += v.wait_time
                self.passed += 1

        # 4. End of phase?
        if self.phase_time >= self.timing[self.current_phase_dir]:
            self._next_phase()
        return self.get_state()

    def _next_phase(self):
        order = list(Direction)
        idx = (order.index(self.current_phase_dir) + 1) % 4
        self.lights[self.current_phase_dir] = LightState.RED
        self.current_phase_dir = order[idx]
        self.lights[self.current_phase_dir] = LightState.GREEN
        self.phase_time = 0
        if idx == 0:
            self.cycle += 1
            self._just_completed_cycle = True

    def cycle_complete(self) -> bool:
        return self._just_completed_cycle

    def apply_timing(self, plan: TimingPlan) -> None:
        self.timing = dict(plan.durations)

    def get_state(self) -> IntersectionState:
        avg = self.total_wait / max(1, self.passed)
        return IntersectionState(
            densities={d: len(self.queues[d]) for d in Direction},
            light_states=dict(self.lights),
            current_phase_time=int(self.phase_time),
            cycle_number=self.cycle,
            avg_wait_time=avg,
            total_cars_passed=self.passed,
        )
```

### `src/simulation/traffic_generator.py`

```python
"""Wraps Member 4's Poisson sampling for clarity in the report."""
from src.math_models.probability import sample_arrivals


def generate_arrivals(rate: float, dt: float) -> int:
    return sample_arrivals(rate, dt)
```

---

## Test Stub

```python
# tests/test_simulation.py
import random
from src.simulation.intersection import Intersection

def test_intersection_step_returns_state():
    random.seed(42)
    inter = Intersection()
    s = inter.step(0.1)
    assert s.total_cars_passed >= 0
    assert sum(s.densities.values()) >= 0

def test_apply_timing():
    from config import TimingPlan, Direction
    inter = Intersection()
    plan = TimingPlan(durations={d: 25 for d in Direction})
    inter.apply_timing(plan)
    assert inter.timing[Direction.NORTH] == 25
```

---

## Best Practices
- Simulation must be **deterministic** with a fixed random seed (for testing).
- Don't put rendering inside simulation — only state.
- Keep `step(dt)` fast — it runs at 30 FPS.

---

## AI Prompt You Can Paste

> "Build a 4-way intersection traffic simulation in Python. Cars arrive via Poisson distribution (use src.math_models.probability.sample_arrivals). Implement an Intersection class with methods step(dt), apply_timing(plan), get_state(), cycle_complete(). State dataclass IntersectionState has fields: densities (dict Direction → int), light_states (dict Direction → LightState), current_phase_time (int), cycle_number (int), avg_wait_time (float), total_cars_passed (int). Include pytest tests."
