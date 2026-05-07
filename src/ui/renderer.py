"""
Pygame renderer — owned by Member 7 (Mohammed Sharif).

Renders the live state of the 4-way intersection used by the demo.

Visual elements
---------------
- Asphalt roads with painted lane dividers and stop lines
- Crosswalks at every approach
- Stylised cars (varied colours, headlights, windscreens)
- Three-bulb traffic-light housings with glow effect on the active bulb
- Compass-style direction labels (N / S / E / W)
- Translucent HUD panel showing cycle, phase time, wait time, cars passed,
  control mode (AI / FIXED), and the lane currently receiving green priority

Public API
----------
    Renderer().draw(state) -> None
"""
import pygame

from config import Direction, IntersectionState, LightState

# ---------------------------------------------------------------------------
# Window / palette
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 700
ROAD_WIDTH = 140
CENTER = (WIDTH // 2, HEIGHT // 2)

PALETTE = {
    "grass":        (34, 139, 70),
    "grass_dark":   (28, 116, 58),
    "road":         (55, 55, 60),
    "road_edge":    (35, 35, 40),
    "lane_paint":   (245, 220, 80),
    "stop_line":    (240, 240, 240),
    "crosswalk":    (240, 240, 240),
    "light_box":    (25, 25, 30),
    "pole":         (60, 60, 65),
    "panel_bg":     (10, 10, 18),
    "panel_border": (80, 130, 200),
    "text":         (235, 240, 250),
    "text_dim":     (160, 170, 185),
    "ai":           (60, 220, 130),
    "fixed":        (220, 130, 60),
    LightState.GREEN:  (60, 220, 80),
    LightState.YELLOW: (250, 210, 60),
    LightState.RED:    (230, 60, 60),
}

# Deterministic but varied car colour palette (looks much better than one shade)
CAR_COLOURS = [
    (190, 200, 220),
    (210, 90, 90),
    (90, 140, 220),
    (240, 220, 110),
    (170, 130, 220),
    (90, 200, 200),
    (240, 160, 80),
    (200, 200, 200),
]


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
class Renderer:
    """All rendering for the live demo."""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Smart Traffic AI")
        self.font = pygame.font.SysFont("Arial", 18)
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.font_big = pygame.font.SysFont("Arial", 22, bold=True)

        # Frame counter for subtle pulsing animation on the active light
        self._frame = 0

        # Pre-computed grass dot positions for cheap "texture"
        self._grass_speckle = [
            (i * 47 % WIDTH, j * 53 % HEIGHT)
            for i in range(0, 40)
            for j in range(0, 40)
            if (i * j) % 7 == 0
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def draw(
        self,
        state: IntersectionState,
        *,
        ai_mode: bool = True,
        priority: Direction | None = None,
    ) -> None:
        """Render one frame.

        `ai_mode` and `priority` are optional — main.py may pass them so the
        HUD shows the live mode and which direction the optimiser favoured.
        """
        self._frame += 1
        self._draw_grass()
        self._draw_roads()
        self._draw_lane_paint()
        self._draw_stop_lines_and_crosswalks()
        self._draw_direction_labels()
        self._draw_cars(state)
        self._draw_lights(state)
        self._draw_hud(state, ai_mode=ai_mode, priority=priority)

    # ------------------------------------------------------------------
    # Background
    # ------------------------------------------------------------------
    def _draw_grass(self) -> None:
        self.screen.fill(PALETTE["grass"])
        for x, y in self._grass_speckle:
            pygame.draw.circle(self.screen, PALETTE["grass_dark"], (x, y), 2)

    def _draw_roads(self) -> None:
        cx, cy = CENTER
        half = ROAD_WIDTH // 2

        # Vertical road (with darker edge stripe)
        pygame.draw.rect(self.screen, PALETTE["road_edge"], (cx - half - 4, 0, ROAD_WIDTH + 8, HEIGHT))
        pygame.draw.rect(self.screen, PALETTE["road"],      (cx - half,     0, ROAD_WIDTH,     HEIGHT))

        # Horizontal road
        pygame.draw.rect(self.screen, PALETTE["road_edge"], (0, cy - half - 4, WIDTH, ROAD_WIDTH + 8))
        pygame.draw.rect(self.screen, PALETTE["road"],      (0, cy - half,     WIDTH, ROAD_WIDTH))

    def _draw_lane_paint(self) -> None:
        """Dashed yellow centre lines on each road (interrupted by the junction)."""
        cx, cy = CENTER
        half = ROAD_WIDTH // 2
        dash = 18
        gap = 14
        thickness = 3

        # Vertical centre line — top half then bottom half
        y = 0
        while y < cy - half:
            pygame.draw.rect(self.screen, PALETTE["lane_paint"],
                             (cx - thickness // 2, y, thickness, dash))
            y += dash + gap
        y = cy + half
        while y < HEIGHT:
            pygame.draw.rect(self.screen, PALETTE["lane_paint"],
                             (cx - thickness // 2, y, thickness, dash))
            y += dash + gap

        # Horizontal centre line — left half then right half
        x = 0
        while x < cx - half:
            pygame.draw.rect(self.screen, PALETTE["lane_paint"],
                             (x, cy - thickness // 2, dash, thickness))
            x += dash + gap
        x = cx + half
        while x < WIDTH:
            pygame.draw.rect(self.screen, PALETTE["lane_paint"],
                             (x, cy - thickness // 2, dash, thickness))
            x += dash + gap

    def _draw_stop_lines_and_crosswalks(self) -> None:
        """White stop lines + zebra crosswalks at every approach."""
        cx, cy = CENTER
        half = ROAD_WIDTH // 2
        stop_thickness = 4
        zebra_w = 8
        zebra_gap = 6
        zebra_len = 18

        # NORTH approach (cars come down toward the centre)
        pygame.draw.rect(self.screen, PALETTE["stop_line"],
                         (cx - half, cy - half - stop_thickness - 2, half, stop_thickness))
        # zebra above stop line
        for i in range(half // (zebra_w + zebra_gap)):
            x = cx - half + i * (zebra_w + zebra_gap) + 2
            pygame.draw.rect(self.screen, PALETTE["crosswalk"],
                             (x, cy - half - stop_thickness - 2 - zebra_len - 4, zebra_w, zebra_len))

        # SOUTH approach
        pygame.draw.rect(self.screen, PALETTE["stop_line"],
                         (cx, cy + half + 2, half, stop_thickness))
        for i in range(half // (zebra_w + zebra_gap)):
            x = cx + i * (zebra_w + zebra_gap) + 2
            pygame.draw.rect(self.screen, PALETTE["crosswalk"],
                             (x, cy + half + 2 + stop_thickness + 4, zebra_w, zebra_len))

        # EAST approach
        pygame.draw.rect(self.screen, PALETTE["stop_line"],
                         (cx + half + 2, cy - half, stop_thickness, half))
        for i in range(half // (zebra_w + zebra_gap)):
            y = cy - half + i * (zebra_w + zebra_gap) + 2
            pygame.draw.rect(self.screen, PALETTE["crosswalk"],
                             (cx + half + 2 + stop_thickness + 4, y, zebra_len, zebra_w))

        # WEST approach
        pygame.draw.rect(self.screen, PALETTE["stop_line"],
                         (cx - half - stop_thickness - 2, cy, stop_thickness, half))
        for i in range(half // (zebra_w + zebra_gap)):
            y = cy + i * (zebra_w + zebra_gap) + 2
            pygame.draw.rect(self.screen, PALETTE["crosswalk"],
                             (cx - half - stop_thickness - 2 - zebra_len - 4, y, zebra_len, zebra_w))

    def _draw_direction_labels(self) -> None:
        labels = {
            Direction.NORTH: ("N",  CENTER[0],  20),
            Direction.SOUTH: ("S",  CENTER[0],  HEIGHT - 30),
            Direction.EAST:  ("E",  WIDTH - 30, CENTER[1]),
            Direction.WEST:  ("W",  20,         CENTER[1]),
        }
        for _, (text, x, y) in labels.items():
            surf = self.font_big.render(text, True, PALETTE["text_dim"])
            rect = surf.get_rect(center=(x, y))
            self.screen.blit(surf, rect)

    # ------------------------------------------------------------------
    # Cars
    # ------------------------------------------------------------------
    def _draw_cars(self, state: IntersectionState) -> None:
        """Stylised cars: body + windscreen + two headlight dots."""
        cx, cy = CENTER
        max_visible = 9          # don't overflow the visible lane
        spacing = 26             # pixels per car

        for d in Direction:
            count = min(state.densities[d], max_visible)
            for i in range(count):
                colour = CAR_COLOURS[(i + d.value.__hash__()) % len(CAR_COLOURS)]
                if d is Direction.NORTH:
                    self._car_vertical(cx - 35, cy - 95 - i * spacing, colour, facing="south")
                elif d is Direction.SOUTH:
                    self._car_vertical(cx + 5,  cy + 75 + i * spacing, colour, facing="north")
                elif d is Direction.EAST:
                    self._car_horizontal(cx + 75 + i * spacing, cy - 35, colour, facing="west")
                elif d is Direction.WEST:
                    self._car_horizontal(cx - 105 - i * spacing, cy + 5, colour, facing="east")

    def _car_vertical(self, x: int, y: int, colour, facing: str) -> None:
        body = pygame.Rect(x, y, 30, 20)
        pygame.draw.rect(self.screen, colour, body, border_radius=4)
        pygame.draw.rect(self.screen, (20, 20, 25), body, 1, border_radius=4)

        # Windscreen
        if facing == "south":  # pointing down
            pygame.draw.rect(self.screen, (40, 60, 90), (x + 4, y + 11, 22, 6), border_radius=2)
            # headlights at the bottom
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 6,  y + 19), 2)
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 24, y + 19), 2)
        else:  # facing north (pointing up)
            pygame.draw.rect(self.screen, (40, 60, 90), (x + 4, y + 3, 22, 6), border_radius=2)
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 6,  y + 1), 2)
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 24, y + 1), 2)

    def _car_horizontal(self, x: int, y: int, colour, facing: str) -> None:
        body = pygame.Rect(x, y, 24, 18)
        pygame.draw.rect(self.screen, colour, body, border_radius=4)
        pygame.draw.rect(self.screen, (20, 20, 25), body, 1, border_radius=4)

        if facing == "west":   # pointing left
            pygame.draw.rect(self.screen, (40, 60, 90), (x + 3,  y + 4, 6, 10), border_radius=2)
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 1,  y + 4),  2)
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 1,  y + 14), 2)
        else:  # facing east (pointing right)
            pygame.draw.rect(self.screen, (40, 60, 90), (x + 15, y + 4, 6, 10), border_radius=2)
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 23, y + 4),  2)
            pygame.draw.circle(self.screen, (255, 240, 180), (x + 23, y + 14), 2)

    # ------------------------------------------------------------------
    # Traffic lights
    # ------------------------------------------------------------------
    def _draw_lights(self, state: IntersectionState) -> None:
        """Three-bulb traffic-light housings with glow on the active bulb."""
        cx, cy = CENTER
        half = ROAD_WIDTH // 2

        # Anchor positions for each housing — they sit on the corner just
        # outside their lane's stop line.
        anchors = {
            Direction.NORTH: (cx - half - 36, cy - half - 36, "vertical"),
            Direction.SOUTH: (cx + half + 6,  cy + half + 6,  "vertical"),
            Direction.EAST:  (cx + half + 6,  cy - half - 36, "horizontal"),
            Direction.WEST:  (cx - half - 60, cy + half + 6,  "horizontal"),
        }

        for d, (ax, ay, orient) in anchors.items():
            self._draw_light_housing(ax, ay, orient, state.light_states[d])

    def _draw_light_housing(self, x: int, y: int, orient: str, active: LightState) -> None:
        # Pole shadow (subtle)
        if orient == "vertical":
            pygame.draw.rect(self.screen, PALETTE["light_box"], (x, y, 30, 70), border_radius=6)
            bulb_positions = [
                (x + 15, y + 12, LightState.RED),
                (x + 15, y + 35, LightState.YELLOW),
                (x + 15, y + 58, LightState.GREEN),
            ]
        else:
            pygame.draw.rect(self.screen, PALETTE["light_box"], (x, y, 70, 30), border_radius=6)
            bulb_positions = [
                (x + 12, y + 15, LightState.RED),
                (x + 35, y + 15, LightState.YELLOW),
                (x + 58, y + 15, LightState.GREEN),
            ]

        for bx, by, bulb_state in bulb_positions:
            if bulb_state == active:
                # Glow halo
                halo = PALETTE[bulb_state]
                pulse = 11 + (self._frame // 6) % 3   # subtle 1-px pulse
                pygame.draw.circle(self.screen, halo, (bx, by), pulse, width=2)
                pygame.draw.circle(self.screen, halo, (bx, by), 8)
            else:
                # Dim version of its colour so all 3 bulbs are always visible
                base = PALETTE[bulb_state]
                dim = tuple(int(c * 0.25) for c in base)
                pygame.draw.circle(self.screen, dim, (bx, by), 8)

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def _draw_hud(
        self,
        state: IntersectionState,
        *,
        ai_mode: bool,
        priority: Direction | None,
    ) -> None:
        # Translucent panel
        panel = pygame.Surface((230, 140), pygame.SRCALPHA)
        panel.fill((*PALETTE["panel_bg"], 200))
        pygame.draw.rect(panel, PALETTE["panel_border"], panel.get_rect(), 2, border_radius=8)
        self.screen.blit(panel, (10, 10))

        # Mode badge
        mode_text = "AI MODE" if ai_mode else "FIXED"
        mode_colour = PALETTE["ai"] if ai_mode else PALETTE["fixed"]
        badge = self.font_small.render(mode_text, True, (10, 10, 15))
        bw, bh = badge.get_size()
        pygame.draw.rect(self.screen, mode_colour, (20, 20, bw + 16, bh + 8), border_radius=10)
        self.screen.blit(badge, (28, 24))

        # Stats
        lines = [
            ("Cycle",       f"{state.cycle_number}"),
            ("Phase",       f"{state.current_phase_time}s"),
            ("Avg Wait",    f"{state.avg_wait_time:.2f}s"),
            ("Cars Passed", f"{state.total_cars_passed}"),
        ]
        y = 50
        for label, value in lines:
            lbl = self.font_small.render(label, True, PALETTE["text_dim"])
            val = self.font.render(value, True, PALETTE["text"])
            self.screen.blit(lbl, (24, y))
            self.screen.blit(val, (130, y - 2))
            y += 22

        # Priority indicator (lower right of panel)
        if priority is not None:
            tag = self.font_small.render(
                f"Priority → {priority.value}", True, PALETTE["ai"]
            )
            self.screen.blit(tag, (24, 132))
