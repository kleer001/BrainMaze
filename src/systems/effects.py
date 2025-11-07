import pygame
import random
import math


class Particle:
    def __init__(self, x, y, color, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 80)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(2, 6)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.vx *= 0.95
        self.vy *= 0.95

    def is_alive(self):
        return self.lifetime > 0

    def get_alpha(self):
        return int(255 * (self.lifetime / self.max_lifetime))


class EffectsManager:
    """
    Manages visual effects like screen flash, particles, etc.
    """

    def __init__(self, config, screen_size):
        self.config = config
        self.screen_width, self.screen_height = screen_size

        self.flash_duration = config.getfloat('Effects', 'screen_flash_duration')
        self.flash_red_intensity = config.getfloat('Effects', 'screen_flash_red_intensity')
        glow_color_str = config.get('Capture', 'glow_color')
        self.glow_color = tuple(map(int, glow_color_str.split(',')))

        self.flash_active = False
        self.flash_timer = 0.0
        self.particles = []

    def trigger_screen_flash(self):
        self.flash_active = True
        self.flash_timer = self.flash_duration

    def trigger_capture_glow(self, x, y):
        particle_count = 20
        for _ in range(particle_count):
            particle = Particle(x, y, self.glow_color, 1.0)
            self.particles.append(particle)

    def update(self, dt):
        if self.flash_active:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_active = False
                self.flash_timer = 0.0

        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.is_alive()]

    def render(self, surface):
        for particle in self.particles:
            particle_surface = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
            alpha = particle.get_alpha()
            color_with_alpha = (*particle.color, alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, (particle.size, particle.size), particle.size)
            surface.blit(particle_surface, (int(particle.x - particle.size), int(particle.y - particle.size)))

        if self.flash_active:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.set_alpha(int(255 * self.flash_red_intensity))
            flash_surface.fill((255, 0, 0))
            surface.blit(flash_surface, (0, 0))
