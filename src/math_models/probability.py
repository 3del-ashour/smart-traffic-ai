"""Probability utilities — owned by Member 4."""
import math
import numpy as np


def expected_arrivals(rate: float, time: float) -> float:
    return rate * time


def poisson_pmf(k: int, rate: float, time: float) -> float:
    lam = rate * time
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def sample_arrivals(rate: float, time: float) -> int:
    return int(np.random.poisson(rate * time))
