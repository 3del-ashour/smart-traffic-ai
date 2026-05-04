"""
Rational traffic agent — owned by Member 2 (Ahmet Cemil Bostanoglu).

Orchestration layer that connects the three AI pillars:
  * Logic engine          (src.logic.inference)              -> priority decision
  * Math models           (src.math_models.*)                -> arrivals + congestion
  * Optimization engine   (src.optimization.simulated_annealing) -> SA timing search

Conceptual pipeline:  state -> perceive -> decide -> act -> TimingPlan

If a teammate module is missing or raises at runtime, a safe internal fallback
keeps the agent producing a valid TimingPlan so the integration in main.py
never crashes during the demo.
"""
from __future__ import annotations

import logging
import math
from typing import Optional

from config import (
    ARRIVAL_RATE_DEFAULT,
    Direction,
    IntersectionState,
    MAX_GREEN_TIME,
    MIN_GREEN_TIME,
    TimingPlan,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Safe imports of teammate modules.
# Each binding is wrapped so that an ImportError in another teammate's area
# never breaks the agent. A minimal local fallback is registered instead.
# ---------------------------------------------------------------------------

try:
    from src.logic.inference import decide_priority as _logic_decide_priority

    _HAS_LOGIC = True
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("Logic module unavailable, using density-max fallback: %s", exc)
    _HAS_LOGIC = False

    def _logic_decide_priority(state: IntersectionState) -> Direction:
        return max(Direction, key=lambda d: state.densities.get(d, 0))


try:
    from src.math_models.probability import expected_arrivals as _math_expected_arrivals

    _HAS_PROB = True
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("Probability module unavailable, using lambda*t fallback: %s", exc)
    _HAS_PROB = False

    def _math_expected_arrivals(rate: float, time: float) -> float:
        return float(rate) * float(time)


try:
    from src.math_models.matrices import congestion_norm as _math_congestion_norm

    _HAS_MATRIX = True
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("Matrices module unavailable, using L2-of-densities fallback: %s", exc)
    _HAS_MATRIX = False

    def _math_congestion_norm(state: IntersectionState) -> float:
        return math.sqrt(sum(int(v) ** 2 for v in state.densities.values()))


try:
    from src.optimization.simulated_annealing import optimize as _opt_optimize

    _HAS_OPT = True
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("Optimization module unavailable, using density-weighted fallback: %s", exc)
    _HAS_OPT = False

    def _opt_optimize(state: IntersectionState, iterations: int = 500) -> TimingPlan:
        # Distribute green time proportional to density across the legal range.
        total = sum(state.densities.values()) or 1
        span = MAX_GREEN_TIME - MIN_GREEN_TIME
        durations = {
            d: int(MIN_GREEN_TIME + (state.densities.get(d, 0) / total) * span)
            for d in Direction
        }
        return TimingPlan(durations=durations)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def _default_plan() -> TimingPlan:
    mid = (MIN_GREEN_TIME + MAX_GREEN_TIME) // 2
    return TimingPlan(durations={d: mid for d in Direction})


def _snapshot(state: IntersectionState) -> IntersectionState:
    """Defensive copy so the agent never mutates the caller's state."""
    return IntersectionState(
        densities=dict(state.densities),
        light_states=dict(state.light_states),
        current_phase_time=state.current_phase_time,
        cycle_number=state.cycle_number,
        avg_wait_time=state.avg_wait_time,
        total_cars_passed=state.total_cars_passed,
    )


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class TrafficAgent:
    """Rational agent: orchestrates Logic + Math + Optimization into a TimingPlan."""

    def __init__(
        self,
        priority_boost: int = 5,
        sa_iterations: int = 500,
        arrival_rate: float = ARRIVAL_RATE_DEFAULT,
        history_limit: int = 200,
    ) -> None:
        self.history: list = []
        self.current_plan: Optional[TimingPlan] = None
        self.priority_boost = int(priority_boost)
        self.sa_iterations = int(sa_iterations)
        self.arrival_rate = float(arrival_rate)
        self.history_limit = int(history_limit)
        # Last priority direction picked by decide() — exposed for logging/tests.
        self.last_priority: Optional[Direction] = None

    # ----- pipeline ---------------------------------------------------------

    def perceive(self, state: IntersectionState) -> None:
        """Record the observation. Bounded history avoids unbounded growth."""
        self._validate_state(state)
        self.history.append(state)
        if len(self.history) > self.history_limit:
            del self.history[: len(self.history) - self.history_limit]

    def decide(self, state: IntersectionState) -> TimingPlan:
        """Build a TimingPlan by combining the three AI pillars."""
        # 1) LOGIC — modus-ponens-based priority
        try:
            priority_dir = _logic_decide_priority(state)
            if priority_dir not in Direction:
                raise ValueError(f"Logic returned non-Direction: {priority_dir!r}")
        except Exception as exc:
            logger.warning("Logic priority failed (%s); falling back to max density", exc)
            priority_dir = max(Direction, key=lambda d: state.densities.get(d, 0))
        self.last_priority = priority_dir

        # 2) MATH — expected arrivals during a max-length green window.
        # Kept for monitoring/report; congestion norm summarises pressure.
        try:
            predicted = {
                d: _math_expected_arrivals(self.arrival_rate, MAX_GREEN_TIME)
                for d in Direction
            }
            congestion = _math_congestion_norm(state)
            logger.debug(
                "math: congestion=%.2f predicted=%s", congestion, predicted
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Math models failed (%s); ignoring", exc)

        # 3) OPTIMIZATION — simulated annealing on green-light durations
        try:
            plan = _opt_optimize(state, iterations=self.sa_iterations)
        except TypeError:
            # Some optimize() variants may not accept iterations kwarg.
            try:
                plan = _opt_optimize(state)
            except Exception as exc:
                logger.warning("Optimizer failed (%s); using default plan", exc)
                plan = _default_plan()
        except Exception as exc:
            logger.warning("Optimizer failed (%s); using default plan", exc)
            plan = _default_plan()

        if not isinstance(plan, TimingPlan) or not getattr(plan, "durations", None):
            logger.warning("Optimizer returned invalid plan; using default")
            plan = _default_plan()

        # 4) LOGIC OVERRIDE — bias the priority direction. Build a fresh dict
        # so we never mutate the optimizer's returned TimingPlan in place.
        durations = dict(plan.durations)
        for d in Direction:
            durations.setdefault(d, (MIN_GREEN_TIME + MAX_GREEN_TIME) // 2)
        durations[priority_dir] = durations[priority_dir] + self.priority_boost

        # 5) BOUND — every duration must respect the legal contract
        bounded = {
            d: _clamp(durations[d], MIN_GREEN_TIME, MAX_GREEN_TIME)
            for d in Direction
        }
        return TimingPlan(durations=bounded)

    def act(self, state: IntersectionState) -> TimingPlan:
        """Public API. perceive -> decide, remember and return the plan."""
        self._validate_state(state)
        # Snapshot first so neither perceive() nor decide() can leak mutations
        # back into the caller's IntersectionState instance.
        snapshot = _snapshot(state)
        self.perceive(snapshot)
        plan = self.decide(snapshot)
        self.current_plan = plan
        logger.info(
            "act cycle=%s priority=%s plan=%s",
            snapshot.cycle_number,
            self.last_priority.value if self.last_priority else None,
            {d.value: plan.durations[d] for d in Direction},
        )
        return plan

    # ----- validation -------------------------------------------------------

    @staticmethod
    def _validate_state(state: IntersectionState) -> None:
        if state is None:
            raise ValueError("IntersectionState must not be None")
        for attr in ("densities", "light_states"):
            if not hasattr(state, attr) or getattr(state, attr) is None:
                raise ValueError(f"IntersectionState missing field: {attr}")
        for d in Direction:
            if d not in state.densities:
                raise ValueError(f"IntersectionState.densities missing direction {d}")
            if not isinstance(state.densities[d], (int, float)):
                raise ValueError(f"IntersectionState.densities[{d}] must be numeric")
            if state.densities[d] < 0:
                raise ValueError(f"IntersectionState.densities[{d}] must be >= 0")
