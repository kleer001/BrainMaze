"""
Maze generation system using recursive backtracker algorithm.
Phase A2: Procedural maze generation with guaranteed solvable paths.
"""

import random
import pygame


class Cell:
    """Represents a single cell in the maze grid."""

    def __init__(self, x, y):
        """
        Initialize a cell.

        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
        """
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def __repr__(self):
        return f"Cell({self.x}, {self.y})"


class Maze:
    """
    Maze generator using recursive backtracker algorithm.
    Creates a perfect maze (single path between any two points).
    """

    def __init__(self, grid_size, tile_size):
        """
        Initialize maze generator.

        Args:
            grid_size: Size of the grid (e.g., 20 for 20x20)
            tile_size: Size of each tile in pixels
        """
        self.grid_size = grid_size
        self.tile_size = tile_size
        self.grid = []
        self.start_pos = None
        self.end_pos = None

        # Generate the maze
        self._generate()

    def _generate(self):
        """Generate maze using recursive backtracker algorithm."""
        # Create grid of cells
        self.grid = []
        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                row.append(Cell(x, y))
            self.grid.append(row)

        # Start from random cell
        start_x = random.randint(0, self.grid_size - 1)
        start_y = random.randint(0, self.grid_size - 1)

        # Run recursive backtracker
        self._carve_passages(start_x, start_y)

        # Find start and end positions (furthest apart corners)
        self._find_start_end_positions()

    def _carve_passages(self, x, y):
        """
        Recursive backtracker algorithm to carve passages.

        Args:
            x: Current X coordinate
            y: Current Y coordinate
        """
        current = self.grid[y][x]
        current.visited = True

        # Get neighbors in random order
        directions = ['top', 'right', 'bottom', 'left']
        random.shuffle(directions)

        for direction in directions:
            nx, ny = self._get_neighbor_coords(x, y, direction)

            # Check if neighbor is valid and unvisited
            if self._is_valid_cell(nx, ny) and not self.grid[ny][nx].visited:
                # Remove walls between current and neighbor
                neighbor = self.grid[ny][nx]
                current.walls[direction] = False
                neighbor.walls[self._opposite_direction(direction)] = False

                # Recursively visit neighbor
                self._carve_passages(nx, ny)

    def _get_neighbor_coords(self, x, y, direction):
        """
        Get coordinates of neighbor in given direction.

        Args:
            x: Current X coordinate
            y: Current Y coordinate
            direction: 'top', 'right', 'bottom', or 'left'

        Returns:
            tuple: (neighbor_x, neighbor_y)
        """
        if direction == 'top':
            return (x, y - 1)
        elif direction == 'right':
            return (x + 1, y)
        elif direction == 'bottom':
            return (x, y + 1)
        elif direction == 'left':
            return (x - 1, y)

    def _opposite_direction(self, direction):
        """
        Get opposite direction.

        Args:
            direction: 'top', 'right', 'bottom', or 'left'

        Returns:
            str: Opposite direction
        """
        opposites = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }
        return opposites[direction]

    def _is_valid_cell(self, x, y):
        """
        Check if coordinates are within grid bounds.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            bool: True if valid
        """
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def _find_start_end_positions(self):
        """
        Find start and end positions that are far apart.
        Uses corners to maximize distance.
        """
        # Define corners
        corners = [
            (0, 0),  # Top-left
            (self.grid_size - 1, 0),  # Top-right
            (0, self.grid_size - 1),  # Bottom-left
            (self.grid_size - 1, self.grid_size - 1)  # Bottom-right
        ]

        # Pick two random corners
        random.shuffle(corners)
        self.start_pos = corners[0]
        self.end_pos = corners[1]

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

    def is_wall(self, x, y, direction):
        """
        Check if there's a wall in a direction from a cell.

        Args:
            x: Cell X coordinate
            y: Cell Y coordinate
            direction: 'top', 'right', 'bottom', or 'left'

        Returns:
            bool: True if wall exists
        """
        if not self._is_valid_cell(x, y):
            return True
        return self.grid[y][x].walls[direction]

    def can_move_to(self, from_x, from_y, to_x, to_y):
        """
        Check if movement from one tile to another is valid (no wall between).

        Args:
            from_x: Starting tile X
            from_y: Starting tile Y
            to_x: Target tile X
            to_y: Target tile Y

        Returns:
            bool: True if movement is valid
        """
        # Check if target is valid
        if not self._is_valid_cell(to_x, to_y):
            return False

        # Determine direction of movement
        if to_x == from_x and to_y == from_y - 1:  # Moving up
            return not self.is_wall(from_x, from_y, 'top')
        elif to_x == from_x and to_y == from_y + 1:  # Moving down
            return not self.is_wall(from_x, from_y, 'bottom')
        elif to_x == from_x - 1 and to_y == from_y:  # Moving left
            return not self.is_wall(from_x, from_y, 'left')
        elif to_x == from_x + 1 and to_y == from_y:  # Moving right
            return not self.is_wall(from_x, from_y, 'right')

        # Invalid movement (diagonal or further than one tile)
        return False

    def render(self, surface, colors):
        """
        Render the maze to a surface.

        Args:
            surface: Pygame surface to draw on
            colors: Dictionary with keys 'floor', 'wall', 'start', 'end'
        """
        # Draw floor tiles for all cells
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )

                # Color start and end tiles differently
                if (x, y) == self.start_pos:
                    pygame.draw.rect(surface, colors['start'], rect)
                elif (x, y) == self.end_pos:
                    pygame.draw.rect(surface, colors['end'], rect)
                else:
                    pygame.draw.rect(surface, colors['floor'], rect)

        # Draw walls
        wall_thickness = 3
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell = self.grid[y][x]

                # Top wall
                if cell.walls['top']:
                    start_pos = (x * self.tile_size, y * self.tile_size)
                    end_pos = ((x + 1) * self.tile_size, y * self.tile_size)
                    pygame.draw.line(surface, colors['wall'], start_pos, end_pos, wall_thickness)

                # Right wall
                if cell.walls['right']:
                    start_pos = ((x + 1) * self.tile_size, y * self.tile_size)
                    end_pos = ((x + 1) * self.tile_size, (y + 1) * self.tile_size)
                    pygame.draw.line(surface, colors['wall'], start_pos, end_pos, wall_thickness)

                # Bottom wall
                if cell.walls['bottom']:
                    start_pos = (x * self.tile_size, (y + 1) * self.tile_size)
                    end_pos = ((x + 1) * self.tile_size, (y + 1) * self.tile_size)
                    pygame.draw.line(surface, colors['wall'], start_pos, end_pos, wall_thickness)

                # Left wall
                if cell.walls['left']:
                    start_pos = (x * self.tile_size, y * self.tile_size)
                    end_pos = (x * self.tile_size, (y + 1) * self.tile_size)
                    pygame.draw.line(surface, colors['wall'], start_pos, end_pos, wall_thickness)
