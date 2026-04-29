"""
Shared types and constants — the SINGLE SOURCE OF TRUTH.
DO NOT modify these without group approval (see docs/INTEGRATION_CONTRACTS.md).
"""
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"


class LightState(Enum):
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"


@dataclass
class IntersectionState:
    """The single source of truth — passed everywhere."""
    densities: dict          # {Direction: int}
    light_states: dict       # {Direction: LightState}
    current_phase_time: int  # seconds elapsed in current phase
    cycle_number: int
    avg_wait_time: float
    total_cars_passed: int


@dataclass
class TimingPlan:
    """Output of optimizer — green durations per direction."""
    durations: dict          # {Direction: int}


# ===== Constants =====
MAX_CARS_PER_LANE = 30
MIN_GREEN_TIME = 10
MAX_GREEN_TIME = 60
SIMULATION_FPS = 30
ARRIVAL_RATE_DEFAULT = 0.3   # cars per second (Poisson lambda)

# Logic thresholds
HIGH_DENSITY_THRESHOLD = 10
LOW_DENSITY_THRESHOLD = 3

# Optimization params
SA_ITERATIONS = 500
SA_INITIAL_TEMP = 10.0
SA_COOLING = 0.95
