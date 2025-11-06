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

    def __init__(self, x, y, config, collision_manager, emoji="🐱", behavior_type=None):
        """
        Initialize enemy at grid position (x, y).

        Args:
            x: Grid X position (tile coordinates)
            y: Grid Y position (tile coordinates)
            config: ConfigParser object with gameplay and enemy settings
            collision_manager: CollisionManager instance for wall detection
            emoji: Emoji character to display (default: "🐱")
            behavior_type: Specific behavior type ('wanderer' or 'patrol'), or None for random
        """
        super().__init__()

        # Store references
        self.config = config
        self.collision_manager = collision_manager
        self.behavior_type_override = behavior_type

        # Load tile size from maze config
        self.tile_size = config.getint('Maze', 'tile_size')

        # Randomize attributes
        speed_min = config.getint('Attributes', 'speed_min')
        speed_max = config.getint('Attributes', 'speed_max')
        awareness_min = config.getint('Attributes', 'awareness_min')
        awareness_max = config.getint('Attributes', 'awareness_max')

        self.speed = random.randint(speed_min, speed_max)  # Tiles per second
        self.awareness = random.randint(awareness_min, awareness_max)  # Tile radius

        # Movement configuration - calculate update_interval based on individual speed
        # Higher speed = lower update_interval (moves more frequently)
        fps = config.getint('Gameplay', 'fps')
        self.update_interval = fps // self.speed  # frames between moves
        self.frame_counter = 0

        # Position tracking
        self.tile_x = x
        self.tile_y = y

        # Create visual representation (emoji)
        self.render_emoji = True
        self.emoji = emoji

        # Create surface for rendering
        if self.render_emoji:
            # Use pygame-emojis to render emoji with proper color support
            emoji_size = int(self.tile_size * 0.8)
            emoji_surface = load_emoji(self.emoji, (emoji_size, emoji_size))

            # Create image surface
            self.image = pygame.Surface((self.tile_size - 4, self.tile_size - 4), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))  # Transparent background

            # Center the emoji on the surface
            emoji_rect = emoji_surface.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
            self.image.blit(emoji_surface, emoji_rect)
        else:
            # Fallback to colored rectangle
            self.image = pygame.Surface((self.tile_size - 4, self.tile_size - 4))
            color = tuple(map(int, config.get('Colors', 'enemy').split(',')))
            self.image.fill(color)

        # Position sprite
        self.rect = self.image.get_rect()
        self.rect.center = (
            x * self.tile_size + self.tile_size // 2,
            y * self.tile_size + self.tile_size // 2
        )

        # Initialize behavior (random selection for Phase A5)
        self.behavior = self._assign_random_behavior()

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
        """
        Move enemy one tile in the given direction.

        Args:
            direction: 'up', 'down', 'left', or 'right'
        """
        if direction == 'up':
            self.tile_y -= 1
        elif direction == 'down':
            self.tile_y += 1
        elif direction == 'left':
            self.tile_x -= 1
        elif direction == 'right':
            self.tile_x += 1

        # Update sprite position to match tile position
        self.rect.center = (
            self.tile_x * self.tile_size + self.tile_size // 2,
            self.tile_y * self.tile_size + self.tile_size // 2
        )

    def update(self, dt, player_pos):
        """
        Update enemy state and position.

        Args:
            dt: Delta time in seconds
            player_pos: Tuple of (x, y) player tile position
        """
        # Increment frame counter
        self.frame_counter += 1

        # Only update movement every N frames
        if self.frame_counter >= self.update_interval:
            self.frame_counter = 0

            # Get direction from behavior
            direction = self.behavior.update(dt * self.update_interval, player_pos)

            # Move if we have a valid direction
            if direction and self.can_move_in_direction(direction):
                self.move_in_direction(direction)

    def get_tile_position(self):
        """
        Get current position in tile coordinates.

        Returns:
            tuple: (tile_x, tile_y)
        """
        return (self.tile_x, self.tile_y)
