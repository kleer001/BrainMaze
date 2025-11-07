import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType3(MazeGenerator):
    """Recursive backtracking maze generator with mirroring."""

    def __init__(self, orientation='vertical'):
        self.orientation = orientation

    def generate(self, grid_size):
        # Initialize grid with all walls
        grid = [[WALL] * grid_size for _ in range(grid_size)]

        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1

        # Create visited tracking grid for the generation area
        # Only track odd-coordinate cells (potential path cells)
        self.visited = [[False] * grid_size for _ in range(grid_size)]

        # Pick random starting cell (must be at odd coordinates)
        if is_vertical:
            start_x = random.randrange(1, half_size, 2)
            start_y = random.randrange(1, grid_size, 2)
        else:
            start_x = random.randrange(1, grid_size, 2)
            start_y = random.randrange(1, half_size, 2)

        # Generate maze using recursive backtracking
        self._recursive_backtrack(grid, start_x, start_y, grid_size, half_size, is_vertical)

        # Mirror the generated half
        self._mirror(grid, grid_size, half_size, is_vertical)

        # Connect across the mirror line to ensure maze is not split
        self._connect_mirror_line(grid, grid_size, half_size, is_vertical)

        return grid

    def _recursive_backtrack(self, grid, x, y, grid_size, half_size, is_vertical):
        """Carve passages using recursive backtracking."""
        # Mark current cell as visited and carve it out
        self.visited[y][x] = True
        grid[y][x] = PATH

        # Define directions: N, E, S, W (2-cell steps to move to next cell)
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if neighbor is within bounds and in generation area
            if not self._is_valid_neighbor(nx, ny, grid_size, half_size, is_vertical):
                continue

            # Check if neighbor has been visited
            if self.visited[ny][nx]:
                continue

            # Carve passage between current cell and neighbor
            wall_x, wall_y = x + dx // 2, y + dy // 2
            grid[wall_y][wall_x] = PATH

            # Recursively visit neighbor
            self._recursive_backtrack(grid, nx, ny, grid_size, half_size, is_vertical)

    def _is_valid_neighbor(self, x, y, grid_size, half_size, is_vertical):
        """Check if coordinates are valid and in generation area."""
        # Must be within grid bounds
        if not (0 <= x < grid_size and 0 <= y < grid_size):
            return False

        # Must be at odd coordinates (potential cell positions)
        if x % 2 == 0 or y % 2 == 0:
            return False

        # Must be in the generation area (half of the grid)
        if is_vertical:
            return x < half_size
        else:
            return y < half_size

    def _mirror(self, grid, grid_size, half_size, is_vertical):
        """Mirror the generated half to create symmetry."""
        for i in range(half_size):
            mirror_i = grid_size - 1 - i
            for j in range(grid_size):
                if is_vertical:
                    grid[j][mirror_i] = grid[j][i]
                else:
                    grid[mirror_i][j] = grid[i][j]

    def _connect_mirror_line(self, grid, grid_size, half_size, is_vertical):
        """Create passages across the mirror line to connect both halves."""
        mirror_line = grid_size // 2

        if is_vertical:
            # Mirror line is a vertical column
            # Look for cells on both sides and connect them
            for y in range(1, grid_size - 1, 2):  # Only check odd y coordinates (cell rows)
                left_x = mirror_line - 1
                right_x = mirror_line + 1

                # Check if both sides have path cells
                if (0 <= left_x < grid_size and 0 <= right_x < grid_size and
                    grid[y][left_x] == PATH and grid[y][right_x] == PATH):
                    # Randomly carve through the mirror line to connect (50% chance)
                    if random.random() < 0.5:
                        grid[y][mirror_line] = PATH
        else:
            # Mirror line is a horizontal row
            # Look for cells on both sides and connect them
            for x in range(1, grid_size - 1, 2):  # Only check odd x coordinates (cell columns)
                top_y = mirror_line - 1
                bottom_y = mirror_line + 1

                # Check if both sides have path cells
                if (0 <= top_y < grid_size and 0 <= bottom_y < grid_size and
                    grid[top_y][x] == PATH and grid[bottom_y][x] == PATH):
                    # Randomly carve through the mirror line to connect (50% chance)
                    if random.random() < 0.5:
                        grid[mirror_line][x] = PATH
