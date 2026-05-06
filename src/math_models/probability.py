"""Probability utilities — owned by Member 4."""

import math
import numpy as np


def expected_arrivals(rate: float, time: float) -> float:
    """Poisson expected value = lambda * time."""
    if rate < 0:
        raise ValueError(f"rate must be >= 0, got {rate}")
    if time < 0:
        raise ValueError(f"time must be >= 0, got {time}")
    return rate * time


def poisson_pmf(k: int, rate: float, time: float) -> float:
    """Probability of exactly k arrivals in `time` seconds.

    Uses log-space arithmetic to avoid overflow for large k or large lambda.
    """
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    if rate < 0:
        raise ValueError(f"rate must be >= 0, got {rate}")
    if time < 0:
        raise ValueError(f"time must be >= 0, got {time}")
    lam = rate * time
    if lam == 0.0:
        return 1.0 if k == 0 else 0.0
    log_pmf = k * math.log(lam) - lam - math.lgamma(k + 1)
    return math.exp(log_pmf)


def sample_arrivals(rate: float, time: float) -> int:
    """Sample number of arrivals from Poisson(rate * time)."""
    if rate < 0:
        raise ValueError(f"rate must be >= 0, got {rate}")
    if time < 0:
        raise ValueError(f"time must be >= 0, got {time}")
    return int(np.random.poisson(rate * time))
