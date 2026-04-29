# Member 4 — Mathematical Modeler

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Build the math foundation — **Linear Algebra + Probability**.

## You Own
- `src/math_models/matrices.py`
- `src/math_models/probability.py`
- `tests/test_math.py`

---

## Contract You Must Honor

| Function | Returns |
|----------|---------|
| `density_matrix(history: list)` | `np.ndarray` |
| `congestion_norm(state)` | `float` |
| `dominant_flow(matrix)` | `np.ndarray` |
| `expected_arrivals(rate, time)` | `float` |
| `poisson_pmf(k, rate, time)` | `float` |
| `sample_arrivals(rate, time)` | `int` |

---

## Step-by-Step Plan

### Day 1-2
- Implement `matrices.py` and `probability.py`.
- Use `numpy` for everything — no manual loops.

### Day 3
- Write unit tests.
- Verify Poisson sampling distribution looks right.

### Day 7-8
- Write the **Math chapter** of the report — include LaTeX formulas:
  - Poisson PMF: $P(k) = \frac{(\lambda t)^k e^{-\lambda t}}{k!}$
  - L2 norm: $\|v\|_2 = \sqrt{\sum v_i^2}$
  - Eigendecomposition explanation

---

## Code Skeleton

### `src/math_models/matrices.py`

```python
import numpy as np
from config import Direction, IntersectionState


def density_matrix(history: list) -> np.ndarray:
    """Rows = cycles, Columns = N, S, E, W."""
    rows = [
        [s.densities[d] for d in Direction]
        for s in history
    ]
    return np.array(rows)


def congestion_norm(state: IntersectionState) -> float:
    """L2 norm of density vector — overall congestion."""
    v = np.array([state.densities[d] for d in Direction])
    return float(np.linalg.norm(v))


def dominant_flow(matrix: np.ndarray) -> np.ndarray:
    """Eigenvector of the covariance matrix → dominant traffic pattern."""
    if matrix.shape[0] < 2:
        return np.zeros(4)
    cov = np.cov(matrix.T)
    vals, vecs = np.linalg.eig(cov)
    return vecs[:, np.argmax(vals.real)].real
```

### `src/math_models/probability.py`

```python
import math
import numpy as np


def expected_arrivals(rate: float, time: float) -> float:
    """Poisson expected value = lambda * time."""
    return rate * time


def poisson_pmf(k: int, rate: float, time: float) -> float:
    """Probability of exactly k arrivals in `time` seconds."""
    lam = rate * time
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def sample_arrivals(rate: float, time: float) -> int:
    """Sample number of arrivals from Poisson(rate*time)."""
    return int(np.random.poisson(rate * time))
```

---

## Test Stub

```python
# tests/test_math.py
import numpy as np
from config import IntersectionState, Direction, LightState
from src.math_models.matrices import congestion_norm
from src.math_models.probability import expected_arrivals, poisson_pmf

def test_norm_zero_when_empty():
    state = IntersectionState(
        densities={d: 0 for d in Direction},
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=0,
        avg_wait_time=0, total_cars_passed=0,
    )
    assert congestion_norm(state) == 0.0

def test_expected_arrivals():
    assert expected_arrivals(0.3, 10) == 3.0

def test_poisson_pmf_sums_to_one():
    s = sum(poisson_pmf(k, 0.3, 10) for k in range(40))
    assert abs(s - 1.0) < 1e-3
```

---

## Best Practices
- Use `numpy` everywhere — no manual loops for math.
- Document the math in the report with formulas (LaTeX).
- Test that probabilities sum to 1 — proves correctness.

---

## AI Prompt You Can Paste

> "Implement linear algebra and probability utilities for a traffic-light AI in Python. I need: density_matrix(history) returning np.ndarray; congestion_norm(state) returning L2 norm float; dominant_flow(matrix) returning the eigenvector with max eigenvalue; expected_arrivals(rate, time); poisson_pmf(k, rate, time); sample_arrivals(rate, time). Use numpy. Include pytest unit tests."
