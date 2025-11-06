import pygame
from typing import Tuple


class FactDisplay:
    def __init__(self, screen_size: Tuple[int, int], display_duration: float, reserved_height: int):
        self.screen_width, self.screen_height = screen_size
        self.display_duration = display_duration
        self.reserved_height = reserved_height
        self.font = pygame.font.Font(None, 28)
        self.active = False
        self.current_fact = ""
        self.elapsed_time = 0.0
        self.background_color = (30, 30, 40)
        self.text_color = (200, 200, 200)
        self.padding = 10

    def show(self, fact: str):
        self.current_fact = fact
        self.active = True
        self.elapsed_time = 0.0

    def update(self, dt: float):
        if not self.active:
            return

        self.elapsed_time += dt

        if self.elapsed_time >= self.display_duration:
            self.active = False

    def render(self, screen: pygame.Surface):
        display_y = self.screen_height - self.reserved_height

        panel_rect = pygame.Rect(0, display_y, self.screen_width, self.reserved_height)
        pygame.draw.rect(screen, self.background_color, panel_rect)

        if self.active:
            lines = self._wrap_text(self.current_fact)
            line_height = self.font.get_height()
            total_text_height = len(lines) * line_height
            y_offset = display_y + (self.reserved_height - total_text_height) // 2

            for line in lines:
                text_surface = self.font.render(line, True, self.text_color)
                text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
                screen.blit(text_surface, text_rect)
                y_offset += line_height

    def is_active(self) -> bool:
        return self.active

    def _wrap_text(self, text: str) -> list:
        max_width = self.screen_width - (self.padding * 2)
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, self.text_color)

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines
