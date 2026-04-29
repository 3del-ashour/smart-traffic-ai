"""
Inference engine — owned by Member 3.
Modus Ponens-based reasoning.
"""
from config import IntersectionState, Direction, LightState
from src.logic.rules import HIGH_THRESHOLD, LOW_THRESHOLD, KNOWLEDGE_BASE


def get_facts(state: IntersectionState, direction: Direction) -> set:
    facts = set()
    if state.densities[direction] > HIGH_THRESHOLD:
        facts.add("high_density")
    if state.densities[direction] < LOW_THRESHOLD:
        facts.add("low_density")
    if state.light_states[direction] == LightState.GREEN:
        facts.add("is_green")
    else:
        facts.add("not_green")
    return facts


def modus_ponens(facts: set) -> set:
    conclusions = set()
    for rule in KNOWLEDGE_BASE:
        if all(f in facts for f in rule["if"]):
            conclusions.add(rule["then"])
    return conclusions


def decide_priority(state: IntersectionState) -> Direction:
    scores = {}
    for d in Direction:
        facts = get_facts(state, d)
        conclusions = modus_ponens(facts)
        scores[d] = (
            (3 if "critical" in conclusions else 0)
            + state.densities[d] * 0.1
        )
    return max(scores, key=scores.get)
