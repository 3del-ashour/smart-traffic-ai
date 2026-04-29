"""Controls panel — owned by Member 8."""
import pygame


class Button:
    def __init__(self, rect, label, on_click):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click

    def draw(self, screen, font):
        pygame.draw.rect(screen, (80, 80, 140), self.rect)
        pygame.draw.rect(screen, (200, 200, 255), self.rect, 2)
        txt = font.render(self.label, True, (255, 255, 255))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 5))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.on_click()


class Controls:
    def __init__(self):
        self.paused = False
        self.ai_mode = True
        self.reset_requested = False
        self.buttons = [
            Button((20, 600, 120, 30), "Pause/Play", self.toggle_pause),
            Button((160, 600, 140, 30), "Toggle AI/Fixed", self.toggle_ai),
            Button((320, 600, 100, 30), "Reset", self.request_reset),
        ]

    def toggle_pause(self):
        self.paused = not self.paused

    def toggle_ai(self):
        self.ai_mode = not self.ai_mode

    def request_reset(self):
        self.reset_requested = True

    def handle_event(self, event) -> None:
        for b in self.buttons:
            b.handle(event)

    def draw(self, screen, font):
        for b in self.buttons:
            b.draw(screen, font)
        mode_text = "AI MODE" if self.ai_mode else "FIXED TIMER"
        color = (0, 220, 0) if self.ai_mode else (220, 220, 0)
        txt = font.render(mode_text, True, color)
        screen.blit(txt, (440, 605))
