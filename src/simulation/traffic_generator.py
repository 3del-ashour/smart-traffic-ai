"""
Traffic generator — owned by Member 6 (Abdulrahman).

Thin wrapper around Member 4's Poisson sampler. Adds a `burst` mode that
triples the arrival rate, which is useful for stress-testing the AI from
the dashboard during the live demo.
"""
from src.math_models.probability import sample_arrivals


def generate_arrivals(rate: float, dt: float, burst: bool = False) -> int:
    """Number of cars arriving in `dt` seconds at the given Poisson rate.

    If `burst` is True the effective rate is tripled — used for
    high-congestion demo scenarios.
    """
    effective_rate = rate * 3 if burst else rate
    return sample_arrivals(effective_rate, dt)
