# Member 9 — Evaluation & Monitoring Specialist

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Measure performance, produce graphs, run **AI vs Fixed-timer** comparison for the report.

## You Own
- `src/evaluation/metrics.py`
- `src/evaluation/monitor.py`
- `tests/test_evaluation.py`
- The comparison plot script

---

## Contract You Must Honor

| Function | Returns |
|----------|---------|
| `compute_metrics(history: list)` | `dict` |
| `Monitor().record(state)` | `None` |
| `Monitor().save_report(path: str)` | `None` |

---

## Step-by-Step Plan

### Day 2-3
- Implement `Monitor` and `metrics.py`.
- Save state history to CSV.

### Day 4-5
- Run AI mode for 5 min simulated → save metrics.
- Run Fixed mode for 5 min simulated → save metrics.

### Day 6
- Plot comparison with matplotlib.
- Generate the **headline chart** for the report.

### Day 7-8
- Write the **Evaluation chapter** of the report:
  - Description of metrics
  - AI vs Fixed comparison plots
  - Tables of numerical results

---

## Code Skeleton

### `src/evaluation/metrics.py`

```python
def compute_metrics(history: list) -> dict:
    if not history:
        return {}
    avg_waits = [s.avg_wait_time for s in history]
    queue_sums = [sum(s.densities.values()) for s in history]
    return {
        "mean_wait":     sum(avg_waits) / len(avg_waits),
        "min_wait":      min(avg_waits),
        "max_wait":      max(avg_waits),
        "total_passed":  history[-1].total_cars_passed,
        "max_queue":     max(queue_sums),
        "mean_queue":    sum(queue_sums) / len(queue_sums),
    }
```

### `src/evaluation/monitor.py`

```python
import csv
from config import Direction


class Monitor:
    def __init__(self):
        self.history = []

    def record(self, state) -> None:
        self.history.append(state)

    def save_report(self, path: str) -> None:
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "cycle", "phase_time", "avg_wait", "passed",
                "qN", "qS", "qE", "qW",
            ])
            for s in self.history:
                w.writerow([
                    s.cycle_number, s.current_phase_time,
                    f"{s.avg_wait_time:.3f}", s.total_cars_passed,
                    s.densities[Direction.NORTH],
                    s.densities[Direction.SOUTH],
                    s.densities[Direction.EAST],
                    s.densities[Direction.WEST],
                ])
```

### Comparison plot script — `scripts/plot_compare.py`

```python
"""Run main.py twice (AI mode + Fixed mode) → compare wait times."""
import csv
import matplotlib.pyplot as plt


def load(path):
    cycles, waits = [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cycles.append(int(row["cycle"]))
            waits.append(float(row["avg_wait"]))
    return cycles, waits


def main():
    ai_x, ai_y = load("docs/metrics_ai.csv")
    fx_x, fx_y = load("docs/metrics_fixed.csv")

    plt.figure(figsize=(10, 5))
    plt.plot(ai_x, ai_y, label="AI Agent (Simulated Annealing)", color="#1abc9c")
    plt.plot(fx_x, fx_y, label="Fixed Timer", color="#e74c3c", linestyle="--")
    plt.xlabel("Cycle")
    plt.ylabel("Average Wait Time (s)")
    plt.title("AI vs Fixed Timer — Average Wait")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig("docs/comparison_plot.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
```

---

## Test Stub

```python
# tests/test_evaluation.py
from config import IntersectionState, Direction, LightState
from src.evaluation.metrics import compute_metrics

def test_metrics_empty():
    assert compute_metrics([]) == {}

def test_metrics_basic():
    s = IntersectionState(
        densities={d: 2 for d in Direction},
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=1,
        avg_wait_time=5.0, total_cars_passed=10,
    )
    m = compute_metrics([s, s, s])
    assert m["mean_wait"] == 5.0
    assert m["total_passed"] == 10
```

---

## Best Practices
- Run experiments with the **same random seed** for fair comparison.
- Include charts in the final report — they are the most convincing evidence.
- Run experiments multiple times and report mean + std deviation.

---

## AI Prompt You Can Paste

> "Implement evaluation + monitoring for a traffic-AI simulation in Python. Track avg wait time, throughput, max queue length. Save state history to CSV. Provide compute_metrics(history) returning a dict with mean_wait, min_wait, max_wait, total_passed, max_queue, mean_queue. Also write a matplotlib comparison plot script that loads two CSVs (AI vs Fixed) and plots avg wait over cycle."
