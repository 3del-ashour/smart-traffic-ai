"""Traffic generator — wraps Poisson sampling. Owned by Member 6."""
from src.math_models.probability import sample_arrivals


def generate_arrivals(rate: float, dt: float) -> int:
    return sample_arrivals(rate, dt)
