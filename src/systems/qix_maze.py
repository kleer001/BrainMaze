"""
Qix-style maze generation algorithm.
Carves corridors from frontier, building outward with guaranteed connectivity.
Portable to game engine.
"""

import random
from collections import deque
from enum import Enum

# Cell types
WALL = 0
CORRIDOR = 1
CHAMBER = 2


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

    def turn_left(self):
        """Rotate 90° counter-clockwise."""
        turns = {
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN,
            Direction.DOWN: Direction.RIGHT,
            Direction.RIGHT: Direction.UP,
        }
        return turns[self]


class QixMazeGenerator:
    """
    Qix-style procedural maze generator.
    Guarantees connectivity, single-width corridors, symmetry.
    """

    def __init__(self, width, height, config):
        """
        Initialize generator.

        Args:
            width: Grid width (must be odd)
            height: Grid height
            config: ConfigParser with generation settings
        """
        if width % 2 == 0:
            raise ValueError("Grid width must be odd for single-center corridor")

        self.width = width
        self.height = height
        self.config = config

        self.fill_target = config.getfloat('Generation', 'fill_target')
        self.chamber_min = config.getint('Generation', 'chamber_min_size')
        self.chamber_max = config.getint('Generation', 'chamber_max_size')
        self.corridor_len_min = config.getint('Generation', 'corridor_length_min')
        self.corridor_len_max = config.getint('Generation', 'corridor_length_max')
        self.max_attempts = config.getint('Generation', 'max_attempts')

        # Grid: 0=wall, 1=corridor, 2=chamber
        self.grid = [[WALL for _ in range(width)] for _ in range(height)]
        self.start_pos = None
        self.end_pos = None

    def generate(self):
        """Generate the maze. Returns True if successful."""
        for attempt in range(self.max_attempts):
            # Reset grid
            self.grid = [[WALL for _ in range(self.width)] for _ in range(self.height)]

            # Step 1: Carve left-half seed chamber (top-left)
            chamber_size = random.randint(self.chamber_min, self.chamber_max)
            self._carve_chamber(1, 1, chamber_size, chamber_size)

            # Step 2: Carve left-half seed chamber (bottom-left)
            self._carve_chamber(1, self.height - chamber_size - 1, chamber_size, chamber_size)

            # Step 3: Mirror chambers to right half (skip middle column for odd width)
            self._mirror_to_right()

            # Step 4: Carve corridors until fill target reached
            if self._carve_corridors():
                # Step 5: Set start/end positions
                self._find_start_end()

                # Step 6: Verify connectivity
                if self._is_connected():
                    return True

        return False

    def _carve_chamber(self, x, y, width, height):
        """
        Carve a rectangular chamber (all filled interior).

        Args:
            x, y: Top-left corner
            width, height: Chamber dimensions
        """
        for cy in range(y, min(y + height, self.height)):
            for cx in range(x, min(x + width, self.width)):
                self.grid[cy][cx] = CORRIDOR

    def _mirror_to_right(self):
        """
        Mirror left half to right half across vertical axis.
        Skip middle column for odd width.
        """
        middle = self.width // 2

        for y in range(self.height):
            for x in range(1, middle + 1):
                # Mirror x position (flip across middle)
                mirror_x = self.width - x

                # Copy left cell to mirrored right position
                self.grid[y][mirror_x] = self.grid[y][x]

    def _carve_corridors(self):
        """
        Carve corridors using Qix algorithm until fill target reached.

        Returns:
            bool: True if fill target reached
        """
        iterations = 0
        max_iterations = 10000  # Safety limit

        while self._get_fill_percentage() < self.fill_target and iterations < max_iterations:
            iterations += 1

            # Get random frontier cell (or any corridor cell)
            frontier_cells = self._get_frontier_cells()

            if not frontier_cells:
                break

            start_cell = random.choice(frontier_cells)
            self._carve_pattern_from(start_cell)

        return self._get_fill_percentage() >= self.fill_target

    def _get_frontier_cells(self):
        """
        Get all corridor cells adjacent to walls.
        These are carving endpoints.
        """
        frontier = []

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CORRIDOR:
                    # Check if adjacent to wall
                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if self._is_valid(nx, ny) and self.grid[ny][nx] == WALL:
                            frontier.append((x, y))
                            break

        return frontier

    def _carve_pattern_from(self, start_pos):
        """
        Carve an L-shaped pattern (4 segments) from start position.
        Algorithm steps 3-11.

        Args:
            start_pos: (x, y) tuple
        """
        x, y = start_pos

        # Pick random initial direction
        initial_dir = random.choice(list(Direction))

        # Attempt 4 segments in pattern: A, B, A, B
        # (but rotated 90° twice to make an L shape)
        segments = [
            ('A', initial_dir),
            ('B', initial_dir.turn_right()),
            ('A', initial_dir.turn_right().turn_right()),
            ('B', initial_dir.turn_right().turn_right().turn_right()),
        ]

        current_x, current_y = x, y

        for segment_type, direction in segments:
            # Decide length for this segment
            if segment_type == 'A':
                length = random.randint(self.corridor_len_min, self.corridor_len_max)
            else:  # 'B'
                length = random.randint(self.corridor_len_min, self.corridor_len_max)

            # Try to carve this segment
            carved_length = self._carve_segment(current_x, current_y, direction, length)

            if carved_length > 0:
                # Update position to end of carved segment
                dx, dy = direction.value
                current_x += dx * carved_length
                current_y += dy * carved_length

    def _carve_segment(self, start_x, start_y, direction, length):
        """
        Carve a corridor segment in given direction.
        Stop if: reach target length, hit existing corridor, or hit wall/no space.

        Args:
            start_x, start_y: Starting position
            direction: Direction enum
            length: Target length

        Returns:
            int: Actual length carved
        """
        dx, dy = direction.value
        carved = 0
        x, y = start_x, start_y

        for step in range(length):
            x += dx
            y += dy

            # Check bounds
            if not self._is_valid(x, y):
                break

            # If we hit existing corridor, we connected!
            if self.grid[y][x] == CORRIDOR:
                break

            # If we hit wall, carve it
            if self.grid[y][x] == WALL:
                self.grid[y][x] = CORRIDOR
                carved += 1
            else:
                # Hit something else, stop
                break

        return carved

    def _is_valid(self, x, y):
        """Check if coordinates are within bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _find_start_end(self):
        """
        Set start/end positions in opposite corners.
        """
        # Top-left corner area (start)
        for y in range(min(3, self.height)):
            for x in range(min(3, self.width)):
                if self.grid[y][x] == CORRIDOR:
                    self.start_pos = (x, y)
                    break
            if self.start_pos:
                break

        # Bottom-right corner area (end)
        for y in range(max(0, self.height - 3), self.height):
            for x in range(max(0, self.width - 3), self.width):
                if self.grid[y][x] == CORRIDOR:
                    self.end_pos = (x, y)
            if self.end_pos:
                break

        # Fallback
        if not self.start_pos:
            self.start_pos = (1, 1)
        if not self.end_pos:
            self.end_pos = (self.width - 2, self.height - 2)

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
                    self.grid[ny][nx] in [CORRIDOR, CHAMBER]):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return False

    def _get_fill_percentage(self):
        """Calculate percentage of grid that is corridor/chamber."""
        filled = sum(
            1 for row in self.grid for cell in row
            if cell in [CORRIDOR, CHAMBER]
        )
        total = self.width * self.height
        return filled / total

    def get_grid(self):
        """Return the grid."""
        return self.grid

    def get_start_pos(self):
        """Return start position."""
        return self.start_pos

    def get_end_pos(self):
        """Return end position."""
        return self.end_pos