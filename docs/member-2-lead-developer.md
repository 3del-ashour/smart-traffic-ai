# Member 2 — Lead Developer (Agent Architect)

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Build the **rational agent** — the brain that ties Logic + Math + Optimization together.

## You Own
- `src/agent/traffic_agent.py`
- `tests/test_agent.py`

---

## Contract You Must Honor

| Function | Returns |
|----------|---------|
| `TrafficAgent().act(state: IntersectionState)` | `TimingPlan` |

---

## Step-by-Step Plan

### Day 1
- Create branch `feature/<your-name>-agent`.
- Write skeleton of `TrafficAgent` class.
- Push empty implementation that returns a default `TimingPlan`.

### Day 2-4
- Implement `perceive → decide → act` loop.
- Call out to Logic, Math, Optimization modules.
- Add history tracking.

### Day 5-6
- Integration testing with the real modules.
- Tune the agent's decision-making.

### Day 7-8
- Write the **Agent chapter** of the report.

---

## Code Skeleton

```python
# src/agent/traffic_agent.py
from config import IntersectionState, TimingPlan, Direction, ARRIVAL_RATE_DEFAULT
from src.logic.inference import decide_priority
from src.math_models.matrices import congestion_norm
from src.math_models.probability import expected_arrivals
from src.optimization.simulated_annealing import optimize


class TrafficAgent:
    """Rational agent: perceives state, decides next timing plan."""

    def __init__(self):
        self.history = []           # list of past IntersectionStates
        self.current_plan = None

    def perceive(self, state: IntersectionState):
        self.history.append(state)

    def decide(self, state: IntersectionState) -> TimingPlan:
        # 1. Logic — which direction is most urgent?
        priority_dir = decide_priority(state)

        # 2. Math — predict arrivals next cycle
        predicted = {
            d: expected_arrivals(rate=ARRIVAL_RATE_DEFAULT, time=30)
            for d in Direction
        }

        # 3. Optimization — find the best timing
        plan = optimize(state, iterations=500)

        # 4. Logic override — bias toward the priority direction
        plan.durations[priority_dir] = min(
            plan.durations[priority_dir] + 5, 60
        )
        return plan

    def act(self, state: IntersectionState) -> TimingPlan:
        self.perceive(state)
        plan = self.decide(state)
        self.current_plan = plan
        return plan
```

---

## Test Stub

```python
# tests/test_agent.py
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
```

---

## Best Practices
- Keep the agent **small** — it orchestrates, it doesn't contain logic.
- Log every decision (use `logging`) for the report.
- Don't put math/logic/optimization code inside the agent — call modules.

---

## AI Prompt You Can Paste

> "I'm building the rational-agent class for a Smart Traffic AI project. Implement `TrafficAgent` in Python following perceive-decide-act, calling out to logic, math, and optimization modules with these exact signatures: [paste INTEGRATION_CONTRACTS.md Section 2]. Include unit tests with pytest. State dataclass: IntersectionState with fields densities, light_states, current_phase_time, cycle_number, avg_wait_time, total_cars_passed."
