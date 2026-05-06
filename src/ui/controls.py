"""Controls panel — owned by Member 8 (Muhammet Baha)."""
import pygame
from typing import Optional


class Button:
    def __init__(self, rect, label, on_click):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.hovered = False
        self.clicked = False
        self.click_timer = 0

    def draw(self, screen, font):
        # Determine colors based on state
        if self.clicked and self.click_timer > 0:
            bg_color = (120, 120, 200)
            border_color = (255, 255, 255)
        elif self.hovered:
            bg_color = (100, 100, 170)
            border_color = (255, 255, 255)
        else:
            bg_color = (80, 80, 140)
            border_color = (200, 200, 255)

        # Draw button with rounded corners effect
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Draw label centered
        txt = font.render(self.label, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)

    def handle(self, event, mouse_pos):
        # Update hover state
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.on_click()
            self.clicked = True
            self.click_timer = 5
        
        # Decay click animation
        if self.click_timer > 0:
            self.click_timer -= 1
        else:
            self.clicked = False


class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 10)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.hovered = False
        
        # Calculate handle position
        self.handle_radius = 8
        self._update_handle_pos()

    def _update_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.rect.x + int(ratio * self.rect.width)
        self.handle_y = self.rect.y + self.rect.height // 2

    def handle_event(self, event, mouse_pos):
        handle_rect = pygame.Rect(
            self.handle_x - self.handle_radius,
            self.handle_y - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2
        )
        
        self.hovered = handle_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            ratio = (new_x - self.rect.x) / self.rect.width
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            self._update_handle_pos()

    def draw(self, screen, font):
        # Draw label
        label_text = f"{self.label}: {self.value:.2f}"
        txt = font.render(label_text, True, (255, 255, 255))
        screen.blit(txt, (self.rect.x, self.rect.y - 20))
        
        # Draw slider track
        track_color = (100, 100, 100)
        pygame.draw.rect(screen, track_color, self.rect, border_radius=5)
        
        # Draw filled portion
        filled_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
        fill_color = (0, 200, 100) if not self.hovered else (0, 220, 120)
        pygame.draw.rect(screen, fill_color, filled_rect, border_radius=5)
        
        # Draw handle
        handle_color = (255, 255, 255) if not self.dragging else (255, 255, 100)
        pygame.draw.circle(screen, handle_color, (self.handle_x, self.handle_y), self.handle_radius)
        pygame.draw.circle(screen, (0, 0, 0), (self.handle_x, self.handle_y), self.handle_radius, 2)


class WaitTimeChart:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.data_points = []
        self.max_points = 50
        self.max_wait_time = 20.0
        
    def add_data(self, wait_time):
        self.data_points.append(wait_time)
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        # Update max for scaling
        if self.data_points:
            self.max_wait_time = max(max(self.data_points) * 1.2, 10.0)
    
    def draw(self, screen, font):
        # Draw background
        pygame.draw.rect(screen, (40, 40, 60), self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 150), self.rect, 2, border_radius=8)
        
        # Draw title
        title = font.render("Average Wait Time", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 10, self.rect.y + 5))
        
        # Draw axes
        padding = 30
        chart_rect = pygame.Rect(
            self.rect.x + padding,
            self.rect.y + padding,
            self.rect.width - padding * 2,
            self.rect.height - padding * 2
        )
        
        # Y-axis
        pygame.draw.line(screen, (150, 150, 150), 
                        (chart_rect.x, chart_rect.y),
                        (chart_rect.x, chart_rect.bottom), 2)
        # X-axis
        pygame.draw.line(screen, (150, 150, 150),
                        (chart_rect.x, chart_rect.bottom),
                        (chart_rect.right, chart_rect.bottom), 2)
        
        # Draw data points
        if len(self.data_points) > 1:
            points = []
            for i, wait_time in enumerate(self.data_points):
                x = chart_rect.x + int(i * chart_rect.width / max(len(self.data_points) - 1, 1))
                normalized_wait = min(wait_time / self.max_wait_time, 1.0)
                y = chart_rect.bottom - int(normalized_wait * chart_rect.height)
                points.append((x, y))
            
            # Draw line
            if len(points) > 1:
                pygame.draw.lines(screen, (0, 255, 150), False, points, 2)
                
            # Draw points
            for point in points:
                pygame.draw.circle(screen, (0, 255, 150), point, 3)
        
        # Draw scale labels
        small_font = pygame.font.SysFont("Arial", 12)
        max_label = small_font.render(f"{self.max_wait_time:.1f}s", True, (200, 200, 200))
        screen.blit(max_label, (chart_rect.x - 28, chart_rect.y - 5))
        
        zero_label = small_font.render("0s", True, (200, 200, 200))
        screen.blit(zero_label, (chart_rect.x - 18, chart_rect.bottom - 5))


