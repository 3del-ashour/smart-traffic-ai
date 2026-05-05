"""Metrics — owned by Member 9."""
import logging

logger = logging.getLogger(__name__)


def compute_metrics(history: list) -> dict:
    if not history:
        return {}
    avg_waits = [s.avg_wait_time for s in history]
    queue_sums = [sum(s.densities.values()) for s in history]
    return {
        "mean_wait":    sum(avg_waits) / len(avg_waits),
        "min_wait":     min(avg_waits),
        "max_wait":     max(avg_waits),
        "total_passed": history[-1].total_cars_passed,
        "max_queue":    max(queue_sums),
        "mean_queue":   sum(queue_sums) / len(queue_sums),
    }