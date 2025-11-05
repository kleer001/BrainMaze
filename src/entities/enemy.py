import pygame
import random
from pygame_emojis import load_emoji
from entities.grid_entity import GridEntity
from utils.direction import apply_direction
from ai.behaviors import WandererBehavior, PatrolBehavior

EMOJI_SIZE_RATIO = 0.8

class Enemy(GridEntity):
    def __init__(self, x, y, config, collision_manager):
        self.tile_size = config.getint('Maze', 'tile_size')
        super().__init__(x, y, self.tile_size)

        self.config = config
        self.collision_manager = collision_manager
        self.tile_x = x
        self.tile_y = y

        self._randomize_attributes(config)
        self._init_movement_config(config)
        self._create_visual(config)
        self._position_at_tile(x, y)
        self.behavior = self._assign_random_behavior()

    def _randomize_attributes(self, config):
        speed_min = config.getint('Attributes', 'speed_min')
        speed_max = config.getint('Attributes', 'speed_max')
        awareness_min = config.getint('Attributes', 'awareness_min')
        awareness_max = config.getint('Attributes', 'awareness_max')

        self.speed = random.randint(speed_min, speed_max)
        self.awareness = random.randint(awareness_min, awareness_max)

    def _init_movement_config(self, config):
        self.update_interval = config.getint('Movement', 'update_interval')
        self.frame_counter = 0

    def _create_visual(self, config):
        self.emoji = "🐱"
        self._render_emoji_visual(config)

    def _render_emoji_visual(self, config):
        emoji_size = int(self.tile_size * EMOJI_SIZE_RATIO)
        emoji_surface = load_emoji(self.emoji, (emoji_size, emoji_size))

        self.image = pygame.Surface((self.tile_size - 4, self.tile_size - 4), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        emoji_rect = emoji_surface.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
        self.image.blit(emoji_surface, emoji_rect)

        self.rect = self.image.get_rect()

    def _assign_random_behavior(self):
        behavior_types_str = self.config.get('Behaviors', 'behavior_types')
        behavior_types = [b.strip() for b in behavior_types_str.split(',')]
        behavior_type = random.choice(behavior_types)

        if behavior_type == 'wanderer':
            return WandererBehavior(self)
        elif behavior_type == 'patrol':
            return PatrolBehavior(self)
        else:
            return WandererBehavior(self)

    def can_move_in_direction(self, direction):
        target_x, target_y = apply_direction(self.tile_x, self.tile_y, direction)
        return self.collision_manager.can_move_to_tile(self.tile_x, self.tile_y, target_x, target_y)

    def move_in_direction(self, direction):
        self.tile_x, self.tile_y = apply_direction(self.tile_x, self.tile_y, direction)
        self._position_at_tile(self.tile_x, self.tile_y)

    def update(self, dt, player_pos):
        self.frame_counter += 1

        if self.frame_counter >= self.update_interval:
            self.frame_counter = 0

            direction = self.behavior.update(dt * self.update_interval, player_pos)

            if direction and self.can_move_in_direction(direction):
                self.move_in_direction(direction)

    def get_tile_position(self):
        return (self.tile_x, self.tile_y)
