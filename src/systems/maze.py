import random
import pygame
import colorsys
from systems.maze_type_1 import MazeType1
from systems.maze_validator import MazeValidator
from systems.maze_looper import loop_maze
from systems.maze_constants import WALL, PATH


class Maze:
    def __init__(self, grid_size, tile_size, min_wall_length=1, max_wall_length=5,
                 orientation='vertical', max_attempts=100, generator=None):
        self.grid_size = grid_size
        self.tile_size = tile_size
        self.max_attempts = max_attempts
        self.generator = generator or MazeType1(min_wall_length, max_wall_length, orientation)
        self.grid = []
        self.start_pos = None
        self.end_pos = None
        self.wall_colors = self._generate_wall_colors()
        self._generate()

    def _generate(self):
        for _ in range(self.max_attempts):
            self.grid = self.generator.generate(self.grid_size)
            self._find_start_end_positions()

            validator = MazeValidator(self.grid, self.grid_size)
            if validator.is_connected(self.start_pos, self.end_pos) and validator.is_fully_traversable(self.start_pos):
                loop_maze(self)
                return

        self.grid = [[PATH] * self.grid_size for _ in range(self.grid_size)]
        self._find_start_end_positions()

    def _find_start_end_positions(self):
        corner_pairs = [
            ((1, 1), (self.grid_size - 2, self.grid_size - 2)),
            ((self.grid_size - 2, 1), (1, self.grid_size - 2))
        ]
        start_corner, end_corner = random.choice(corner_pairs)

        self.start_pos = self._find_path_near(start_corner) or start_corner
        self.end_pos = self._find_path_near(end_corner) or end_corner

    def _find_path_near(self, corner):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                pos = (corner[0] + dx, corner[1] + dy)
                if self._is_valid_position(pos) and not self.is_wall(*pos):
                    return pos
        return None

    def _is_valid_position(self, pos):
        x, y = pos
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def _generate_wall_colors(self):
        """Generate 12 color pairs (bright border, dark fill) from 12 hues"""
        colors = []
        for i in range(12):
            hue = i / 12.0  # Evenly spaced hues around color wheel

            # Bright border: high saturation, high value
            bright_rgb = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
            bright_color = tuple(int(c * 255) for c in bright_rgb)

            # Dark fill: high saturation, lower value
            dark_rgb = colorsys.hsv_to_rgb(hue, 0.80, 0.45)
            dark_color = tuple(int(c * 255) for c in dark_rgb)

            colors.append((bright_color, dark_color))

        return colors

    def get_start_position(self):
        return self.start_pos

    def get_end_position(self):
        return self.end_pos

    def is_wall(self, x, y):
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return True
        return self.grid[y][x] == WALL

    def can_move_to(self, from_x, from_y, to_x, to_y):
        return not self.is_wall(to_x, to_y)

    def render(self, surface, colors):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = self._create_tile_rect(x, y)

                if self.grid[y][x] == WALL:
                    # Get color pair for this wall
                    bright_color, dark_color = self._get_wall_color_pair(x, y)

                    # Draw bright border (full rectangle)
                    pygame.draw.rect(surface, bright_color, rect)

                    # Draw dark fill (inset by 8 pixels)
                    border_width = 8
                    inner_rect = pygame.Rect(
                        rect.x + border_width,
                        rect.y + border_width,
                        rect.width - (border_width * 2),
                        rect.height - (border_width * 2)
                    )

                    # Only draw inner rect if there's room for it
                    if inner_rect.width > 0 and inner_rect.height > 0:
                        pygame.draw.rect(surface, dark_color, inner_rect)
                else:
                    # Non-wall tiles use original color system
                    color = self._get_tile_color((x, y), colors)
                    pygame.draw.rect(surface, color, rect)

    def _create_tile_rect(self, x, y):
        return pygame.Rect(x * self.tile_size, y * self.tile_size,
                          self.tile_size, self.tile_size)

    def _get_tile_color(self, pos, colors):
        x, y = pos
        if self.grid[y][x] == WALL:
            return colors['wall']
        return colors['floor']

    def _get_wall_color_pair(self, x, y):
        """Get the color pair (bright, dark) for a wall at position (x, y)"""
        # Use position to deterministically select from the 12 hues
        # This creates a nice varied pattern across the maze
        color_index = (x * 7 + y * 11) % 12
        return self.wall_colors[color_index]