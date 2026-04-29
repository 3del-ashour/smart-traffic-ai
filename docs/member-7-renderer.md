# Member 7 — UI/UX Designer (Renderer)

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Build the **animated visualization** with Pygame.

## You Own
- `src/ui/renderer.py`

---

## Contract You Must Honor

| Function | Returns |
|----------|---------|
| `Renderer().draw(state: IntersectionState)` | `None` |

> The renderer is **read-only** — it never mutates state.

---

## Step-by-Step Plan

### Day 2-3
- Build basic intersection layout (cross-shape roads).
- Draw cars as queued rectangles in each direction.

### Day 4
- Add traffic-light circles with color states.
- Add HUD (cycle, phase time, avg wait, cars passed).

### Day 5-6
- Polish visuals — smooth animations.
- Add a small chart of avg wait over cycles (bottom-right corner).

### Day 7-8
- Help with the UI section of the report — include screenshots.

---

## Code Skeleton

```python
# src/ui/renderer.py
import pygame
from config import IntersectionState, Direction, LightState

WIDTH, HEIGHT = 900, 700
COLORS = {
    "road": (60, 60, 60),
    "bg":   (30, 130, 60),
    "car":  (200, 200, 255),
    LightState.GREEN:  (0, 220, 0),
    LightState.YELLOW: (240, 200, 0),
    LightState.RED:    (220, 0, 0),
}


class Renderer:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Smart Traffic AI")
        self.font = pygame.font.SysFont("Arial", 18)

    def draw(self, state: IntersectionState) -> None:
        self.screen.fill(COLORS["bg"])
        self._draw_roads()
        self._draw_cars(state)
        self._draw_lights(state)
        self._draw_hud(state)

    def _draw_roads(self):
        cx, cy = WIDTH // 2, HEIGHT // 2
        pygame.draw.rect(self.screen, COLORS["road"], (cx - 60, 0, 120, HEIGHT))
        pygame.draw.rect(self.screen, COLORS["road"], (0, cy - 60, WIDTH, 120))

    def _draw_cars(self, state):
        cx, cy = WIDTH // 2, HEIGHT // 2
        for d in Direction:
            count = min(state.densities[d], 8)
            for i in range(count):
                if d == Direction.NORTH:
                    pygame.draw.rect(self.screen, COLORS["car"],
                                     (cx - 30, cy - 100 - i * 22, 25, 18))
                elif d == Direction.SOUTH:
                    pygame.draw.rect(self.screen, COLORS["car"],
                                     (cx + 5, cy + 82 + i * 22, 25, 18))
                elif d == Direction.EAST:
                    pygame.draw.rect(self.screen, COLORS["car"],
                                     (cx + 82 + i * 28, cy - 30, 22, 16))
                elif d == Direction.WEST:
                    pygame.draw.rect(self.screen, COLORS["car"],
                                     (cx - 104 - i * 28, cy + 5, 22, 16))

    def _draw_lights(self, state):
        cx, cy = WIDTH // 2, HEIGHT // 2
        positions = {
            Direction.NORTH: (cx - 70, cy - 70),
            Direction.SOUTH: (cx + 55, cy + 55),
            Direction.EAST:  (cx + 55, cy - 70),
            Direction.WEST:  (cx - 70, cy + 55),
        }
        for d, pos in positions.items():
            pygame.draw.circle(self.screen, COLORS[state.light_states[d]], pos, 10)

    def _draw_hud(self, state):
        lines = [
            f"Cycle: {state.cycle_number}",
            f"Phase Time: {state.current_phase_time}s",
            f"Avg Wait: {state.avg_wait_time:.2f}s",
            f"Cars Passed: {state.total_cars_passed}",
        ]
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(txt, (10, 10 + i * 22))
```

---

## Best Practices
- Don't compute logic in the renderer — only **read state**.
- Use vector graphics (`pygame.draw`) — they scale.
- Keep frame rendering fast (target < 16ms).

---

## AI Prompt You Can Paste

> "Build a Pygame renderer for a 4-way intersection traffic simulation. Class Renderer with method draw(state: IntersectionState). Draw cross-shape roads, cars as queued rectangles per direction (N, S, E, W), traffic lights as colored circles, and a HUD with cycle number, phase time, average wait, and total cars passed. Render-only — never mutate state. State has fields densities (dict), light_states (dict), current_phase_time, cycle_number, avg_wait_time, total_cars_passed."
