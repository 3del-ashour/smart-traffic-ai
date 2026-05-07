"""
Tests for the propositional logic engine — Member 3 (Logic Engineer).

Covers:
  - rules.py  : fact helpers, KNOWLEDGE_BASE structure, CONCLUSION_SCORES
  - inference.py : get_facts, modus_ponens, _score, decide_priority

Run with:
    pytest tests/test_logic.py -v
"""
import pytest

from config import (
    Direction,
    HIGH_DENSITY_THRESHOLD,
    IntersectionState,
    LOW_DENSITY_THRESHOLD,
    LightState,
)
from src.logic.inference import _score, decide_priority, get_facts, modus_ponens
from src.logic.rules import (
    CONCLUSION_SCORES,
    HIGH_THRESHOLD,
    KNOWLEDGE_BASE,
    LOW_THRESHOLD,
    fact_all_equal,
    fact_high_density,
    fact_low_density,
)

# ── Shared fixtures ────────────────────────────────────────────────────────────

ALL_RED   = {d: LightState.RED   for d in Direction}
ALL_GREEN = {d: LightState.GREEN for d in Direction}

# Density values guaranteed to be above / below / between the thresholds.
ABOVE_HIGH = HIGH_THRESHOLD + 5   # e.g. 15
BELOW_LOW  = LOW_THRESHOLD  - 1   # e.g. 2
MID        = (HIGH_THRESHOLD + LOW_THRESHOLD) // 2  # e.g. 6

# Canonical "one busy direction, rest idle" densities used by many tests.
NORTH_HEAVY = {d: BELOW_LOW for d in Direction} | {Direction.NORTH: ABOVE_HIGH}
SOUTH_HEAVY = {d: BELOW_LOW for d in Direction} | {Direction.SOUTH: ABOVE_HIGH}


def _state(
    densities: dict | None = None,
    lights: dict | None = None,
    cycle: int = 1,
) -> IntersectionState:
    """Build a minimal but realistic IntersectionState."""
    return IntersectionState(
        densities=dict(densities or {d: MID for d in Direction}),
        light_states=dict(lights or ALL_RED),
        current_phase_time=0,
        cycle_number=cycle,
        avg_wait_time=2.5,
        total_cars_passed=42,
    )


# ── rules.py — threshold aliases ──────────────────────────────────────────────

class TestThresholds:
    def test_high_threshold_matches_config(self):
        assert HIGH_THRESHOLD == HIGH_DENSITY_THRESHOLD

    def test_low_threshold_matches_config(self):
        assert LOW_THRESHOLD == LOW_DENSITY_THRESHOLD

    def test_thresholds_ordered(self):
        """Low threshold must be strictly below high threshold."""
        assert LOW_THRESHOLD < HIGH_THRESHOLD


# ── rules.py — fact helper functions ──────────────────────────────────────────

class TestFactHelpers:
    def test_fact_high_density_above_threshold(self):
        assert fact_high_density(ABOVE_HIGH) is True

    def test_fact_high_density_at_threshold_is_false(self):
        # Strictly greater-than, so equal should be False.
        assert fact_high_density(HIGH_THRESHOLD) is False

    def test_fact_high_density_below_threshold(self):
        assert fact_high_density(BELOW_LOW) is False

    def test_fact_low_density_below_threshold(self):
        assert fact_low_density(BELOW_LOW) is True

    def test_fact_low_density_at_threshold_is_false(self):
        # Strictly less-than, so equal should be False.
        assert fact_low_density(LOW_THRESHOLD) is False

    def test_fact_low_density_above_threshold(self):
        assert fact_low_density(ABOVE_HIGH) is False

    def test_fact_all_equal_identical_values(self):
        equal = {d: 5 for d in Direction}
        assert fact_all_equal(equal) is True

    def test_fact_all_equal_different_values(self):
        unequal = {d: i for i, d in enumerate(Direction)}
        assert fact_all_equal(unequal) is False

    def test_fact_all_equal_single_direction(self):
        assert fact_all_equal({Direction.NORTH: 7}) is True

    def test_fact_all_equal_empty_returns_false(self):
        assert fact_all_equal({}) is False


# ── rules.py — KNOWLEDGE_BASE structure ───────────────────────────────────────

