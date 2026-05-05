"""Monitor — owned by Member 9."""
import csv
import os
import logging
from config import Direction

logger = logging.getLogger(__name__)


class Monitor:
    def __init__(self):
        self.history = []

    def record(self, state) -> None:
        self.history.append(state)
        logger.debug(f"Recorded state — cycle {state.cycle_number}")

    def save_report(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "cycle", "phase_time", "avg_wait", "passed",
                "qN", "qS", "qE", "qW",
            ])
            for s in self.history:
                w.writerow([
                    s.cycle_number,
                    s.current_phase_time,
                    f"{s.avg_wait_time:.3f}",
                    s.total_cars_passed,
                    s.densities[Direction.NORTH],
                    s.densities[Direction.SOUTH],
                    s.densities[Direction.EAST],
                    s.densities[Direction.WEST],
                ])
        logger.info(f"Report saved to {path}")