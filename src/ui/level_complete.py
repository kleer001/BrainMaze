import pygame


class LevelCompleteScreen:
    def __init__(self, screen_size):
        self.screen_width, self.screen_height = screen_size
        self.is_showing = False
        self.facts = []
        self.progress_text = ""
        self.is_game_over = False
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.bg_color = (20, 20, 30)
        self.text_color = (255, 255, 200)
        self.title_color = (100, 200, 255)

    def show(self, facts, progress_text, is_game_over=False):
        self.facts = facts
        self.progress_text = progress_text
        self.is_game_over = is_game_over
        self.is_showing = True

    def hide(self):
        self.is_showing = False
        self.facts = []

    def is_active(self):
        return self.is_showing

    def render(self, surface):
        if not self.is_showing:
            return

        surface.fill(self.bg_color)

        title_text = "Game Complete!" if self.is_game_over else "Level Complete!"
        title = self.font_large.render(title_text, True, self.title_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        surface.blit(title, title_rect)

        progress = self.font_medium.render(f"Progress: {self.progress_text}", True, self.title_color)
        progress_rect = progress.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(progress, progress_rect)

        subtitle = self.font_medium.render("Facts Learned:", True, self.text_color)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 150))
        surface.blit(subtitle, subtitle_rect)

        y_offset = 180
        line_spacing = 40
        margin = 40

        for fact in self.facts:
            words = fact.split()
            lines = []
            current_line = []
            max_width = self.screen_width - (margin * 2)

            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.font_medium.render(test_line, True, self.text_color)
                if test_surface.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            bullet = self.font_medium.render("• ", True, self.text_color)
            surface.blit(bullet, (margin, y_offset))

            for i, line in enumerate(lines):
                text_surface = self.font_medium.render(line, True, self.text_color)
                x_offset = margin + 20 if i == 0 else margin + 40
                surface.blit(text_surface, (x_offset, y_offset))
                y_offset += line_spacing

            y_offset += 10

        prompt_text = "Press ESC to quit" if self.is_game_over else "Press SPACE to continue"
        prompt = self.font_medium.render(prompt_text, True, self.title_color)
        prompt_rect = prompt.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        surface.blit(prompt, prompt_rect)