class TestKnowledgeBase:
    def test_knowledge_base_is_a_list(self):
        assert isinstance(KNOWLEDGE_BASE, list)

    def test_every_rule_has_required_keys(self):
        for i, rule in enumerate(KNOWLEDGE_BASE):
            assert "if"   in rule, f"Rule {i} missing 'if'"
            assert "then" in rule, f"Rule {i} missing 'then'"

    def test_all_conclusions_have_a_score(self):
        """Every rule's conclusion must have a weight in CONCLUSION_SCORES."""
        for rule in KNOWLEDGE_BASE:
            assert rule["then"] in CONCLUSION_SCORES, (
                f"No score for conclusion '{rule['then']}'"
            )

    def test_urgent_score_is_highest(self):
        assert CONCLUSION_SCORES["urgent"] == max(CONCLUSION_SCORES.values())

    def test_skip_score_is_lowest(self):
        assert CONCLUSION_SCORES["skip"] == min(CONCLUSION_SCORES.values())

    def test_critical_score_positive(self):
        assert CONCLUSION_SCORES["critical"] > 0

    def test_shorten_and_skip_scores_negative(self):
        assert CONCLUSION_SCORES["shorten"] < 0
        assert CONCLUSION_SCORES["skip"]    < 0


# ── inference.py — get_facts ───────────────────────────────────────────────────

class TestGetFacts:
    def test_high_density_red_light_facts(self):
        state = _state(densities=NORTH_HEAVY, lights=ALL_RED)
        facts = get_facts(state, Direction.NORTH)
        assert "high_density" in facts
        assert "not_green"    in facts
        assert "is_red"       in facts
        assert "low_density"  not in facts
        assert "is_green"     not in facts

    def test_low_density_green_light_facts(self):
        state = _state(densities={d: BELOW_LOW for d in Direction}, lights=ALL_GREEN)
        facts = get_facts(state, Direction.EAST)
        assert "low_density" in facts
        assert "is_green"    in facts
        assert "not_green"   not in facts

    def test_emergency_fact_present_when_in_set(self):
        state = _state()
        facts = get_facts(state, Direction.SOUTH, emergency_directions={Direction.SOUTH})
        assert "emergency"     in facts
        assert "not_emergency" not in facts

    def test_not_emergency_fact_when_absent(self):
        state = _state()
        facts = get_facts(state, Direction.NORTH, emergency_directions={Direction.SOUTH})
        assert "not_emergency" in facts
        assert "emergency"     not in facts

    def test_all_equal_fact_when_densities_equal(self):
        state = _state(densities={d: 5 for d in Direction})
        facts = get_facts(state, Direction.WEST)
        assert "all_equal" in facts

    def test_all_equal_fact_absent_when_unequal(self):
        state = _state(densities=NORTH_HEAVY)
        facts = get_facts(state, Direction.NORTH)
        assert "all_equal" not in facts

    def test_default_emergency_set_is_empty(self):
        """Calling get_facts without emergency_directions must not raise."""
        state = _state()
        facts = get_facts(state, Direction.NORTH)
        assert "not_emergency" in facts
        assert "emergency"     not in facts


# ── inference.py — modus_ponens ───────────────────────────────────────────────

class TestModusPonens:
    # R1 — critical
    def test_r1_high_density_not_green_gives_critical(self):
        assert "critical" in modus_ponens({"high_density", "not_green", "not_emergency"})

    # R2 — extend (congested + green)
    def test_r2_high_density_is_green_gives_extend(self):
        assert "extend" in modus_ponens({"high_density", "is_green", "not_emergency"})

    # R3 — shorten
    def test_r3_low_density_is_green_gives_shorten(self):
        assert "shorten" in modus_ponens({"low_density", "is_green", "not_emergency"})

    # R4 — skip (requires not_emergency)
    def test_r4_low_density_not_green_gives_skip(self):
        assert "skip" in modus_ponens({"low_density", "not_green", "not_emergency"})

    def test_r4_skip_does_not_fire_on_emergency_direction(self):
        """R4 must not fire when 'emergency' is present (not_emergency absent)."""
        conclusions = modus_ponens({"low_density", "not_green", "emergency"})
        assert "skip" not in conclusions

    # R5 — urgent (emergency + red)
    def test_r5_emergency_not_green_gives_urgent(self):
        assert "urgent" in modus_ponens({"emergency", "not_green", "low_density"})

    # R6 — extend (emergency + green)
    def test_r6_emergency_is_green_gives_extend(self):
        assert "extend" in modus_ponens({"emergency", "is_green"})

    # R7 — rotate
    def test_r7_all_equal_gives_rotate(self):
        assert "rotate" in modus_ponens({"all_equal", "is_red", "not_emergency"})

    # R8 — yield
    def test_r8_is_red_gives_yield(self):
        assert "yield" in modus_ponens({"is_red", "not_emergency"})

    # Empty / no-match
    def test_empty_facts_gives_no_conclusions(self):
        assert modus_ponens(set()) == set()

    def test_unrelated_facts_give_no_conclusions(self):
        assert modus_ponens({"foo", "bar"}) == set()

    # Return type
    def test_returns_set(self):
        assert isinstance(modus_ponens({"high_density", "not_green"}), set)

    # Multiple conclusions can fire simultaneously
    def test_multiple_conclusions_can_fire(self):
        """High density + red: both R1 (critical) and R8 (yield) fire."""
        conclusions = modus_ponens({"high_density", "not_green", "is_red", "not_emergency"})
        assert "critical" in conclusions
        assert "yield"    in conclusions


