# Member 3 — Logic Engineer

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Implement the **logical inference engine** — the agent's reasoning layer using **Propositional Logic + Modus Ponens**.

## You Own
- `src/logic/rules.py`
- `src/logic/inference.py`
- `tests/test_logic.py`

---

## Contract You Must Honor

| Function | Returns |
|----------|---------|
| `decide_priority(state: IntersectionState)` | `Direction` |
| `modus_ponens(facts: set)` | `set` of conclusions |

---

## Step-by-Step Plan

### Day 1-2
- Define propositions and rules in `rules.py`.
- Document each rule in plain English **first**, then in code.

### Day 3
- Implement `modus_ponens` and `decide_priority`.
- Write unit tests.

### Day 4
- Add edge cases: emergency vehicles, all-equal density.

### Day 7-8
- Write the **Logic chapter** of the report — include rule examples and inference traces.

---

## Code Skeleton

### `src/logic/rules.py`

```python
"""
Propositional Logic Rules for Smart Traffic Controller

Propositions:
  P1(D): density(D) > HIGH_THRESHOLD
  P2(D): density(D) < LOW_THRESHOLD
  P3(D): light(D) == GREEN

Rules (Horn clauses):
  R1: P1(D) ∧ ¬P3(D) → CRITICAL(D)
  R2: P2(D) ∧ P3(D)  → SHORTEN(D)
  R3: ALL_EQUAL      → ROTATE
"""

HIGH_THRESHOLD = 10
LOW_THRESHOLD = 3

KNOWLEDGE_BASE = [
    {"if": ["high_density", "not_green"], "then": "critical"},
    {"if": ["low_density", "is_green"],   "then": "shorten"},
    {"if": ["all_equal"],                 "then": "rotate"},
]
```

### `src/logic/inference.py`

```python
from config import IntersectionState, Direction, LightState
from src.logic.rules import HIGH_THRESHOLD, LOW_THRESHOLD, KNOWLEDGE_BASE


def get_facts(state: IntersectionState, direction: Direction) -> set:
    """Return atomic facts holding for this direction."""
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
    """Apply each rule. If all `if` clauses hold, conclude `then`."""
    conclusions = set()
    for rule in KNOWLEDGE_BASE:
        if all(f in facts for f in rule["if"]):
            conclusions.add(rule["then"])
    return conclusions


def decide_priority(state: IntersectionState) -> Direction:
    """Return the most critical direction."""
    scores = {}
    for d in Direction:
        facts = get_facts(state, d)
        conclusions = modus_ponens(facts)
        scores[d] = (
            (3 if "critical" in conclusions else 0)
            + state.densities[d] * 0.1
        )
    return max(scores, key=scores.get)
```

---

## Test Stub

```python
# tests/test_logic.py
from config import IntersectionState, Direction, LightState
from src.logic.inference import decide_priority, modus_ponens

def test_high_density_triggers_critical():
    densities = {d: 1 for d in Direction}
    densities[Direction.NORTH] = 20
    state = IntersectionState(
        densities=densities,
        light_states={d: LightState.RED for d in Direction},
        current_phase_time=0, cycle_number=1,
        avg_wait_time=0.0, total_cars_passed=0,
    )
    assert decide_priority(state) == Direction.NORTH

def test_modus_ponens_critical():
    assert "critical" in modus_ponens({"high_density", "not_green"})
```

---

## Best Practices
- Write rules in plain English first in the report, then translate to code.
- Each rule should have an example (input → conclusion).
- Keep `KNOWLEDGE_BASE` data-driven — easy to add rules.

---

## AI Prompt You Can Paste

> "Implement a propositional logic inference engine in Python for a traffic AI. Use Modus Ponens. Define a knowledge base of rules as Python data. Expose `decide_priority(state) -> Direction` and `modus_ponens(facts: set) -> set`. State data class: IntersectionState (with densities and light_states dicts). Include unit tests with pytest."
