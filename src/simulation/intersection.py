"""
Intersection simulation — owned by Member 6.
See docs/member-6-simulation.md for the full implementation guide.
"""
from config import (
    IntersectionState, TimingPlan, Direction, LightState,
    ARRIVAL_RATE_DEFAULT,
)
from src.math_models.probability import sample_arrivals
from src.simulation.vehicle import Vehicle


class Intersection:
    def __init__(self, arrival_rate=ARRIVAL_RATE_DEFAULT):
        self.queues = {d: [] for d in Direction}
        self.lights = {d: LightState.RED for d in Direction}
        self.lights[Direction.NORTH] = LightState.GREEN
        self.timing = {d: 30 for d in Direction}
        self.phase_time = 0.0
        self.cycle = 0
        self.elapsed = 0.0
        self.passed = 0
        self.total_wait = 0.0
        self.current_phase_dir = Direction.NORTH
        self._just_completed_cycle = False
        self.arrival_rate = arrival_rate

    def step(self, dt: float) -> IntersectionState:
        self.elapsed += dt
        self.phase_time += dt
        self._just_completed_cycle = False

        for d in Direction:
            n = sample_arrivals(self.arrival_rate, dt)
            for _ in range(n):
                self.queues[d].append(Vehicle(d, self.elapsed))

        for d in Direction:
            for v in self.queues[d]:
                v.wait_time += dt

        if int(self.elapsed) > int(self.elapsed - dt):
            if self.queues[self.current_phase_dir]:
                v = self.queues[self.current_phase_dir].pop(0)
                self.total_wait += v.wait_time
                self.passed += 1

        if self.phase_time >= self.timing[self.current_phase_dir]:
            self._next_phase()
        return self.get_state()

    def _next_phase(self):
        order = list(Direction)
        idx = (order.index(self.current_phase_dir) + 1) % 4
        self.lights[self.current_phase_dir] = LightState.RED
        self.current_phase_dir = order[idx]
        self.lights[self.current_phase_dir] = LightState.GREEN
        self.phase_time = 0
        if idx == 0:
            self.cycle += 1
            self._just_completed_cycle = True

    def cycle_complete(self) -> bool:
        return self._just_completed_cycle

    def apply_timing(self, plan: TimingPlan) -> None:
        self.timing = dict(plan.durations)

    def set_arrival_rate(self, rate: float) -> None:
        """Update the arrival rate for traffic generation."""
        self.arrival_rate = rate

    def get_state(self) -> IntersectionState:
        avg = self.total_wait / max(1, self.passed)
        return IntersectionState(
            densities={d: len(self.queues[d]) for d in Direction},
            light_states=dict(self.lights),
            current_phase_time=int(self.phase_time),
            cycle_number=self.cycle,
            avg_wait_time=avg,
            total_cars_passed=self.passed,
        )
