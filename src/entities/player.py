"""
Player entity with buffered input and corner forgiveness.
Phase A1: Movement in empty space (no walls yet).
"""

import pygame


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
    
    def __init__(self, x, y, config):
        """
        Initialize player at grid position (x, y).
        
        Args:
            x: Grid X position (tile coordinates)
            y: Grid Y position (tile coordinates)
            config: ConfigParser object with gameplay settings
        """
        super().__init__()
        
        # Load configuration
        self.tile_size = config.getint('Maze', 'tile_size')
        self.base_speed = config.getfloat('Player', 'base_speed')
        self.input_buffer_duration = config.getfloat('Player', 'input_buffer_duration')
        self.corner_forgiveness = config.getint('Player', 'corner_forgiveness')
        
        # Convert speed from tiles/second to pixels/second
        self.speed_pixels_per_second = self.base_speed * self.tile_size
        
        # Create sprite (colored rectangle for now)
        self.image = pygame.Surface((self.tile_size - 4, self.tile_size - 4))
        color = tuple(map(int, config.get('Colors', 'player').split(',')))
        self.image.fill(color)
        
        # Position (center of tile in pixel coordinates)
        self.rect = self.image.get_rect()
        self.rect.center = (
            x * self.tile_size + self.tile_size // 2,
            y * self.tile_size + self.tile_size // 2
        )
        
        # Use float position for smooth movement
        self.pos = Vector2(self.rect.centerx, self.rect.centery)
        
        # Movement state
        self.velocity = Vector2(0, 0)
        self.current_direction = None  # 'up', 'down', 'left', 'right', or None
        self.is_moving = False  # True when committed to a tile movement
        self.target_pos = None  # Target tile center we're moving toward
        
        # Input buffering
        self.buffered_direction = None
        self.buffer_timer = 0.0
        
    def handle_input(self, keys):
        """
        Process keyboard input with buffering.
        Only accepts new direction when not currently committed to a movement.
        
        Args:
            keys: pygame.key.get_pressed() result
        """
        # Import key constants
        from pygame import K_w, K_s, K_a, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT
        
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
        """
        Update player position with grid-snapped movement.
        Player commits to full tile movements.
        
        Args:
            dt: Delta time in seconds
        """
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
        
        # Keep player on screen (temporary, will be replaced by wall collision)
        screen_width = self.tile_size * 20  # 20x20 grid
        screen_height = self.tile_size * 20
        
        half_tile = self.tile_size // 2
        if self.pos.x < half_tile:
            self.pos.x = half_tile
            self.is_moving = False
            self.velocity = Vector2(0, 0)
        elif self.pos.x > screen_width - half_tile:
            self.pos.x = screen_width - half_tile
            self.is_moving = False
            self.velocity = Vector2(0, 0)
            
        if self.pos.y < half_tile:
            self.pos.y = half_tile
            self.is_moving = False
            self.velocity = Vector2(0, 0)
        elif self.pos.y > screen_height - half_tile:
            self.pos.y = screen_height - half_tile
            self.is_moving = False
            self.velocity = Vector2(0, 0)
    
    def _can_move_in_direction(self, direction):
        """
        Check if movement in direction is valid (wall collision check).
        Phase A1: Always returns True (no walls yet).
        Phase A2: Will check maze walls with corner forgiveness.
        
        Args:
            direction: 'up', 'down', 'left', or 'right'
            
        Returns:
            bool: True if movement is valid
        """
        # TODO Phase A2: Implement wall collision checking with corner forgiveness
        return True
    
    def _start_movement(self, direction):
        """
        Start movement in a direction toward the next tile center.
        
        Args:
            direction: 'up', 'down', 'left', or 'right'
        """
        self.current_direction = direction
        self.is_moving = True
        
        # Calculate target position (center of next tile)
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
        elif direction == 'right':
            target_tile_x = current_tile_x + 1
            target_tile_y = current_tile_y
            self.velocity = Vector2(self.speed_pixels_per_second, 0)
        
        # Calculate pixel position of target tile center
        self.target_pos = Vector2(
            target_tile_x * self.tile_size + self.tile_size // 2,
            target_tile_y * self.tile_size + self.tile_size // 2
        )
    
    def get_tile_position(self):
        """
        Get current position in tile coordinates.
        
        Returns:
            tuple: (tile_x, tile_y)
        """
        tile_x = int(self.pos.x // self.tile_size)
        tile_y = int(self.pos.y // self.tile_size)
        return (tile_x, tile_y)