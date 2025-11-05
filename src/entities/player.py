import pygame
import math
from entities.grid_entity import GridEntity
from utils.vector2 import Vector2
from utils.direction import UP, DOWN, LEFT, RIGHT, apply_direction

BRIGHTNESS_AMPLITUDE = 0.4
MIN_BRIGHTNESS = 0.6
MAX_BRIGHTNESS = 1.4

class Player(GridEntity):
    def __init__(self, x, y, config, collision_manager):
        self.tile_size = config.getint('Maze', 'tile_size')
        super().__init__(x, y, self.tile_size)

        self.collision_manager = collision_manager
        self._load_config(config)
        self._init_visual()
        self._init_movement()
        self._init_input_buffer()
        self._init_invincibility()
        self._store_spawn(x, y)

    def _load_config(self, config):
        self.base_speed = config.getfloat('Player', 'base_speed')
        self.input_buffer_duration = config.getfloat('Player', 'input_buffer_duration')
        self.corner_forgiveness = config.getint('Player', 'corner_forgiveness')
        self.invincibility_duration = config.getfloat('Player', 'invincibility_duration')
        self.pulse_frequency = config.getfloat('Effects', 'invincibility_pulse_frequency')
        self.speed_pixels_per_second = self.base_speed * self.tile_size
        self.base_color = tuple(map(int, config.get('Colors', 'player').split(',')))

    def _init_visual(self):
        self.image = pygame.Surface((self.tile_size - 4, self.tile_size - 4))
        self.image.fill(self.base_color)
        self.rect = self.image.get_rect()
        self._position_at_tile(*self.get_tile_position())

    def _init_movement(self):
        self.pos = Vector2(self.rect.centerx, self.rect.centery)
        self.velocity = Vector2(0, 0)
        self.current_direction = None
        self.is_moving = False
        self.target_pos = None

    def _init_input_buffer(self):
        self.buffered_direction = None
        self.buffer_timer = 0.0

    def _init_invincibility(self):
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.pulse_timer = 0.0

    def _store_spawn(self, x, y):
        self.spawn_x = x
        self.spawn_y = y

    def handle_input(self, keys):
        from pygame import K_w, K_s, K_a, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT

        desired_direction = self._get_desired_direction(keys, {
            UP: [K_w, K_UP],
            DOWN: [K_s, K_DOWN],
            LEFT: [K_a, K_LEFT],
            RIGHT: [K_d, K_RIGHT]
        })

        if self.is_moving and desired_direction and desired_direction != self.current_direction:
            self._buffer_input(desired_direction)
        elif not self.is_moving and desired_direction:
            self._try_start_movement_or_buffer(desired_direction)

    def _get_desired_direction(self, keys, key_map):
        for direction, key_list in key_map.items():
            if any(keys[k] for k in key_list):
                return direction
        return None

    def _buffer_input(self, direction):
        self.buffered_direction = direction
        self.buffer_timer = self.input_buffer_duration

    def _try_start_movement_or_buffer(self, direction):
        if self._can_move_in_direction(direction):
            self._start_movement(direction)
            self._clear_buffer()
        else:
            self._buffer_input(direction)

    def _clear_buffer(self):
        self.buffered_direction = None
        self.buffer_timer = 0.0

    def update(self, dt):
        self._update_invincibility(dt)

        if self.is_moving and self.target_pos:
            self._update_movement(dt)
        elif self.buffered_direction and self.buffer_timer > 0:
            self._update_buffered_input(dt)

        if self.buffer_timer <= 0:
            self.buffered_direction = None

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def _update_invincibility(self, dt):
        if not self.is_invincible:
            return

        self.invincibility_timer -= dt
        self.pulse_timer += dt

        if self.invincibility_timer <= 0:
            self._deactivate_invincibility()
        else:
            self._apply_invincibility_visual()

    def _deactivate_invincibility(self):
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.image.fill(self.base_color)

    def _apply_invincibility_visual(self):
        pulse_value = math.sin(self.pulse_timer * 2 * math.pi / self.pulse_frequency)
        brightness = 1.0 + (pulse_value * BRIGHTNESS_AMPLITUDE)
        pulsed_color = tuple(min(255, int(c * brightness)) for c in self.base_color)
        self.image.fill(pulsed_color)

    def _update_movement(self, dt):
        self.pos.x += self.velocity.x * dt
        self.pos.y += self.velocity.y * dt

        if self._has_reached_target():
            self._snap_to_target()
            self._stop_movement()

            if self.buffered_direction and self._can_move_in_direction(self.buffered_direction):
                self._start_movement(self.buffered_direction)
                self._clear_buffer()

    def _has_reached_target(self):
        if self.current_direction == UP:
            return self.pos.y <= self.target_pos.y
        if self.current_direction == DOWN:
            return self.pos.y >= self.target_pos.y
        if self.current_direction == LEFT:
            return self.pos.x <= self.target_pos.x
        if self.current_direction == RIGHT:
            return self.pos.x >= self.target_pos.x
        return False

    def _snap_to_target(self):
        self.pos.x = self.target_pos.x
        self.pos.y = self.target_pos.y

    def _stop_movement(self):
        self.is_moving = False
        self.velocity = Vector2(0, 0)

    def _update_buffered_input(self, dt):
        self.buffer_timer -= dt

        if self._can_move_in_direction(self.buffered_direction):
            self._start_movement(self.buffered_direction)
            self._clear_buffer()

    def _can_move_in_direction(self, direction):
        current_tile_x, current_tile_y = self.get_tile_position()
        target_tile_x, target_tile_y = apply_direction(current_tile_x, current_tile_y, direction)

        if self.collision_manager.can_move_to_tile(current_tile_x, current_tile_y, target_tile_x, target_tile_y):
            return True

        return self._try_corner_forgiveness(direction, current_tile_x, current_tile_y, target_tile_x, target_tile_y)

    def _try_corner_forgiveness(self, direction, current_tile_x, current_tile_y, target_tile_x, target_tile_y):
        can_move, adj_x, adj_y = self.collision_manager.check_corner_forgiveness(
            self.pos.x, self.pos.y, direction
        )

        if not can_move:
            return False

        self.pos.x = adj_x
        self.pos.y = adj_y

        current_tile_x, current_tile_y = self.get_tile_position()
        target_tile_x, target_tile_y = apply_direction(current_tile_x, current_tile_y, direction)

        return self.collision_manager.can_move_to_tile(current_tile_x, current_tile_y, target_tile_x, target_tile_y)

    def _start_movement(self, direction):
        self.current_direction = direction
        self.is_moving = True

        current_tile_x, current_tile_y = self.get_tile_position()
        target_tile_x, target_tile_y = apply_direction(current_tile_x, current_tile_y, direction)

        self.velocity = self._calculate_velocity(direction)
        target_center_x, target_center_y = self.tile_utils.tile_to_pixel_center(target_tile_x, target_tile_y)
        self.target_pos = Vector2(target_center_x, target_center_y)

    def _calculate_velocity(self, direction):
        if direction == UP:
            return Vector2(0, -self.speed_pixels_per_second)
        if direction == DOWN:
            return Vector2(0, self.speed_pixels_per_second)
        if direction == LEFT:
            return Vector2(-self.speed_pixels_per_second, 0)
        if direction == RIGHT:
            return Vector2(self.speed_pixels_per_second, 0)
        return Vector2(0, 0)

    def respawn(self):
        spawn_pixel_x, spawn_pixel_y = self.tile_utils.tile_to_pixel_center(self.spawn_x, self.spawn_y)
        self.pos.x = spawn_pixel_x
        self.pos.y = spawn_pixel_y
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self._stop_movement()
        self.target_pos = None
        self.current_direction = None
        self._clear_buffer()

        self.is_invincible = True
        self.invincibility_timer = self.invincibility_duration
        self.pulse_timer = 0.0

    def can_take_damage(self):
        return not self.is_invincible
