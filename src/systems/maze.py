"""
Maze generation system using recursive backtracker algorithm.
Phase A2: Procedural maze generation with guaranteed solvable paths.
Each wall occupies a full grid square.
"""

import random
import pygame

# Cell types
WALL = 1
PATH = 0


class Maze:
    """
    Maze generator using recursive backtracker algorithm.
    Creates a perfect maze where each wall occupies a full grid square.
    """

    def __init__(self, grid_size, tile_size):
        """
        Initialize maze generator.

        Args:
            grid_size: Total grid size from config (e.g., 20 for 20x20 grid)
                      This will be used to calculate path cells that fit with walls
            tile_size: Size of each tile in pixels
        """
        # Calculate how many path cells we can fit in the grid
        # Formula: path_size = (grid_size - 1) // 2
        # This ensures: actual_grid_size = 2 * path_size + 1 <= grid_size
        self.path_size = (grid_size - 1) // 2
        self.grid_size = 2 * self.path_size + 1  # Actual grid size with walls
        self.tile_size = tile_size
        self.grid = []
        self.start_pos = None
        self.end_pos = None
        self.visited = []  # For generation algorithm

        # Generate the maze
        self._generate()

    def _generate(self):
        """Generate maze using recursive backtracker algorithm."""
        # Initialize grid - all walls
        self.grid = [[WALL for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Initialize visited tracking for path cells only
        self.visited = [[False for _ in range(self.path_size)] for _ in range(self.path_size)]

        # Mark all path cells (at even coordinates) as PATH
        for py in range(self.path_size):
            for px in range(self.path_size):
                x = px * 2 + 1  # Convert to actual grid coordinates
                y = py * 2 + 1
                self.grid[y][x] = PATH

        # Start from random path cell
        start_px = random.randint(0, self.path_size - 1)
        start_py = random.randint(0, self.path_size - 1)

        # Run recursive backtracker to carve passages
        self._carve_passages(start_px, start_py)

        # Find start and end positions (furthest apart corners)
        self._find_start_end_positions()

    def _carve_passages(self, px, py):
        """
        Recursive backtracker algorithm to carve passages.

        Args:
            px: Current path cell X coordinate
            py: Current path cell Y coordinate
        """
        self.visited[py][px] = True

        # Get neighbors in random order
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left
        random.shuffle(directions)

        for dx, dy in directions:
            # Calculate neighbor path cell position
            npx = px + dx
            npy = py + dy

            # Check if neighbor is valid and unvisited
            if self._is_valid_path_cell(npx, npy) and not self.visited[npy][npx]:
                # Convert to actual grid coordinates
                x = px * 2 + 1
                y = py * 2 + 1
                nx = npx * 2 + 1
                ny = npy * 2 + 1

                # Carve passage (remove wall between cells)
                wall_x = (x + nx) // 2
                wall_y = (y + ny) // 2
                self.grid[wall_y][wall_x] = PATH

                # Recursively visit neighbor
                self._carve_passages(npx, npy)

    def _is_valid_path_cell(self, px, py):
        """
        Check if path cell coordinates are within bounds.

        Args:
            px: Path cell X coordinate
            py: Path cell Y coordinate

        Returns:
            bool: True if valid
        """
        return 0 <= px < self.path_size and 0 <= py < self.path_size

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
        Find start and end positions that are far apart.
        Uses corners of path cells to maximize distance.
        Returns positions in actual grid coordinates (odd indices).
        """
        # Define path cell corners (convert to actual grid coordinates)
        path_corners = [
            (0, 0),  # Top-left path cell
            (self.path_size - 1, 0),  # Top-right path cell
            (0, self.path_size - 1),  # Bottom-left path cell
            (self.path_size - 1, self.path_size - 1)  # Bottom-right path cell
        ]

        # Pick two random corners
        random.shuffle(path_corners)

        # Convert to actual grid coordinates
        start_px, start_py = path_corners[0]
        end_px, end_py = path_corners[1]

        self.start_pos = (start_px * 2 + 1, start_py * 2 + 1)
        self.end_pos = (end_px * 2 + 1, end_py * 2 + 1)

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
