"""
Visual effects system.
Phase A4: Screen flash effect for player-enemy collision.
"""

import pygame


class EffectsManager:
    """
    Manages visual effects like screen flash, particles, etc.
    """

    def __init__(self, config, screen_size):
        """
        Initialize effects manager.

        Args:
            config: ConfigParser object with gameplay settings
            screen_size: (width, height) tuple of screen dimensions
        """
        self.config = config
        self.screen_width, self.screen_height = screen_size

        # Screen flash parameters
        self.flash_duration = config.getfloat('Effects', 'screen_flash_duration')
        self.flash_red_intensity = config.getfloat('Effects', 'screen_flash_red_intensity')

        # Flash state
        self.flash_active = False
        self.flash_timer = 0.0

    def trigger_screen_flash(self):
        """Trigger a red screen flash (on player-enemy collision)."""
        self.flash_active = True
        self.flash_timer = self.flash_duration

    def update(self, dt):
        """
        Update effects timers.

        Args:
            dt: Delta time in seconds
        """
        # Update flash timer
        if self.flash_active:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_active = False
                self.flash_timer = 0.0

    def render(self, surface):
        """
        Render all active effects.

        Args:
            surface: Pygame surface to draw on
        """
        # Render screen flash
        if self.flash_active:
            # Create semi-transparent red overlay
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.set_alpha(int(255 * self.flash_red_intensity))
            flash_surface.fill((255, 0, 0))  # Red
            surface.blit(flash_surface, (0, 0))
