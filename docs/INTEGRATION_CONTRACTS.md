# Integration Contracts — READ BEFORE CODING

> **These are the rules of the game. Everyone follows them. No exceptions.**

If you change a function signature listed here without updating this document **and notifying the Project Manager (Member 1)**, you break everyone else's code.

---

## 1. Shared Types (`config.py`)

Everyone imports from `config.py`. Don't redefine these.

```python
# config.py
from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"

class LightState(Enum):
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"

@dataclass
class IntersectionState:
    """The single source of truth — passed everywhere."""
    densities: dict          # {Direction.NORTH: 12, ...}
    light_states: dict       # {Direction.NORTH: LightState.GREEN, ...}
    current_phase_time: int  # seconds elapsed in current phase
    cycle_number: int
    avg_wait_time: float
    total_cars_passed: int

@dataclass
class TimingPlan:
    """Output of optimizer — green durations per direction."""
    durations: dict          # {Direction.NORTH: 35, ...}

# Constants
MAX_CARS_PER_LANE = 30
MIN_GREEN_TIME = 10
MAX_GREEN_TIME = 60
SIMULATION_FPS = 30
ARRIVAL_RATE_DEFAULT = 0.3   # cars per second (Poisson lambda)
```

---

## 2. Function Signatures (FROZEN)

| Owner | Module | Function | Returns |
|-------|--------|----------|---------|
| M6 | `simulation.intersection` | `Intersection().step(dt: float)` | `IntersectionState` |
| M6 | `simulation.intersection` | `Intersection().get_state()` | `IntersectionState` |
| M6 | `simulation.intersection` | `Intersection().apply_timing(plan: TimingPlan)` | `None` |
| M6 | `simulation.intersection` | `Intersection().cycle_complete()` | `bool` |
| M3 | `logic.inference` | `decide_priority(state: IntersectionState)` | `Direction` |
| M3 | `logic.inference` | `modus_ponens(facts: set)` | `set` |
| M4 | `math_models.matrices` | `density_matrix(history: list)` | `np.ndarray` |
| M4 | `math_models.matrices` | `congestion_norm(state: IntersectionState)` | `float` |
| M4 | `math_models.matrices` | `dominant_flow(matrix: np.ndarray)` | `np.ndarray` |
| M4 | `math_models.probability` | `expected_arrivals(rate: float, time: float)` | `float` |
| M4 | `math_models.probability` | `poisson_pmf(k: int, rate: float, time: float)` | `float` |
| M4 | `math_models.probability` | `sample_arrivals(rate: float, time: float)` | `int` |
| M5 | `optimization.simulated_annealing` | `optimize(state, iterations=1000)` | `TimingPlan` |
| M2 | `agent.traffic_agent` | `TrafficAgent().act(state: IntersectionState)` | `TimingPlan` |
| M7 | `ui.renderer` | `Renderer().draw(state: IntersectionState)` | `None` |
| M8 | `ui.controls` | `Controls().handle_event(event)` | `None` |
| M9 | `evaluation.metrics` | `compute_metrics(history: list)` | `dict` |
| M9 | `evaluation.monitor` | `Monitor().record(state)` | `None` |
| M9 | `evaluation.monitor` | `Monitor().save_report(path: str)` | `None` |

---

## 3. The 10 Rules

1. **Don't change shared types in `config.py`** without group approval.
2. **Function signatures above are frozen.**
3. **Imports use absolute paths** from `src/`. Example: `from src.logic.inference import decide_priority`.
4. **Each module must include unit tests** in `tests/test_<module>.py`.
5. **UI is read-only** — only consumes `IntersectionState`. Never mutates simulation directly.
6. **Random seeds are configurable** — for reproducible demos.
7. **All code formatted with `black`** before committing.
8. **Every PR must pass `pytest`** — Member 1 will not merge if tests fail.
9. **No `print()` debugging** in final code — use Python `logging` module.
10. **No hardcoded magic numbers** — put them in `config.py`.

---

## 4. Branching Rules

- One branch per feature: `feature/<your-name>-<module>`
- Never commit to `main` directly.
- Open a Pull Request → Member 1 reviews → merge.
- Pull `main` **daily** before starting work.

---

## 5. Conflict Resolution

If two members need to change the same file, **talk in the group chat first**. The Project Manager has final say. Document any contract changes here.

---

## 6. Communication Channels

- **GitHub Issues** — task tracking + technical discussion
- **Group chat** — daily updates and quick questions
- **Stand-up meetings** — every 2 days during the 9-day sprint
