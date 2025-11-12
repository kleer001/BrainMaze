"""
Player entity with buffered input and corner forgiveness.
Phase A4: Movement with wall collision detection and invincibility system.
"""

import pygame
import math
from pygame_emojis import load_emoji


class Vector2:
    """Simple 2D vector class for position and velocity."""
    
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)


class Player(pygame.sprite.Sprite):
    """
    Player sprite with continuous movement and industry-standard input buffering.
    """
    
    def __init__(self, x, y, config, collision_manager, maze):
        super().__init__()

        self.collision_manager = collision_manager
        self.maze = maze
        self.tile_size = maze.tile_size
        self.offset_x = maze.offset_x
        self.offset_y = maze.offset_y

        self.base_speed = config.getfloat('Player', 'base_speed')
        self.input_buffer_duration = config.getfloat('Player', 'input_buffer_duration')
        self.corner_forgiveness = config.getint('Player', 'corner_forgiveness')
        self.invincibility_duration = config.getfloat('Player', 'invincibility_duration')
        self.pulse_frequency = config.getfloat('Effects', 'invincibility_pulse_frequency')
        self.freeze_duration = config.getfloat('Capture', 'freeze_duration')
        self.flicker_frequency = config.getfloat('Capture', 'flicker_frequency')
        self.glow_intensity = config.getfloat('Capture', 'glow_intensity')
        glow_color_str = config.get('Capture', 'glow_color')
        self.glow_color = tuple(map(int, glow_color_str.split(',')))

        self.speed_pixels_per_second = self.base_speed * self.tile_size

        emoji_size = self.tile_size - 4
        brain_emoji = load_emoji('🧠', (emoji_size, emoji_size))
        self.image = pygame.Surface((emoji_size, emoji_size), pygame.SRCALPHA)
        self.image.blit(brain_emoji, (0, 0))
        self.base_image = self.image.copy()
        self.facing_right = True

        self.spawn_x = x
        self.spawn_y = y

        self.rect = self.image.get_rect()
        self.rect.center = (
            self.offset_x + x * self.tile_size + self.tile_size // 2,
            self.offset_y + y * self.tile_size + self.tile_size // 2
        )

        self.pos = Vector2(self.rect.centerx, self.rect.centery)
        
        # Movement state
        self.velocity = Vector2(0, 0)
        self.current_direction = None  # 'up', 'down', 'left', 'right', or None
        self.is_moving = False  # True when committed to a tile movement
        self.target_pos = None  # Target tile center we're moving toward
        
        # Input buffering
        self.buffered_direction = None
        self.buffer_timer = 0.0

        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.pulse_timer = 0.0

        self.is_frozen = False
        self.freeze_timer = 0.0
        self.flicker_timer = 0.0
        
    def handle_input(self, keys):
        from pygame import K_w, K_s, K_a, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT

        if self.is_frozen:
            return
        
        # Determine desired direction from input
        desired_direction = None
        
        if keys[K_w] or keys[K_UP]:
            desired_direction = 'up'
        elif keys[K_s] or keys[K_DOWN]:
            desired_direction = 'down'
        elif keys[K_a] or keys[K_LEFT]:
            desired_direction = 'left'
        elif keys[K_d] or keys[K_RIGHT]:
            desired_direction = 'right'
        
        # If we're currently moving, buffer the new input
        if self.is_moving and desired_direction and desired_direction != self.current_direction:
            self.buffered_direction = desired_direction
            self.buffer_timer = self.input_buffer_duration
        
        # If we're not moving and have input, start moving
        elif not self.is_moving and desired_direction:
            if self._can_move_in_direction(desired_direction):
                self._start_movement(desired_direction)
                self.buffered_direction = None
                self.buffer_timer = 0.0
            else:
                # Can't move that way, buffer it
                self.buffered_direction = desired_direction
                self.buffer_timer = self.input_buffer_duration
    
    def update(self, dt):
        if self.is_frozen:
            self.freeze_timer -= dt
            self.flicker_timer += dt

            if self.freeze_timer <= 0:
                self.is_frozen = False
                self.freeze_timer = 0.0
                self.image.set_alpha(255)
            else:
                flicker_cycle = 1.0 / self.flicker_frequency
                flicker_phase = (self.flicker_timer % flicker_cycle) / flicker_cycle
                alpha = int(255 * (0.3 + 0.7 * abs(math.sin(flicker_phase * math.pi))))
                self.image.set_alpha(alpha)
            return

        if self.is_invincible:
            self.invincibility_timer -= dt
            self.pulse_timer += dt

            if self.invincibility_timer <= 0:
                self.is_invincible = False
                self.invincibility_timer = 0.0
                self.image.set_alpha(255)
            else:
                pulse_value = math.sin(self.pulse_timer * 2 * math.pi / self.pulse_frequency)
                alpha = int(255 * (0.8 + pulse_value * 0.2))
                self.image.set_alpha(alpha)

        # If we're moving toward a target
        if self.is_moving and self.target_pos:
            # Move toward target
            self.pos.x += self.velocity.x * dt
            self.pos.y += self.velocity.y * dt
            
            # Check if we've reached or passed the target
            reached = False
            if self.current_direction == 'up' and self.pos.y <= self.target_pos.y:
                reached = True
            elif self.current_direction == 'down' and self.pos.y >= self.target_pos.y:
                reached = True
            elif self.current_direction == 'left' and self.pos.x <= self.target_pos.x:
                reached = True
            elif self.current_direction == 'right' and self.pos.x >= self.target_pos.x:
                reached = True
            
            # Snap to target when reached
            if reached:
                self.pos.x = self.target_pos.x
                self.pos.y = self.target_pos.y
                self.is_moving = False
                self.velocity = Vector2(0, 0)
                
                # Try to execute buffered input immediately
                if self.buffered_direction and self._can_move_in_direction(self.buffered_direction):
                    self._start_movement(self.buffered_direction)
                    self.buffered_direction = None
                    self.buffer_timer = 0.0
        
        # Not moving, check buffered input timer
        elif self.buffered_direction and self.buffer_timer > 0:
            self.buffer_timer -= dt
            
            if self._can_move_in_direction(self.buffered_direction):
                self._start_movement(self.buffered_direction)
                self.buffered_direction = None
                self.buffer_timer = 0.0
        
        # Clear expired buffer
        if self.buffer_timer <= 0:
            self.buffered_direction = None
        
        # Update rect position (for rendering and collision)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
    
    def _can_move_in_direction(self, direction):
        """
        Check if movement in direction is valid (wall collision check).
        Includes corner forgiveness for smooth movement.

        Args:
            direction: 'up', 'down', 'left', or 'right'

        Returns:
            bool: True if movement is valid
        """
        # Get current tile position
        current_tile_x, current_tile_y = self.get_tile_position()

        # Calculate target tile position
        target_tile_x, target_tile_y = current_tile_x, current_tile_y
        if direction == 'up':
            target_tile_y -= 1
        elif direction == 'down':
            target_tile_y += 1
        elif direction == 'left':
            target_tile_x -= 1
        elif direction == 'right':
            target_tile_x += 1

        # Check basic wall collision
        can_move = self.collision_manager.can_move_to_tile(
            current_tile_x, current_tile_y,
            target_tile_x, target_tile_y
        )

        if can_move:
            return True

        # If basic check fails, try corner forgiveness
        can_move_cf, adj_x, adj_y = self.collision_manager.check_corner_forgiveness(
            self.pos.x, self.pos.y, direction
        )

        if can_move_cf:
            # Apply corner forgiveness adjustment (snap to center)
            self.pos.x = adj_x
            self.pos.y = adj_y

            # Recalculate tile positions after snapping to center
            current_tile_x, current_tile_y = self.get_tile_position()

            # Recalculate target tile position
            target_tile_x, target_tile_y = current_tile_x, current_tile_y
            if direction == 'up':
                target_tile_y -= 1
            elif direction == 'down':
                target_tile_y += 1
            elif direction == 'left':
                target_tile_x -= 1
            elif direction == 'right':
                target_tile_x += 1

            # Recheck if movement is valid after snapping
            return self.collision_manager.can_move_to_tile(
                current_tile_x, current_tile_y,
                target_tile_x, target_tile_y
            )

        return False
    
    def _start_movement(self, direction):
        """
        Start movement in a direction toward the next tile center.

        Args:
            direction: 'up', 'down', 'left', or 'right'
        """
        self.current_direction = direction
        self.is_moving = True

        current_tile_x, current_tile_y = self.get_tile_position()

        if direction == 'up':
            target_tile_y = current_tile_y - 1
            target_tile_x = current_tile_x
            self.velocity = Vector2(0, -self.speed_pixels_per_second)
        elif direction == 'down':
            target_tile_y = current_tile_y + 1
            target_tile_x = current_tile_x
            self.velocity = Vector2(0, self.speed_pixels_per_second)
        elif direction == 'left':
            target_tile_x = current_tile_x - 1
            target_tile_y = current_tile_y
            self.velocity = Vector2(-self.speed_pixels_per_second, 0)
            self._update_facing(False)
        elif direction == 'right':
            target_tile_x = current_tile_x + 1
            target_tile_y = current_tile_y
            self.velocity = Vector2(self.speed_pixels_per_second, 0)
            self._update_facing(True)

        self.target_pos = Vector2(
            self.offset_x + target_tile_x * self.tile_size + self.tile_size // 2,
            self.offset_y + target_tile_y * self.tile_size + self.tile_size // 2
        )
    
    def _update_facing(self, facing_right):
        """
        Update brain emoji facing direction.

        Args:
            facing_right: True if facing right, False if facing left
        """
        if facing_right != self.facing_right:
            self.facing_right = facing_right
            self.image = pygame.transform.flip(self.base_image, True, False)
            self.base_image = self.image.copy()

    def get_tile_position(self):
        tile_x = int((self.pos.x - self.offset_x) // self.tile_size)
        tile_y = int((self.pos.y - self.offset_y) // self.tile_size)
        return (tile_x, tile_y)

    def respawn(self):
        spawn_pixel_x = self.offset_x + self.spawn_x * self.tile_size + self.tile_size // 2
        spawn_pixel_y = self.offset_y + self.spawn_y * self.tile_size + self.tile_size // 2
        self.pos.x = spawn_pixel_x
        self.pos.y = spawn_pixel_y
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Stop movement
        self.velocity = Vector2(0, 0)
        self.is_moving = False
        self.target_pos = None
        self.current_direction = None

        # Clear buffered input
        self.buffered_direction = None
        self.buffer_timer = 0.0

        # Activate invincibility
        self.is_invincible = True
        self.invincibility_timer = self.invincibility_duration
        self.pulse_timer = 0.0

    def can_take_damage(self):
        return not self.is_invincible

    def freeze(self):
        self.is_frozen = True
        self.freeze_timer = self.freeze_duration
        self.flicker_timer = 0.0

        self.velocity = Vector2(0, 0)
        self.is_moving = False
        self.target_pos = None
        self.current_direction = None
        self.buffered_direction = None
        self.buffer_timer = 0.0