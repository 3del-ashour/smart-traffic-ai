"""
Intersection simulation — owned by Member 6 (Abdulrahman).
See docs/member-6-simulation.md for the full implementation guide.

Provides the simulated 4-way intersection used by the rest of the system:
  - Stochastic Poisson arrivals (Member 4 math model)
  - Per-lane queues with bounded capacity (MAX_CARS_PER_LANE)
  - Phase rotation driven by TimingPlan from the agent (Member 2 / Member 5)
  - Telemetry for evaluation (Member 9): peak_density, total_wait, passed
"""
import logging

from config import (
    ARRIVAL_RATE_DEFAULT,
    Direction,
    IntersectionState,
    LightState,
    MAX_CARS_PER_LANE,
    TimingPlan,
)
from src.math_models.probability import sample_arrivals
from src.simulation.vehicle import Vehicle

# Telemetry logger for technical monitoring (used by Member 9 monitor)
logger = logging.getLogger(__name__)


class Intersection:
    """4-way simulation engine with congestion telemetry."""

    def __init__(self, arrival_rate: float = ARRIVAL_RATE_DEFAULT):
        self.queues = {d: [] for d in Direction}
        self.lights = {d: LightState.RED for d in Direction}
        self.lights[Direction.NORTH] = LightState.GREEN
        self.timing = {d: 30 for d in Direction}

        # Phase / clock state
        self.phase_time = 0.0
        self.cycle = 0
        self.elapsed = 0.0
        self.current_phase_dir = Direction.NORTH
        self._just_completed_cycle = False

        # Arrival model (live-tunable from the dashboard)
        self.arrival_rate = arrival_rate

        # Telemetry
        self.passed = 0
        self.total_wait = 0.0
        self.peak_density = 0

    # ------------------------------------------------------------------
    # Main step
    # ------------------------------------------------------------------
    def step(self, dt: float) -> IntersectionState:
        """High-frequency state update (typically 30 FPS)."""
        self.elapsed += dt
        self.phase_time += dt
        self._just_completed_cycle = False

        # 1. Stochastic Poisson arrivals — capped at MAX_CARS_PER_LANE
        for d in Direction:
            free = MAX_CARS_PER_LANE - len(self.queues[d])
            if free > 0:
                n = sample_arrivals(self.arrival_rate, dt)
                for _ in range(min(n, free)):
                    self.queues[d].append(Vehicle(d, self.elapsed))
            # Track worst-case congestion for the evaluation report
            self.peak_density = max(self.peak_density, len(self.queues[d]))

        # 2. Accumulate wait time for every queued vehicle
        for d in Direction:
            for v in self.queues[d]:
                v.wait_time += dt

        # 3. Throughput on the green lane (1 car / sec)
        if int(self.elapsed) > int(self.elapsed - dt):
            if self.queues[self.current_phase_dir]:
                v = self.queues[self.current_phase_dir].pop(0)
                self.total_wait += v.wait_time
                self.passed += 1

        # 4. Phase transition when the timer expires
        if self.phase_time >= self.timing[self.current_phase_dir]:
            self._next_phase()

        return self.get_state()

    # ------------------------------------------------------------------
    # Phase transition
    # ------------------------------------------------------------------
    def _next_phase(self):
        """Rotate green light to the next direction (round-robin)."""
        order = list(Direction)
        idx = (order.index(self.current_phase_dir) + 1) % 4

        logger.info(
            "Transition: %s -> %s",
            self.current_phase_dir.name,
            order[idx].name,
        )

        self.lights[self.current_phase_dir] = LightState.RED
        self.current_phase_dir = order[idx]
        self.lights[self.current_phase_dir] = LightState.GREEN
        self.phase_time = 0

        if idx == 0:
            self.cycle += 1
            self._just_completed_cycle = True

    # Backwards-compatible alias (some tests / docs reference this name)
    def _transition_phase(self):
        self._next_phase()

    # ------------------------------------------------------------------
    # Public API used by Agent (Member 2) and Controls (Member 8)
    # ------------------------------------------------------------------
    def cycle_complete(self) -> bool:
        """True for one tick after every full 4-way rotation — agent re-plans here."""
        return self._just_completed_cycle

    def apply_timing(self, plan: TimingPlan) -> None:
        """Inject the optimised TimingPlan from Simulated Annealing (Member 5)."""
        self.timing = dict(plan.durations)

    def set_arrival_rate(self, rate: float) -> None:
        """Update arrival rate live from the dashboard slider (Member 8)."""
        self.arrival_rate = rate

    def get_state(self) -> IntersectionState:
        """The single source of truth — passed to AI and UI every tick."""
        avg = self.total_wait / max(1, self.passed)
        return IntersectionState(
            densities={d: len(self.queues[d]) for d in Direction},
            light_states=dict(self.lights),
            current_phase_time=int(self.phase_time),
            cycle_number=self.cycle,
            avg_wait_time=round(avg, 2),
            total_cars_passed=self.passed,
        )
