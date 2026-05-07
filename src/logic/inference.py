"""
Inference engine — owned by Member 3.
Modus Ponens-based reasoning over the KNOWLEDGE_BASE defined in rules.py.

Public API (honoured by traffic_agent.py):
  get_facts(state, direction) -> set[str]
  modus_ponens(facts)         -> set[str]
  decide_priority(state)      -> Direction
"""
from config import IntersectionState, Direction, LightState
from src.logic.rules import (
    HIGH_THRESHOLD,
    LOW_THRESHOLD,
    KNOWLEDGE_BASE,
    CONCLUSION_SCORES,
    fact_high_density,
    fact_low_density,
    fact_all_equal,
)


def get_facts(
    state: IntersectionState,
    direction: Direction,
    *,
    emergency_directions: set | None = None,
) -> set:
    """Derive the set of atomic propositions true for *direction* in *state*.

    Args:
        state:                Current intersection snapshot.
        direction:            The lane direction being evaluated.
        emergency_directions: Optional set of Directions where an emergency
                              vehicle has been detected.  Defaults to empty.

    Returns:
        A set of proposition name strings (e.g. ``{"high_density", "not_green"}``).
    """
    if emergency_directions is None:
        emergency_directions = set()

    facts: set[str] = set()
    cars = state.densities[direction]

    # ── Density propositions ──────────────────────────────────────────────────
    if fact_high_density(cars):
        facts.add("high_density")
    if fact_low_density(cars):
        facts.add("low_density")

    # ── Light-state propositions ──────────────────────────────────────────────
    light = state.light_states[direction]
    if light == LightState.GREEN:
        facts.add("is_green")
    else:
        facts.add("not_green")
    if light == LightState.RED:
        facts.add("is_red")

    # ── Emergency vehicle proposition (and its negation) ─────────────────────
    if direction in emergency_directions:
        facts.add("emergency")
    else:
        facts.add("not_emergency")

    # ── Global equal-density proposition ─────────────────────────────────────
    if fact_all_equal(state.densities):
        facts.add("all_equal")

    return facts


def modus_ponens(facts: set) -> set:
    """Apply every Horn-clause rule from KNOWLEDGE_BASE via Modus Ponens.

    For each rule:  if  ALL antecedents are in *facts*  →  add the conclusion.

    Args:
        facts: Set of atomic proposition strings for a single direction.

    Returns:
        Set of conclusion strings (e.g. ``{"critical"}``).
    """
    conclusions: set[str] = set()
    for rule in KNOWLEDGE_BASE:
        if all(antecedent in facts for antecedent in rule["if"]):
            conclusions.add(rule["then"])
    return conclusions


def _score(conclusions: set, density: int) -> float:
    """Map a set of conclusions to a numeric priority score.

    Scores are looked up from CONCLUSION_SCORES (centralised in rules.py).
    A small density-proportional term breaks ties between equal-scoring
    directions.

    Args:
        conclusions: Output of modus_ponens for one direction.
        density:     Raw car count for that direction.

    Returns:
        Floating-point priority score — higher means more urgent.
    """
    base = sum(CONCLUSION_SCORES.get(c, 0) for c in conclusions)
    tiebreak = density * 0.1          # sub-unit so it never overrides a rule
    return base + tiebreak


def decide_priority(
    state: IntersectionState,
    *,
    emergency_directions: set | None = None,
) -> Direction:
    """Return the Direction that should receive highest priority right now.

    Pipeline per direction:
      1. get_facts  → atomic propositions
      2. modus_ponens → conclusions
      3. _score     → numeric priority
    The direction with the highest score wins.

    Args:
        state:                Current intersection snapshot.
        emergency_directions: Directions where emergency vehicles are present.

    Returns:
        The most critical Direction.
    """
    scores: dict[Direction, float] = {}
    for d in Direction:
        facts = get_facts(state, d, emergency_directions=emergency_directions)
        conclusions = modus_ponens(facts)
        scores[d] = _score(conclusions, state.densities[d])
    return max(scores, key=scores.get)
