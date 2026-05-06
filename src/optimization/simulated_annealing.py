"""
Simulated Annealing Optimizer — Member 5 (Kürşat Bayram)

Matches the report exactly:
  - Initial Temperature : T₀ = 100.0
  - Cooling rate        : α  = 0.99  (T → T × α each iteration)
  - Iterations          : 1000
  - Convergence         : ~35-40 % wait-time reduction vs. fixed timers

Algorithm (from report pseudocode):
  1. Start from a neutral plan (30 s per direction).
  2. Perturb: randomly tweak one direction by ±Δ seconds.
  3. Compute ΔCost = Cost(candidate) - Cost(current).
  4. Accept if ΔCost < 0  OR  with probability exp(-ΔCost / T).
  5. Cool: T ← T × α.
  6. Return the best plan ever seen.
"""
import math
import random
from config import (
    Direction,
    IntersectionState,
    MAX_GREEN_TIME,
    MIN_GREEN_TIME,
    SA_COOLING,
    SA_INITIAL_TEMP,
    SA_ITERATIONS,
    TimingPlan,
)


# ---------------------------------------------------------------------------
# Cost function
# ---------------------------------------------------------------------------

def cost_function(plan: TimingPlan, state: IntersectionState) -> float:
    """
    C = Σ [ ρ_d × (MAX_GREEN - G_d) / MAX_GREEN ]

    Penalises plans that give insufficient green time to high-density lanes.
    Lower is better.
    """
    total = 0.0
    for d in Direction:
        density = state.densities.get(d, 0)
        green = plan.durations.get(d, MIN_GREEN_TIME)
        total += density * (MAX_GREEN_TIME - green) / MAX_GREEN_TIME
    return total


# ---------------------------------------------------------------------------
# Random-search baseline (used for comparison chart in report)
# ---------------------------------------------------------------------------

def random_search(state: IntersectionState,
                  iterations: int = SA_ITERATIONS) -> tuple:
    """
    Pure random search baseline.
    Returns (best_plan, cost_history) for comparison plots.
    """
    best = TimingPlan(durations={d: 30 for d in Direction})
    best_cost = cost_function(best, state)
    history = []

    for _ in range(iterations):
        candidate = TimingPlan(durations={
            d: random.randint(MIN_GREEN_TIME, MAX_GREEN_TIME)
            for d in Direction
        })
        c_cost = cost_function(candidate, state)
        if c_cost < best_cost:
            best, best_cost = candidate, c_cost
        history.append(best_cost)

    return best, history


# ---------------------------------------------------------------------------
# Neighbour / perturbation
# ---------------------------------------------------------------------------

def _perturb(plan: TimingPlan, step: int = 3) -> TimingPlan:
    """
    Perturb one randomly chosen direction by ±step seconds.
    Result is clamped to [MIN_GREEN_TIME, MAX_GREEN_TIME].
    """
    new = TimingPlan(durations=dict(plan.durations))
    d = random.choice(list(Direction))
    delta = random.choice([-step, step])
    new.durations[d] = max(
        MIN_GREEN_TIME,
        min(MAX_GREEN_TIME, new.durations[d] + delta),
    )
    return new


# ---------------------------------------------------------------------------
# Simulated Annealing
# ---------------------------------------------------------------------------

def optimize(
    state: IntersectionState,
    iterations: int = SA_ITERATIONS,
    T0: float = SA_INITIAL_TEMP,
    alpha: float = SA_COOLING,
    return_history: bool = False,
) -> TimingPlan:
    """
    Simulated Annealing optimiser — matches report pseudocode exactly.

    Parameters
    ----------
    state      : current intersection state (densities drive the cost)
    iterations : number of SA steps            (default 1000)
    T0         : initial temperature            (default 100.0)
    alpha      : cooling rate  T ← T × alpha   (default 0.99)
    return_history : if True, returns (TimingPlan, cost_history list)

    Returns
    -------
    TimingPlan with best green-light durations found.
    """
    # Initialise — neutral plan (30 s per direction)
    current = TimingPlan(durations={d: 30 for d in Direction})
    best = current
    current_cost = cost_function(current, state)
    best_cost = current_cost
    T = T0

    cost_history = []   # for convergence plot

    for _ in range(iterations):
        # Perturb
        candidate = _perturb(current)
        candidate_cost = cost_function(candidate, state)

        delta = candidate_cost - current_cost

        # Accept?
        if delta < 0:
            # Better solution → always accept
            current = candidate
            current_cost = candidate_cost
            if current_cost < best_cost:
                best = current
                best_cost = current_cost
        else:
            # Worse solution → accept with probability exp(-ΔCost / T)
            probability = math.exp(-delta / max(T, 1e-9))
            if random.random() < probability:
                current = candidate
                current_cost = candidate_cost

        # Cool
        T *= alpha
        cost_history.append(best_cost)

    if return_history:
        return best, cost_history
    return best


# ---------------------------------------------------------------------------
# Convergence & comparison plots  (run directly: python -m src.optimization.simulated_annealing)
# ---------------------------------------------------------------------------

def _generate_plots() -> None:
    """
    Generates two charts saved to docs/:
      1. sa_cooling_schedule.png  — temperature vs iteration
      2. sa_vs_random.png         — SA cost vs Random Search cost
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not installed — skipping plots.")
        return

    import os
    os.makedirs("docs", exist_ok=True)

    # ── Chart 1: Cooling schedule ──────────────────────────────────────────
    iters = SA_ITERATIONS
    temps = [SA_INITIAL_TEMP * (SA_COOLING ** i) for i in range(iters)]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(range(iters), temps, color="#1a5fa8", linewidth=2)
    ax.set_title("Simulated Annealing — Cooling Schedule", fontsize=14, fontweight="bold")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Temperature (T)")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xlim(0, iters)
    ax.set_ylim(0, SA_INITIAL_TEMP * 1.05)
    plt.tight_layout()
    plt.savefig("docs/sa_cooling_schedule.png", dpi=150)
    plt.close()
    print("Saved: docs/sa_cooling_schedule.png")

    # ── Chart 2: SA vs Random Search ──────────────────────────────────────
    # Simulate on a realistic congested state
    from config import LightState
    test_state = IntersectionState(
        densities={
            Direction.NORTH: 18,
            Direction.SOUTH: 8,
            Direction.EAST: 14,
            Direction.WEST: 5,
        },
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0,
        cycle_number=1,
        avg_wait_time=0.0,
        total_cars_passed=0,
    )

    _, sa_history = optimize(test_state, return_history=True)
    _, rs_history = random_search(test_state)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(sa_history, color="#e67e22", linewidth=2, label="Simulated Annealing")
    ax.plot(rs_history, color="#7f8c8d", linewidth=2,
            linestyle="--", label="Random Search")
    ax.set_title("Performance Comparison: SA vs Random Search",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Cost (Wait Time Metric)")
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle="--")
    plt.tight_layout()
    plt.savefig("docs/sa_vs_random.png", dpi=150)
    plt.close()
    print("Saved: docs/sa_vs_random.png")

    print("\nAll plots generated successfully.")


if __name__ == "__main__":
    _generate_plots()
