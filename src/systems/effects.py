import pygame

class EffectsManager:
    def __init__(self, config, screen_size):
        self.config = config
        self.screen_width, self.screen_height = screen_size

        self.flash_duration = config.getfloat('Effects', 'screen_flash_duration')
        self.flash_red_intensity = config.getfloat('Effects', 'screen_flash_red_intensity')

        self.flash_active = False
        self.flash_timer = 0.0

    def trigger_screen_flash(self):
        self.flash_active = True
        self.flash_timer = self.flash_duration

    def update(self, dt):
        if self.flash_active:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_active = False
                self.flash_timer = 0.0

    def render(self, surface):
        if self.flash_active:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.set_alpha(int(255 * self.flash_red_intensity))
            flash_surface.fill((255, 0, 0))
            surface.blit(flash_surface, (0, 0))
