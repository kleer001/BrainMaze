"""
Maze generation system using corridor-carving algorithm with perfect symmetry.
"""

import random
import pygame
import configparser
from pathlib import Path
from collections import deque
from enum import Enum

WALL = 1
PATH = 0

INTERNAL_WALL = 0
INTERNAL_CORRIDOR = 1


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def turn_right(self):
        """Rotate 90° clockwise."""
        turns = {
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
        }
        return turns[self]


class Maze:
    """
    Maze generator with perfect left-right symmetry.
    """

    def __init__(self, grid_size, tile_size, wall_density=0.2, max_wall_length=4, max_attempts=100):
        """
        Initialize maze generator.

        Args:
            grid_size: Total grid size (e.g., 20 for 20x20 grid)
            tile_size: Size of each tile in pixels
            wall_density: Ignored, kept for API compatibility
            max_wall_length: Ignored, kept for API compatibility
            max_attempts: Ignored, kept for API compatibility
        """
        self.tile_size = tile_size

        if grid_size % 2 == 0:
            grid_size += 1

        self.grid_size = grid_size
        self.grid = []
        self.start_pos = None
        self.end_pos = None

        config = self._load_config()
        self.fill_target = config.getfloat('Generation', 'fill_target')
        self.chamber_min = config.getint('Generation', 'chamber_min_size')
        self.chamber_max = config.getint('Generation', 'chamber_max_size')
        self.corridor_len_min = config.getint('Generation', 'corridor_length_min')
        self.corridor_len_max = config.getint('Generation', 'corridor_length_max')
        self.generation_attempts = config.getint('Generation', 'max_attempts')

        self._generate()

    def _load_config(self):
        """Load maze generation configuration."""
        config = configparser.ConfigParser()
        config_path = Path('config/maze_config.ini')

        if config_path.exists():
            config.read(config_path)
        else:
            config['Generation'] = {
                'fill_target': '0.8',
                'chamber_min_size': '3',
                'chamber_max_size': '5',
                'corridor_length_min': '3',
                'corridor_length_max': '8',
                'max_attempts': '5'
            }

        return config

    def _generate(self):
        """Generate maze using corridor-carving algorithm."""
        for attempt in range(self.generation_attempts):
            internal_grid = [[INTERNAL_WALL for _ in range(self.grid_size)] for _ in range(self.grid_size)]

            chamber_size = random.randint(self.chamber_min, self.chamber_max)
            self._carve_chamber(internal_grid, 1, 1, chamber_size, chamber_size)
            self._carve_chamber(internal_grid, 1, self.grid_size - chamber_size - 1, chamber_size, chamber_size)
            self._mirror_to_right(internal_grid)

            if self._carve_corridors(internal_grid):
                self._mirror_to_right(internal_grid)
                self._convert_grid(internal_grid)
                self._find_start_end()
                if self._is_connected():
                    return

        self.grid = [[PATH for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.start_pos = (1, 1)
        self.end_pos = (self.grid_size - 2, self.grid_size - 2)

    def _carve_chamber(self, grid, x, y, width, height):
        """Carve a rectangular chamber."""
        for cy in range(y, min(y + height, self.grid_size)):
            for cx in range(x, min(x + width, self.grid_size)):
                grid[cy][cx] = INTERNAL_CORRIDOR

    def _mirror_to_right(self, grid):
        """Mirror left half to right half across vertical axis."""
        middle = self.grid_size // 2
        for y in range(self.grid_size):
            for x in range(middle + 1):
                mirror_x = self.grid_size - 1 - x
                grid[y][mirror_x] = grid[y][x]

    def _carve_corridors(self, grid):
        """Carve corridors on left half until fill target reached."""
        iterations = 0
        max_iterations = 10000

        while self._get_projected_fill(grid) < self.fill_target and iterations < max_iterations:
            iterations += 1
            frontier_cells = self._get_frontier_cells(grid)

            if not frontier_cells:
                break

            start_cell = random.choice(frontier_cells)
            self._carve_pattern_from(grid, start_cell)

        return self._get_projected_fill(grid) >= self.fill_target

    def _get_frontier_cells(self, grid):
        """Get all corridor cells adjacent to walls on left half."""
        frontier = []
        middle = self.grid_size // 2

        for y in range(self.grid_size):
            for x in range(middle + 1):
                if grid[y][x] == INTERNAL_CORRIDOR:
                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if self._is_valid(nx, ny) and grid[ny][nx] == INTERNAL_WALL:
                            frontier.append((x, y))
                            break

        return frontier

    def _carve_pattern_from(self, grid, start_pos):
        """Carve an L-shaped pattern from start position."""
        x, y = start_pos
        initial_dir = random.choice(list(Direction))

        segments = [
            ('A', initial_dir),
            ('B', initial_dir.turn_right()),
            ('A', initial_dir.turn_right().turn_right()),
            ('B', initial_dir.turn_right().turn_right().turn_right()),
        ]

        current_x, current_y = x, y

        for segment_type, direction in segments:
            length = random.randint(self.corridor_len_min, self.corridor_len_max)
            carved_length = self._carve_segment(grid, current_x, current_y, direction, length)

            if carved_length > 0:
                dx, dy = direction.value
                current_x += dx * carved_length
                current_y += dy * carved_length

    def _would_create_parallel_corridor(self, grid, x, y, direction):
        """
        Check if carving would create problematic parallel corridors.
        Only prevents cases that would create a thin (1-cell wide) wall between parallel corridors.
        """
        dx, dy = direction.value

        # Get perpendicular directions
        if dx != 0:  # Horizontal movement, check vertical
            perp_dirs = [(0, -1), (0, 1)]
        else:  # Vertical movement, check horizontal
            perp_dirs = [(-1, 0), (1, 0)]

        # Check both perpendicular sides
        for px, py in perp_dirs:
            # Check if we're creating a situation where there are parallel corridors
            # with only a 1-cell wall between them, AND that wall would be isolated

            # Position perpendicular to us
            perp_x, perp_y = x + px, y + py

            # If there's a corridor perpendicular to our carving direction
            if self._is_valid(perp_x, perp_y) and grid[perp_y][perp_x] == INTERNAL_CORRIDOR:
                # Check cells before and after in our carving direction
                prev_x, prev_y = x - dx, y - dy
                next_x, next_y = x + dx, y + dy

                # Previous cell perpendicular
                prev_perp_x, prev_perp_y = prev_x + px, prev_y + py

                # Only block if:
                # 1. Previous cell in carving direction is a corridor
                # 2. Previous cell's perpendicular neighbor is also a corridor
                # 3. The wall between them (at perp_x, perp_y - dx/dy) would be thin
                if (self._is_valid(prev_x, prev_y) and
                    grid[prev_y][prev_x] == INTERNAL_CORRIDOR and
                    self._is_valid(prev_perp_x, prev_perp_y) and
                    grid[prev_perp_y][prev_perp_x] == INTERNAL_CORRIDOR):

                    # Check if the wall between the parallel corridors would be isolated
                    # (surrounded on ends)
                    wall_x, wall_y = perp_x + dx, perp_y + dy
                    if (self._is_valid(wall_x, wall_y) and
                        grid[wall_y][wall_x] == INTERNAL_CORRIDOR):
                        # This would create a very thin wall segment, block it
                        return True

        return False

    def _would_create_wall_island(self, grid, x, y):
        """
        Check if carving this cell would create a completely isolated wall cell.
        A wall is an island if it's a single cell surrounded by corridors on all 4 sides
        AND has no diagonal wall neighbors.
        """
        # Check all orthogonally adjacent wall cells
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            wx, wy = x + dx, y + dy

            # Skip if not valid or not a wall
            if not self._is_valid(wx, wy) or grid[wy][wx] != INTERNAL_WALL:
                continue

            # Count corridor neighbors of this wall
            corridor_neighbors = 0
            # Count wall neighbors of this wall (orthogonal and diagonal)
            wall_neighbors = 0

            # Check orthogonal neighbors
            for ddx, ddy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = wx + ddx, wy + ddy
                if not self._is_valid(nx, ny):
                    continue

                if grid[ny][nx] == INTERNAL_CORRIDOR or (nx == x and ny == y):
                    corridor_neighbors += 1
                elif grid[ny][nx] == INTERNAL_WALL:
                    wall_neighbors += 1

            # Check diagonal neighbors for wall connections
            for ddx, ddy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                nx, ny = wx + ddx, wy + ddy
                if self._is_valid(nx, ny) and grid[ny][nx] == INTERNAL_WALL:
                    wall_neighbors += 1

            # Wall would be an island if surrounded by corridors AND has no wall neighbors
            if corridor_neighbors >= 4 and wall_neighbors == 0:
                return True

        return False

    def _has_2x2_corridor_block(self, grid, x, y):
        """
        Check if carving here would create a problematic 2x2 block of corridors.
        Allows 2x2 blocks that are part of larger (3x3+) areas (chambers),
        but prevents narrow double-wide corridors.
        """
        # Check all 4 possible 2x2 blocks where (x,y) is a corner
        blocks_to_check = [
            # (x,y) is top-left: check right, down, diagonal
            [(1, 0), (0, 1), (1, 1)],
            # (x,y) is top-right: check left, down, diagonal
            [(-1, 0), (0, 1), (-1, 1)],
            # (x,y) is bottom-left: check right, up, diagonal
            [(1, 0), (0, -1), (1, -1)],
            # (x,y) is bottom-right: check left, up, diagonal
            [(-1, 0), (0, -1), (-1, -1)]
        ]

        for pattern in blocks_to_check:
            # Check if this forms a 2x2 block
            forms_2x2 = True
            for dx, dy in pattern:
                nx, ny = x + dx, y + dy
                if not self._is_valid(nx, ny) or grid[ny][nx] != INTERNAL_CORRIDOR:
                    forms_2x2 = False
                    break

            if not forms_2x2:
                continue

            # We have a 2x2 block. Check if it's part of a larger area (chamber)
            # by seeing if it can expand to 3x3
            # For simplicity, just check if there are corridors beyond the 2x2 in multiple directions
            expansion_count = 0

            # Get the 2x2 bounding box
            min_x = min(x, x + pattern[0][0], x + pattern[1][0], x + pattern[2][0])
            max_x = max(x, x + pattern[0][0], x + pattern[1][0], x + pattern[2][0])
            min_y = min(y, y + pattern[0][1], y + pattern[1][1], y + pattern[2][1])
            max_y = max(y, y + pattern[0][1], y + pattern[1][1], y + pattern[2][1])

            # Check if corridors extend beyond the 2x2 block
            check_points = [
                (min_x - 1, min_y), (min_x - 1, max_y),  # Left
                (max_x + 1, min_y), (max_x + 1, max_y),  # Right
                (min_x, min_y - 1), (max_x, min_y - 1),  # Top
                (min_x, max_y + 1), (max_x, max_y + 1),  # Bottom
            ]

            for cx, cy in check_points:
                if self._is_valid(cx, cy) and grid[cy][cx] == INTERNAL_CORRIDOR:
                    expansion_count += 1

            # If the 2x2 can expand in multiple directions, it's likely part of a chamber
            # Allow it. Otherwise, it's a narrow double-width corridor - block it.
            if expansion_count < 4:  # Less than 4 expansions means it's narrow
                return True

        return False

    def _carve_segment(self, grid, start_x, start_y, direction, length):
        """Carve a corridor segment in given direction on left half only."""
        dx, dy = direction.value
        carved = 0
        x, y = start_x, start_y
        middle = self.grid_size // 2

        for step in range(length):
            x += dx
            y += dy

            if not self._is_valid(x, y):
                break

            if x > middle:
                break

            if grid[y][x] == INTERNAL_CORRIDOR:
                break

            # Don't carve if it would create a 2x2 block of corridors
            if self._has_2x2_corridor_block(grid, x, y):
                break

            # Don't carve if it would create completely isolated wall cells
            if self._would_create_wall_island(grid, x, y):
                break

            if grid[y][x] == INTERNAL_WALL:
                grid[y][x] = INTERNAL_CORRIDOR
                carved += 1
            else:
                break

        return carved

    def _get_projected_fill(self, grid):
        """Calculate projected fill percentage after mirroring left half to right."""
        middle = self.grid_size // 2
        filled_left = 0
        filled_middle = 0

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if grid[y][x] == INTERNAL_CORRIDOR:
                    if x < middle:
                        filled_left += 1
                    elif x == middle:
                        filled_middle += 1

        projected_filled = (filled_left * 2) + filled_middle
        total = self.grid_size * self.grid_size
        return projected_filled / total

    def _convert_grid(self, internal_grid):
        """Convert internal representation to public representation."""
        self.grid = [[WALL if cell == INTERNAL_WALL else PATH for cell in row] for row in internal_grid]

    def _find_start_end(self):
        """Set start/end positions in opposite corners."""
        for y in range(min(3, self.grid_size)):
            for x in range(min(3, self.grid_size)):
                if self.grid[y][x] == PATH:
                    self.start_pos = (x, y)
                    break
            if self.start_pos:
                break

        for y in range(max(0, self.grid_size - 3), self.grid_size):
            for x in range(max(0, self.grid_size - 3), self.grid_size):
                if self.grid[y][x] == PATH:
                    self.end_pos = (x, y)
                    break
            if self.end_pos:
                break

        if not self.start_pos:
            self.start_pos = (1, 1)
        if not self.end_pos:
            self.end_pos = (self.grid_size - 2, self.grid_size - 2)

    def _is_connected(self):
        """Check if start and end are connected via BFS."""
        if not self.start_pos or not self.end_pos:
            return False

        queue = deque([self.start_pos])
        visited = {self.start_pos}

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.end_pos:
                return True

            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                if (self._is_valid(nx, ny) and
                    (nx, ny) not in visited and
                    self.grid[ny][nx] == PATH):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return False

    def _is_valid(self, x, y):
        """Check if coordinates are within bounds."""
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def get_start_position(self):
        """
        Get start position in tile coordinates.

        Returns:
            tuple: (x, y) in tile coordinates
        """
        return self.start_pos

    def get_end_position(self):
        """
        Get end position in tile coordinates.

        Returns:
            tuple: (x, y) in tile coordinates
        """
        return self.end_pos

    def is_wall(self, x, y):
        """
        Check if a grid cell is a wall.

        Args:
            x: Grid X coordinate
            y: Grid Y coordinate

        Returns:
            bool: True if cell is a wall or out of bounds
        """
        if not self._is_valid(x, y):
            return True
        return self.grid[y][x] == WALL

    def can_move_to(self, from_x, from_y, to_x, to_y):
        """
        Check if movement from one tile to another is valid.

        Args:
            from_x: Starting tile X (grid coordinates)
            from_y: Starting tile Y (grid coordinates)
            to_x: Target tile X (grid coordinates)
            to_y: Target tile Y (grid coordinates)

        Returns:
            bool: True if movement is valid (target is not a wall)
        """
        return not self.is_wall(to_x, to_y)

    def render(self, surface, colors):
        """
        Render the maze to a surface.

        Args:
            surface: Pygame surface to draw on
            colors: Dictionary with keys 'floor', 'wall', 'start', 'end'
        """
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )

                if self.grid[y][x] == WALL:
                    pygame.draw.rect(surface, colors['wall'], rect)
                elif (x, y) == self.start_pos:
                    pygame.draw.rect(surface, colors['start'], rect)
                elif (x, y) == self.end_pos:
                    pygame.draw.rect(surface, colors['end'], rect)
                else:
                    pygame.draw.rect(surface, colors['floor'], rect)