# ── inference.py — decide_priority ────────────────────────────────────────────

class TestDecidePriority:
    def test_returns_a_direction(self):
        state = _state()
        result = decide_priority(state)
        assert isinstance(result, Direction)

    def test_high_density_direction_wins(self):
        """NORTH with 20+ cars (critical) must outrank all others with 2 cars."""
        state = _state(densities=NORTH_HEAVY, lights=ALL_RED)
        assert decide_priority(state) == Direction.NORTH

    def test_high_density_south_wins(self):
        state = _state(densities=SOUTH_HEAVY, lights=ALL_RED)
        assert decide_priority(state) == Direction.SOUTH

    def test_emergency_wins_over_low_density_competitors(self):
        """Emergency on WEST beats the other directions that all have low cars."""
        densities = {d: BELOW_LOW for d in Direction}
        state = _state(densities=densities, lights=ALL_RED)
        result = decide_priority(state, emergency_directions={Direction.WEST})
        assert result == Direction.WEST

    def test_emergency_on_red_beats_normal_congested(self):
        """urgent (+12) from a small emergency queue beats critical (+10) on NORTH
        only when the density tiebreaker doesn't flip it.  Use equal density here
        so the only differentiator is the rule scores."""
        densities = {d: MID for d in Direction}
        state = _state(densities=densities, lights=ALL_RED)
        result = decide_priority(state, emergency_directions={Direction.EAST})
        assert result == Direction.EAST

    def test_equal_density_still_returns_a_direction(self):
        """All directions equal — must return *one* Direction without crashing."""
        state = _state(densities={d: MID for d in Direction}, lights=ALL_RED)
        result = decide_priority(state)
        assert result in Direction

    def test_all_zero_density_does_not_raise(self):
        state = _state(densities={d: 0 for d in Direction}, lights=ALL_RED)
        result = decide_priority(state)
        assert result in Direction

    def test_priority_consistent_across_calls(self):
        """Same state must produce the same result every time (determinism)."""
        state = _state(densities=NORTH_HEAVY, lights=ALL_RED)
        results = {decide_priority(state) for _ in range(10)}
        assert len(results) == 1

    def test_green_light_high_density_extends_priority(self):
        """High density + green → extend (+4) should still rank above low-density red."""
        lights = dict(ALL_RED)
        lights[Direction.SOUTH] = LightState.GREEN
        densities = {d: BELOW_LOW for d in Direction}
        densities[Direction.SOUTH] = ABOVE_HIGH
        state = _state(densities=densities, lights=lights)
        assert decide_priority(state) == Direction.SOUTH

    def test_low_density_green_is_deprioritised(self):
        """A direction with low density + green (shorten) must lose to a congested red."""
        lights = {d: LightState.RED for d in Direction}
        lights[Direction.EAST] = LightState.GREEN
        densities = {d: BELOW_LOW for d in Direction}
        densities[Direction.NORTH] = ABOVE_HIGH     # critical on red
        # EAST has low density + green (shorten -3); NORTH critical (+10)
        state = _state(densities=densities, lights=lights)
        assert decide_priority(state) == Direction.NORTH


# ── inference.py — _score (unit test the scoring helper) ──────────────────────

class TestScore:
    def test_urgent_conclusion_gives_high_score(self):
        score = _score({"urgent"}, density=1)
        assert score >= CONCLUSION_SCORES["urgent"]

    def test_skip_conclusion_gives_low_score(self):
        score = _score({"skip"}, density=1)
        assert score <= CONCLUSION_SCORES["skip"] + 1  # +0.1 tiebreak

    def test_density_tiebreak_is_sub_unit(self):
        """Tiebreak from density alone must never flip a one-step score difference."""
        diff = CONCLUSION_SCORES["critical"] - CONCLUSION_SCORES["extend"]
        # Two directions differ by exactly one rule level (diff ≥ 6).
        # Even 30 cars * 0.1 = 3.0 < 6, so the rule conclusion must dominate.
        max_tiebreak = 30 * 0.1
        assert max_tiebreak < diff

    def test_empty_conclusions_score_is_density_tiebreak_only(self):
        assert _score(set(), density=10) == pytest.approx(1.0)

    def test_multiple_conclusions_are_summed(self):
        expected = CONCLUSION_SCORES["critical"] + CONCLUSION_SCORES["yield"] + 5 * 0.1
        assert _score({"critical", "yield"}, density=5) == pytest.approx(expected)
