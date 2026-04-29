"""Rational agent — owned by Member 2."""
from config import IntersectionState, TimingPlan, Direction, ARRIVAL_RATE_DEFAULT, MAX_GREEN_TIME
from src.logic.inference import decide_priority
from src.math_models.probability import expected_arrivals
from src.optimization.simulated_annealing import optimize


class TrafficAgent:
    def __init__(self):
        self.history = []
        self.current_plan = None

    def perceive(self, state: IntersectionState):
        self.history.append(state)

    def decide(self, state: IntersectionState) -> TimingPlan:
        priority_dir = decide_priority(state)

        # predict arrivals next cycle (used in report — not yet wired into cost)
        _ = {
            d: expected_arrivals(rate=ARRIVAL_RATE_DEFAULT, time=30)
            for d in Direction
        }

        plan = optimize(state)
        plan.durations[priority_dir] = min(
            plan.durations[priority_dir] + 5, MAX_GREEN_TIME
        )
        return plan

    def act(self, state: IntersectionState) -> TimingPlan:
        self.perceive(state)
        plan = self.decide(state)
        self.current_plan = plan
        return plan
