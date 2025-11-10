import random
import pygame
import colorsys
from systems.maze_type_1 import MazeType1
from systems.maze_validator import MazeValidator
from systems.maze_looper import loop_maze
from systems.maze_constants import WALL, PATH


class Maze:
    def __init__(self, grid_size, tile_size, min_wall_length=1, max_wall_length=5,
                 orientation='vertical', max_attempts=100, generator=None, corner_radius=4):
        self.grid_size = grid_size
        self.tile_size = tile_size
        self.corner_radius = corner_radius
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
        """Generate one random color pair (bright border, dark fill) from 12 hues for this level"""
        # Pick one random hue from 12 evenly-spaced hues
        hue_index = random.randint(0, 11)
        hue = hue_index / 12.0

        # Bright border: high saturation, high value
        bright_rgb = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
        bright_color = tuple(int(c * 255) for c in bright_rgb)

        # Dark fill: high saturation, lower value
        dark_rgb = colorsys.hsv_to_rgb(hue, 0.80, 0.45)
        dark_color = tuple(int(c * 255) for c in dark_rgb)

        return (bright_color, dark_color)

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
        bright_color, dark_color = self.wall_colors
        border_width = 8
        floor_color = colors['floor']

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = self._create_tile_rect(x, y)

                if self.grid[y][x] == WALL:
                    # Draw dark fill for entire wall tile
                    pygame.draw.rect(surface, dark_color, rect)

                    # Check which edges face non-walls (should have bright border)
                    has_wall_north = y > 0 and self.grid[y-1][x] == WALL
                    has_wall_south = y < self.grid_size - 1 and self.grid[y+1][x] == WALL
                    has_wall_west = x > 0 and self.grid[y][x-1] == WALL
                    has_wall_east = x < self.grid_size - 1 and self.grid[y][x+1] == WALL

                    # Draw bright border only on edges facing non-walls
                    if not has_wall_north:  # Top edge
                        pygame.draw.rect(surface, bright_color,
                                       pygame.Rect(rect.x, rect.y, rect.width, border_width))
                    if not has_wall_south:  # Bottom edge
                        pygame.draw.rect(surface, bright_color,
                                       pygame.Rect(rect.x, rect.y + rect.height - border_width,
                                                 rect.width, border_width))
                    if not has_wall_west:  # Left edge
                        pygame.draw.rect(surface, bright_color,
                                       pygame.Rect(rect.x, rect.y, border_width, rect.height))
                    if not has_wall_east:  # Right edge
                        pygame.draw.rect(surface, bright_color,
                                       pygame.Rect(rect.x + rect.width - border_width, rect.y,
                                                 border_width, rect.height))

                    # Draw inside corner rounded arcs where perpendicular walls meet
                    # Northwest inside corner: walls to north AND west
                    if has_wall_north and has_wall_west:
                        self._draw_inside_corner(surface, bright_color, rect.x, rect.y, 'nw')
                    # Northeast inside corner: walls to north AND east
                    if has_wall_north and has_wall_east:
                        self._draw_inside_corner(surface, bright_color, rect.x + rect.width, rect.y, 'ne')
                    # Southwest inside corner: walls to south AND west
                    if has_wall_south and has_wall_west:
                        self._draw_inside_corner(surface, bright_color, rect.x, rect.y + rect.height, 'sw')
                    # Southeast inside corner: walls to south AND east
                    if has_wall_south and has_wall_east:
                        self._draw_inside_corner(surface, bright_color, rect.x + rect.width, rect.y + rect.height, 'se')

                    # Detect and draw outside corners (wall protruding into path)
                    # NW outside corner: walls continue south & east, but not north & west
                    if has_wall_south and has_wall_east and not has_wall_north and not has_wall_west:
                        self._draw_outside_corner_cut(surface, floor_color, rect.x, rect.y, 'nw')
                    # NE outside corner: walls continue south & west, but not north & east
                    if has_wall_south and has_wall_west and not has_wall_north and not has_wall_east:
                        self._draw_outside_corner_cut(surface, floor_color, rect.x + rect.width, rect.y, 'ne')
                    # SW outside corner: walls continue north & east, but not south & west
                    if has_wall_north and has_wall_east and not has_wall_south and not has_wall_west:
                        self._draw_outside_corner_cut(surface, floor_color, rect.x, rect.y + rect.height, 'sw')
                    # SE outside corner: walls continue north & west, but not south & east
                    if has_wall_north and has_wall_west and not has_wall_south and not has_wall_east:
                        self._draw_outside_corner_cut(surface, floor_color, rect.x + rect.width, rect.y + rect.height, 'se')

                else:
                    # Non-wall tiles (paths)
                    color = self._get_tile_color((x, y), colors)
                    pygame.draw.rect(surface, color, rect)

                    # Draw rounded corners on path tiles adjacent to wall outside corners
                    has_wall_north = y > 0 and self.grid[y-1][x] == WALL
                    has_wall_south = y < self.grid_size - 1 and self.grid[y+1][x] == WALL
                    has_wall_west = x > 0 and self.grid[y][x-1] == WALL
                    has_wall_east = x < self.grid_size - 1 and self.grid[y][x+1] == WALL

                    # Check diagonals for outside corners
                    has_wall_nw = y > 0 and x > 0 and self.grid[y-1][x-1] == WALL
                    has_wall_ne = y > 0 and x < self.grid_size - 1 and self.grid[y-1][x+1] == WALL
                    has_wall_sw = y < self.grid_size - 1 and x > 0 and self.grid[y+1][x-1] == WALL
                    has_wall_se = y < self.grid_size - 1 and x < self.grid_size - 1 and self.grid[y+1][x+1] == WALL

                    # SE corner of path: if wall to north and wall to west but no wall NW diagonal
                    if has_wall_north and has_wall_west and not has_wall_nw:
                        self._draw_path_corner(surface, floor_color, rect.x, rect.y, 'se')
                    # SW corner of path: if wall to north and wall to east but no wall NE diagonal
                    if has_wall_north and has_wall_east and not has_wall_ne:
                        self._draw_path_corner(surface, floor_color, rect.x + rect.width, rect.y, 'sw')
                    # NE corner of path: if wall to south and wall to west but no wall SW diagonal
                    if has_wall_south and has_wall_west and not has_wall_sw:
                        self._draw_path_corner(surface, floor_color, rect.x, rect.y + rect.height, 'ne')
                    # NW corner of path: if wall to south and wall to east but no wall SE diagonal
                    if has_wall_south and has_wall_east and not has_wall_se:
                        self._draw_path_corner(surface, floor_color, rect.x + rect.width, rect.y + rect.height, 'nw')

    def _create_tile_rect(self, x, y):
        return pygame.Rect(x * self.tile_size, y * self.tile_size,
                          self.tile_size, self.tile_size)

    def _get_tile_color(self, pos, colors):
        x, y = pos
        if self.grid[y][x] == WALL:
            return colors['wall']
        return colors['floor']

    def _draw_inside_corner(self, surface, color, x, y, corner):
        """Draw a rounded inside corner (bright arc where two walls meet)"""
        radius = self.corner_radius

        # Draw a small filled circle at the corner intersection point
        # The radius is small enough (4px) that it creates a nice rounded corner effect
        pygame.draw.circle(surface, color, (x, y), radius)

    def _draw_outside_corner_cut(self, surface, color, x, y, corner):
        """Draw a quarter-circle cut in floor color to round off wall outside corners"""
        radius = self.corner_radius

        # Draw a filled circle at the corner to "cut" it and create a rounded appearance
        pygame.draw.circle(surface, color, (x, y), radius)

    def _draw_path_corner(self, surface, color, x, y, corner):
        """Draw a rounded corner on path tiles adjacent to wall outside corners"""
        radius = self.corner_radius

        # Draw a filled circle at the path tile corner to match the wall's rounded corner
        pygame.draw.circle(surface, color, (x, y), radius)