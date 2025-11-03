"""
Maze generation system using random wall scattering (Pac-Man style).
Phase A4: Pac-Man style open field with scattered short wall segments.
Features vertical axis symmetry for aesthetic appeal.
Each wall occupies a full grid square.
"""

import random
import pygame
from collections import deque

# Cell types
WALL = 1
PATH = 0


class Maze:
    """
    Maze generator using random wall scattering (Pac-Man style).
    Creates an open field with short scattered wall segments.
    Features vertical axis symmetry for beautiful, balanced layouts.
    """

    def __init__(self, grid_size, tile_size, wall_density=0.2, max_wall_length=4, max_attempts=100):
        """
        Initialize maze generator.

        Args:
            grid_size: Total grid size (e.g., 20 for 20x20 grid)
            tile_size: Size of each tile in pixels
            wall_density: Target percentage of grid to be walls (0.0 to 1.0)
            max_wall_length: Maximum length of wall segments in tiles
            max_attempts: Maximum generation attempts before giving up
        """
        self.grid_size = grid_size
        self.tile_size = tile_size
        self.wall_density = wall_density
        self.max_wall_length = max_wall_length
        self.max_attempts = max_attempts
        self.grid = []
        self.start_pos = None
        self.end_pos = None

        # Generate the maze
        self._generate()

    def _generate(self):
        """Generate maze using random wall scattering (Pac-Man style) with vertical symmetry."""
        for attempt in range(self.max_attempts):
            # Initialize grid - all paths
            self.grid = [[PATH for _ in range(self.grid_size)] for _ in range(self.grid_size)]

            # Calculate target number of wall tiles (for one half, will be mirrored)
            total_tiles = self.grid_size * self.grid_size
            target_walls_total = int(total_tiles * self.wall_density)
            target_walls_half = target_walls_total // 2  # Only generate half, will mirror

            # Place random wall segments on LEFT HALF only
            walls_placed = 0
            max_segment_attempts = target_walls_half * 3  # Prevent infinite loop
            segment_attempts = 0
            half_width = self.grid_size // 2

            while walls_placed < target_walls_half and segment_attempts < max_segment_attempts:
                segment_attempts += 1

                # Random starting position (LEFT HALF only)
                x = random.randint(0, half_width - 1)
                y = random.randint(0, self.grid_size - 1)

                # Random orientation (horizontal or vertical)
                horizontal = random.choice([True, False])

                # Random segment length (1 to max_wall_length)
                length = random.randint(1, self.max_wall_length)

                # Try to place wall segment (only in left half)
                placed = self._place_wall_segment_with_mirror(x, y, length, horizontal)
                if placed > 0:
                    walls_placed += placed

            # Set start and end positions
            self._find_start_end_positions()

            # Check if path exists from start to end AND all areas are reachable (no pockets)
            if self._is_connected(self.start_pos, self.end_pos) and self._is_fully_traversable():
                # Success!
                return

        # If we failed all attempts, create empty maze (all paths)
        print(f"Warning: Failed to generate connected maze after {self.max_attempts} attempts. Using open field.")
        self.grid = [[PATH for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self._find_start_end_positions()

    def _place_wall_segment_with_mirror(self, x, y, length, horizontal):
        """
        Try to place a wall segment at the given position and mirror it to the right side.

        Args:
            x: Starting X coordinate (left half only)
            y: Starting Y coordinate
            length: Length of wall segment
            horizontal: True for horizontal wall, False for vertical

        Returns:
            int: Number of wall tiles placed (0 if failed)
        """
        half_width = self.grid_size // 2

        # Check if segment fits in left half
        if horizontal:
            if x + length > half_width:
                return 0
        else:
            if y + length > self.grid_size:
                return 0

        # Place the wall segment on LEFT side
        tiles_placed = 0
        for i in range(length):
            if horizontal:
                self.grid[y][x + i] = WALL
                tiles_placed += 1
            else:
                self.grid[y + i][x] = WALL
                tiles_placed += 1

        # Mirror to RIGHT side
        for i in range(length):
            if horizontal:
                # Mirror x-coordinate for horizontal walls
                mirror_x = self.grid_size - 1 - (x + i)
                self.grid[y][mirror_x] = WALL
            else:
                # Mirror x-coordinate for vertical walls
                mirror_x = self.grid_size - 1 - x
                self.grid[y + i][mirror_x] = WALL

        return tiles_placed

    def _is_connected(self, start_pos, end_pos):
        """
        Check if there's a path from start to end using BFS.

        Args:
            start_pos: (x, y) tuple of start position
            end_pos: (x, y) tuple of end position

        Returns:
            bool: True if path exists
        """
        if start_pos == end_pos:
            return True

        # BFS from start to end
        queue = deque([start_pos])
        visited = set([start_pos])

        while queue:
            x, y = queue.popleft()

            # Check all 4 neighbors
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                # Check if we reached the end
                if (nx, ny) == end_pos:
                    return True

                # Check if valid and unvisited path
                if (self._is_valid_grid_cell(nx, ny) and
                    not self.is_wall(nx, ny) and
                    (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return False

    def _is_fully_traversable(self):
        """
        Check if all path cells are reachable from start (no isolated pockets).

        Returns:
            bool: True if entire maze is traversable with no pockets
        """
        if not self.start_pos:
            return False

        # Count total path cells
        total_paths = 0
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if not self.is_wall(x, y):
                    total_paths += 1

        # BFS from start to count reachable cells
        queue = deque([self.start_pos])
        visited = set([self.start_pos])

        while queue:
            x, y = queue.popleft()

            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                if (self._is_valid_grid_cell(nx, ny) and
                    not self.is_wall(nx, ny) and
                    (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        # All path cells must be reachable
        return len(visited) == total_paths

    def _is_valid_grid_cell(self, x, y):
        """
        Check if grid coordinates are within bounds.

        Args:
            x: Grid X coordinate
            y: Grid Y coordinate

        Returns:
            bool: True if valid
        """
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def _find_start_end_positions(self):
        """
        Find start and end positions in opposite corners.
        Uses grid corners and ensures they're on path tiles.
        """
        # Define corner pairs (opposite corners)
        corner_pairs = [
            ((1, 1), (self.grid_size - 2, self.grid_size - 2)),  # Top-left & Bottom-right
            ((self.grid_size - 2, 1), (1, self.grid_size - 2))   # Top-right & Bottom-left
        ]

        # Pick a random corner pair
        start_corner, end_corner = random.choice(corner_pairs)

        # Find available path tile near start corner
        start_pos = None
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                x, y = start_corner[0] + dx, start_corner[1] + dy
                if self._is_valid_grid_cell(x, y) and not self.is_wall(x, y):
                    start_pos = (x, y)
                    break
            if start_pos:
                break

        # Find available path tile near end corner
        end_pos = None
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                x, y = end_corner[0] + dx, end_corner[1] + dy
                if self._is_valid_grid_cell(x, y) and not self.is_wall(x, y):
                    end_pos = (x, y)
                    break
            if end_pos:
                break

        # Set positions (with fallback)
        self.start_pos = start_pos if start_pos else (1, 1)
        self.end_pos = end_pos if end_pos else (self.grid_size - 2, self.grid_size - 2)

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
        if not self._is_valid_grid_cell(x, y):
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
        # Check if target is valid and not a wall
        return not self.is_wall(to_x, to_y)

    def render(self, surface, colors):
        """
        Render the maze to a surface.
        Each grid cell is drawn as either a wall (full square) or a path.

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

                # Determine color based on cell type and position
                if self.grid[y][x] == WALL:
                    pygame.draw.rect(surface, colors['wall'], rect)
                elif (x, y) == self.start_pos:
                    pygame.draw.rect(surface, colors['start'], rect)
                elif (x, y) == self.end_pos:
                    pygame.draw.rect(surface, colors['end'], rect)
                else:
                    pygame.draw.rect(surface, colors['floor'], rect)