class Controls:
    def __init__(self):
        self.paused = False
        self.ai_mode = True
        self.reset_requested = False
        self.arrival_rate = 0.3
        self.simulation_speed = 1.0
        
        # Buttons with improved layout
        button_y = 645
        self.buttons = [
            Button((20, button_y, 120, 35), "⏯ Pause/Play", self.toggle_pause),
            Button((150, button_y, 140, 35), "🤖 Toggle AI", self.toggle_ai),
            Button((300, button_y, 100, 35), "🔄 Reset", self.request_reset),
        ]
        
        # Sliders
        slider_y = 700
        self.sliders = [
            Slider(20, slider_y, 200, 0.1, 1.0, 0.3, "Arrival Rate"),
            Slider(240, slider_y, 200, 0.5, 3.0, 1.0, "Sim Speed"),
        ]
        
        # Wait time chart
        self.chart = WaitTimeChart(460, 555, 350, 160)
        self.chart_update_counter = 0

    def toggle_pause(self):
        self.paused = not self.paused

    def toggle_ai(self):
        self.ai_mode = not self.ai_mode

    def request_reset(self):
        self.reset_requested = True
        self.chart.data_points.clear()

    def handle_event(self, event) -> None:
        mouse_pos = pygame.mouse.get_pos()
        
        for b in self.buttons:
            b.handle(event, mouse_pos)
        
        for s in self.sliders:
            s.handle_event(event, mouse_pos)
        
        # Update public values from sliders
        self.arrival_rate = self.sliders[0].value
        self.simulation_speed = self.sliders[1].value

    def update_chart(self, wait_time):
        """Update chart every N frames to avoid too frequent updates."""
        self.chart_update_counter += 1
        if self.chart_update_counter >= 30:
            self.chart.add_data(wait_time)
            self.chart_update_counter = 0

    def draw(self, screen, font):
        # Draw control panel background
        panel_rect = pygame.Rect(0, 540, 900, 200)
        pygame.draw.rect(screen, (25, 25, 35), panel_rect)
        pygame.draw.line(screen, (100, 100, 150), (0, 540), (900, 540), 2)
        
        # Draw title section
        title_font = pygame.font.SysFont("Arial", 20, bold=True)
        title = title_font.render("🎛️ Control Dashboard", True, (255, 255, 255))
        screen.blit(title, (20, 550))
        
        # Draw mode indicator with badge style
        mode_text = "🤖 AI MODE" if self.ai_mode else "⏱️ FIXED TIMER"
        mode_bg_color = (0, 150, 70) if self.ai_mode else (180, 140, 0)
        mode_border_color = (0, 220, 100) if self.ai_mode else (220, 180, 0)
        
        mode_txt = title_font.render(mode_text, True, (255, 255, 255))
        mode_rect = pygame.Rect(180, 548, mode_txt.get_width() + 20, 28)
        pygame.draw.rect(screen, mode_bg_color, mode_rect, border_radius=14)
        pygame.draw.rect(screen, mode_border_color, mode_rect, 2, border_radius=14)
        screen.blit(mode_txt, (mode_rect.x + 10, mode_rect.y + 4))
        
        # Draw pause indicator
        if self.paused:
            pause_txt = font.render("⏸ PAUSED", True, (255, 100, 100))
            screen.blit(pause_txt, (350, 553))
        
        # Draw buttons
        for b in self.buttons:
            b.draw(screen, font)
        
        # Draw sliders
        for s in self.sliders:
            s.draw(screen, font)
        
        # Draw chart
        self.chart.draw(screen, font)
