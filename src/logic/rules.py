"""
Propositional Logic rules — owned by Member 3.
See docs/member-3-logic-engineer.md for the full guide.

Propositions:
  P1(D): density(D) > HIGH_THRESHOLD
  P2(D): density(D) < LOW_THRESHOLD
  P3(D): light(D) == GREEN

Rules (Horn clauses):
  R1: P1(D) ∧ ¬P3(D) → CRITICAL(D)
  R2: P2(D) ∧ P3(D)  → SHORTEN(D)
  R3: ALL_EQUAL      → ROTATE
"""
from config import HIGH_DENSITY_THRESHOLD, LOW_DENSITY_THRESHOLD

HIGH_THRESHOLD = HIGH_DENSITY_THRESHOLD
LOW_THRESHOLD = LOW_DENSITY_THRESHOLD

KNOWLEDGE_BASE = [
    {"if": ["high_density", "not_green"], "then": "critical"},
    {"if": ["low_density", "is_green"],   "then": "shorten"},
    {"if": ["all_equal"],                 "then": "rotate"},
]
