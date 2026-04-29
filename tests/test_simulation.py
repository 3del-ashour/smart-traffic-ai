import random
from config import TimingPlan, Direction
from src.simulation.intersection import Intersection


def test_intersection_step_returns_state():
    random.seed(42)
    inter = Intersection()
    s = inter.step(0.1)
    assert s.total_cars_passed >= 0
    assert sum(s.densities.values()) >= 0


def test_apply_timing():
    inter = Intersection()
    plan = TimingPlan(durations={d: 25 for d in Direction})
    inter.apply_timing(plan)
    assert inter.timing[Direction.NORTH] == 25
