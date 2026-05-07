"""
Propositional Logic Rules for Smart Traffic Controller
=======================================================
Owned by Member 3 — Logic Engineer.
See docs/member-3-logic-engineer.md for the full specification.

Propositions (atomic facts, evaluated per-direction by inference.get_facts):
  high_density   : density(D) > HIGH_THRESHOLD       (P1)
  low_density    : density(D) < LOW_THRESHOLD         (P2)
  is_green       : light(D) == GREEN                  (P3)
  not_green      : light(D) != GREEN                  (¬P3)
  is_red         : light(D) == RED                    (P4)
  emergency      : emergency_vehicle present in D     (P5)
  not_emergency  : no emergency vehicle in D          (¬P5)
  all_equal      : all directions have equal density  (P6, global)

Horn-Clause Rules (antecedents → consequent):
  R1: high_density  ∧ not_green              → critical  # backlog building up, needs green
  R2: high_density  ∧ is_green              → extend    # keep green longer; queue is heavy
  R3: low_density   ∧ is_green              → shorten   # waste of green; yield to others
  R4: low_density   ∧ not_green             → skip      # no cars waiting; skip this phase
       (R4 requires not_emergency so an ambulance route is never skipped)
  R5: emergency     ∧ not_green             → urgent    # override: give green immediately
  R6: emergency     ∧ is_green             → extend    # keep green until emergency clears
  R7: all_equal                             → rotate    # fair round-robin when loads match
  R8: is_red                               → yield     # currently red: deprioritise

Conclusion values and their effect on the scoring in inference.decide_priority:
  critical  → +10  (highest urgency — backlog, no green)
  urgent    → +12  (emergency vehicle override, highest possible score)
  extend    → +4   (already green but still heavy / emergency ongoing)
  shorten   → -3   (low density, wasteful green)
  skip      → -5   (no cars, not green — lowest priority)
  rotate    →  0   (used by decide_priority to break ties fairly)
  yield     → -1   (modest penalty for being on red with normal load)
"""

from config import HIGH_DENSITY_THRESHOLD, LOW_DENSITY_THRESHOLD

# ── Threshold aliases (imported by inference.py) ─────────────────────────────
HIGH_THRESHOLD = HIGH_DENSITY_THRESHOLD   # cars — above this → congested
LOW_THRESHOLD  = LOW_DENSITY_THRESHOLD    # cars — below this → sparse

# ── Score weights ─────────────────────────────────────────────────────────────
# Centralised here so the inference layer never needs magic numbers.
# inference.py reads CONCLUSION_SCORES to convert conclusions → numeric scores.
CONCLUSION_SCORES: dict[str, int] = {
    "urgent":   12,   # R5/R6 — emergency vehicle present
    "critical": 10,   # R1    — heavy queue, no green
    "extend":    4,   # R2/R6 — keep current green phase
    "rotate":    0,   # R7    — equal densities, rotate fairly
    "yield":    -1,   # R8    — on red with normal load
    "shorten":  -3,   # R3    — light load, has green
    "skip":     -5,   # R4    — no cars, no green
}

# ── Knowledge Base (Horn clauses) ─────────────────────────────────────────────
# Each entry is a rule:
#   "if"   : list of proposition names — ALL must be in the fact set (conjunction)
#   "then" : conclusion string that gets added to the result set
#   "note" : plain-English description (for the report / debugging)
#
# IMPORTANT: keep this data-driven. To add a new rule, append a dict — no
# code changes required anywhere else, because inference.modus_ponens iterates
# this list generically.
KNOWLEDGE_BASE: list[dict] = [
    # ── R1: Critical backlog — heavy queue waiting for green ──────────────────
    {
        "if":   ["high_density", "not_green"],
        "then": "critical",
        "note": "High density + red light → cars piling up; prioritise immediately.",
    },

    # ── R2: Sustain heavy green — already green and still congested ───────────
    {
        "if":   ["high_density", "is_green"],
        "then": "extend",
        "note": "High density + green light → extend phase to drain the queue.",
    },

    # ── R3: Shorten wasteful green — light traffic already has green ──────────
    {
        "if":   ["low_density", "is_green"],
        "then": "shorten",
        "note": "Low density + green light → shorten phase; yield time to others.",
    },

    # ── R4: Skip idle red — no cars waiting, not green, no emergency ───────────
    # Requires not_emergency: an emergency vehicle route must never be skipped
    # even if its queue looks sparse (e.g., single ambulance counted as 1 car).
    {
        "if":   ["low_density", "not_green", "not_emergency"],
        "then": "skip",
        "note": "Low density + red + no emergency → skip or minimise this phase.",
    },

    # ── R5: Emergency override — vehicle detected, currently red ─────────────
    {
        "if":   ["emergency", "not_green"],
        "then": "urgent",
        "note": "Emergency vehicle + red → grant green immediately (highest priority).",
    },

    # ── R6: Emergency sustain — vehicle detected, currently green ────────────
    {
        "if":   ["emergency", "is_green"],
        "then": "extend",
        "note": "Emergency vehicle + green → keep green until vehicle clears.",
    },

    # ── R7: Fair rotation — all queues are equal ──────────────────────────────
    {
        "if":   ["all_equal"],
        "then": "rotate",
        "note": "Equal density across all directions → rotate phases fairly.",
    },

    # ── R8: Yield — direction is currently red (default deprioritisation) ─────
    {
        "if":   ["is_red"],
        "then": "yield",
        "note": "Currently on red with no special condition → slight deprioritisation.",
    },
]


# ── Helper: fact constructors (used by inference.get_facts) ───────────────────
# These pure functions derive atomic proposition labels from raw values, keeping
# all threshold logic in one place (this file).

def fact_high_density(cars: int) -> bool:
    """P1: True when car count exceeds the high-density threshold."""
    return cars > HIGH_THRESHOLD


def fact_low_density(cars: int) -> bool:
    """P2: True when car count is below the low-density threshold."""
    return cars < LOW_THRESHOLD


def fact_all_equal(densities: dict) -> bool:
    """P6: True when every direction has the same density value.

    Args:
        densities: mapping of Direction → car count (the full intersection dict).

    Returns:
        True if all values are identical.
    """
    values = list(densities.values())
    return len(values) > 0 and all(v == values[0] for v in values)
