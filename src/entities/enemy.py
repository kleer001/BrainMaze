"""
Enemy entity with AI-driven movement.
Phase A3: Single enemy with random wandering behavior.
Phase A5: Multiple behaviors - randomly assigned on spawn.
"""

import pygame
import random
from pygame_emojis import load_emoji
from ai.behaviors import WandererBehavior, PatrolBehavior


class Enemy(pygame.sprite.Sprite):
    """
    Enemy sprite with AI behavior and randomized attributes.
    Moves through the maze with wall collision detection.
    """

    def __init__(self, x, y, config, collision_manager, maze, emoji="🐱", behavior_type=None, fact=""):
        super().__init__()

        self.config = config
        self.collision_manager = collision_manager
        self.maze = maze
        self.behavior_type_override = behavior_type
        self.fact = fact

        self.tile_size = maze.tile_size
        self.offset_x = maze.offset_x
        self.offset_y = maze.offset_y

        speed_min = config.getint('Attributes', 'speed_min')
        speed_max = config.getint('Attributes', 'speed_max')
        awareness_min = config.getint('Attributes', 'awareness_min')
        awareness_max = config.getint('Attributes', 'awareness_max')

        self.speed = random.randint(speed_min, speed_max)
        self.awareness = random.randint(awareness_min, awareness_max)

        self.update_interval = config.getint('Movement', 'update_interval')
        self.frame_counter = 0

        self.tile_x = x
        self.tile_y = y

        self.render_emoji = True
        self.emoji = emoji

        if self.render_emoji:
            emoji_size = int(self.tile_size * 0.8)
            emoji_surface = load_emoji(self.emoji, (emoji_size, emoji_size))

            self.image = pygame.Surface((self.tile_size - 4, self.tile_size - 4), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))

            emoji_rect = emoji_surface.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
            self.image.blit(emoji_surface, emoji_rect)
        else:
            self.image = pygame.Surface((self.tile_size - 4, self.tile_size - 4))
            color = tuple(map(int, config.get('Colors', 'enemy').split(',')))
            self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.center = (
            self.offset_x + x * self.tile_size + self.tile_size // 2,
            self.offset_y + y * self.tile_size + self.tile_size // 2
        )

        # Initialize behavior (random selection for Phase A5)
        self.behavior = self._assign_random_behavior()

        # Death animation state
        self.is_dying = False
        self.death_timer = 0.0
        self.death_duration = 0.5
        self.flash_count = 0
        self.flash_interval = 0.1
        self.base_image = self.image.copy()

    def _assign_random_behavior(self):
        if self.behavior_type_override:
            behavior_type = self.behavior_type_override
        else:
            behavior_types_str = self.config.get('Behaviors', 'behavior_types')
            behavior_types = [b.strip() for b in behavior_types_str.split(',')]
            behavior_type = random.choice(behavior_types)

        behavior_map = {
            'wanderer': WandererBehavior,
            'patrol': PatrolBehavior
        }

        behavior_class = behavior_map.get(behavior_type, WandererBehavior)
        return behavior_class(self)

    def can_move_in_direction(self, direction):
        """
        Check if movement in direction is valid (wall collision check).

        Args:
            direction: 'up', 'down', 'left', or 'right'

        Returns:
            bool: True if movement is valid
        """
        # Calculate target tile position
        target_x, target_y = self.tile_x, self.tile_y

        if direction == 'up':
            target_y -= 1
        elif direction == 'down':
            target_y += 1
        elif direction == 'left':
            target_x -= 1
        elif direction == 'right':
            target_x += 1

        # Check if target tile is valid
        return self.collision_manager.can_move_to_tile(
            self.tile_x, self.tile_y,
            target_x, target_y
        )

    def move_in_direction(self, direction):
        if direction == 'up':
            self.tile_y -= 1
        elif direction == 'down':
            self.tile_y += 1
        elif direction == 'left':
            self.tile_x -= 1
        elif direction == 'right':
            self.tile_x += 1

        self.rect.center = (
            self.offset_x + self.tile_x * self.tile_size + self.tile_size // 2,
            self.offset_y + self.tile_y * self.tile_size + self.tile_size // 2
        )

    def update(self, dt, player_pos):
        """
        Update enemy state and position.

        Args:
            dt: Delta time in seconds
            player_pos: Tuple of (x, y) player tile position
        """
        if self.is_dying:
            self._update_death_animation(dt)
            return

        self.frame_counter += 1

        if self.frame_counter >= self.update_interval:
            self.frame_counter = 0
            direction = self.behavior.update(dt * self.update_interval, player_pos)

            if direction and self.can_move_in_direction(direction):
                self.move_in_direction(direction)

    def die(self):
        if not self.is_dying:
            self.is_dying = True
            self.death_timer = 0.0
        return self.emoji, self.fact

    def _update_death_animation(self, dt):
        """
        Update flash and fade animation during death.

        Args:
            dt: Delta time in seconds
        """
        self.death_timer += dt

        if self.death_timer >= self.death_duration:
            self.kill()
            return

        progress = self.death_timer / self.death_duration
        flash_phase = int(self.death_timer / self.flash_interval) % 2

        if flash_phase == 0:
            self.image = self.base_image.copy()
        else:
            self.image = pygame.Surface(self.base_image.get_size(), pygame.SRCALPHA)

        alpha = int(255 * (1.0 - progress))
        self.image.set_alpha(alpha)

    def get_tile_position(self):
        """
        Get current position in tile coordinates.

        Returns:
            tuple: (tile_x, tile_y)
        """
        return (self.tile_x, self.tile_y)
