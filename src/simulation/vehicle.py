"""
Vehicle entity — owned by Member 6 (Abdulrahman).

Represents a single car waiting at the intersection. Tracks precise spawn
time and accumulated wait time so Member 9's evaluation module can compute
average / worst-case wait metrics across the run.
"""
from config import Direction


class Vehicle:
    """High-fidelity vehicle agent within the intersection."""

    def __init__(self, direction: Direction, spawn_time: float):
        # Direction the vehicle is coming from
        self.direction = direction

        # Absolute simulation time (s) when the vehicle was generated
        self.spawn_time = spawn_time

        # Total seconds spent waiting at a RED light
        self.wait_time = 0.0

        # Stable identifier for evaluation tracking
        self.id = id(self)

    def update_wait(self, dt: float, is_moving: bool) -> None:
        """
        Increment wait time only while the vehicle is stuck at the light.
        Called when a finer-grained per-vehicle model is needed.
        """
        if not is_moving:
            self.wait_time += dt
