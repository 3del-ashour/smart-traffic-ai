"""
Tests for Member 7 (Mohammed Sharif) — Pygame renderer.

These tests run headlessly via SDL's dummy video driver, so they're safe in CI.
They verify the renderer:
  - constructs without error
  - exposes a screen surface of the expected size
  - draws successfully for various states (empty, busy, all GREEN, all RED)
  - accepts the optional ai_mode and priority hints from main.py
"""
import os

# Force Pygame into headless mode BEFORE it's imported anywhere
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from config import Direction, IntersectionState, LightState
from src.ui.renderer import HEIGHT, WIDTH, Renderer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def _pygame_init():
    pygame.init()
    yield
    pygame.quit()


def _state(densities=None, lights=None, **kwargs) -> IntersectionState:
    return IntersectionState(
        densities=densities or {d: 0 for d in Direction},
        light_states=lights or {d: LightState.RED for d in Direction},
        current_phase_time=kwargs.get("current_phase_time", 0),
        cycle_number=kwargs.get("cycle_number", 0),
        avg_wait_time=kwargs.get("avg_wait_time", 0.0),
        total_cars_passed=kwargs.get("total_cars_passed", 0),
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_renderer_constructs():
    r = Renderer()
    assert r.screen is not None
    assert r.screen.get_width() == WIDTH
    assert r.screen.get_height() == HEIGHT


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def test_draw_empty_state():
    r = Renderer()
    r.draw(_state())
    # Just confirm a frame was rendered (non-zero pixel sum)
    assert pygame.surfarray.array3d(r.screen).sum() > 0


def test_draw_busy_state():
    r = Renderer()
    state = _state(
        densities={Direction.NORTH: 12, Direction.SOUTH: 4, Direction.EAST: 9, Direction.WEST: 6},
        lights={
            Direction.NORTH: LightState.GREEN,
            Direction.SOUTH: LightState.RED,
            Direction.EAST: LightState.RED,
            Direction.WEST: LightState.RED,
        },
        avg_wait_time=12.34,
        total_cars_passed=87,
        cycle_number=5,
        current_phase_time=22,
    )
    r.draw(state)


def test_draw_all_lights_red():
    r = Renderer()
    r.draw(_state(lights={d: LightState.RED for d in Direction}))


def test_draw_yellow_transition():
    r = Renderer()
    r.draw(_state(lights={
        Direction.NORTH: LightState.YELLOW,
        Direction.SOUTH: LightState.RED,
        Direction.EAST: LightState.RED,
        Direction.WEST: LightState.RED,
    }))


def test_draw_accepts_ai_mode_and_priority():
    r = Renderer()
    state = _state(densities={d: 5 for d in Direction})
    # ai_mode=True with a priority direction — the HUD should render that hint
    r.draw(state, ai_mode=True, priority=Direction.EAST)
    # Fixed mode without priority
    r.draw(state, ai_mode=False, priority=None)


def test_density_overflow_does_not_crash():
    """A lane with way more cars than visible slots must not blow up."""
    r = Renderer()
    state = _state(densities={d: 999 for d in Direction})
    r.draw(state)


def test_many_frames_animation_counter_progresses():
    """The internal frame counter should advance so the pulse animation works."""
    r = Renderer()
    state = _state()
    start = r._frame
    for _ in range(30):
        r.draw(state)
    assert r._frame == start + 30
