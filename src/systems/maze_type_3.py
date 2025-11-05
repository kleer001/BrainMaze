import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType3(MazeGenerator):
    """Recursive backtracking maze generator with mirroring."""

    def __init__(self, orientation='vertical'):
        self.orientation = orientation

    def generate(self, grid_size):
        grid = [[WALL] * grid_size for _ in range(grid_size)]
        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1

        # Generate one half
        self._initialize_cells(grid, grid_size, half_size, is_vertical)

        # Pick random starting cell in the generation area
        if is_vertical:
            start_x = random.randrange(0, half_size, 2)
            start_y = random.randrange(0, grid_size, 2)
        else:
            start_x = random.randrange(0, grid_size, 2)
            start_y = random.randrange(0, half_size, 2)

        # Generate maze using recursive backtracking
        self._recursive_backtrack(grid, start_x, start_y, grid_size, half_size, is_vertical)

        # Mirror the generated half
        self._mirror(grid, grid_size, half_size, is_vertical)

        return grid

    def _initialize_cells(self, grid, grid_size, half_size, is_vertical):
        """Initialize cells (every other cell is a potential path)."""
        for y in range(0, grid_size, 2):
            for x in range(0, grid_size, 2):
                if is_vertical:
                    if x < half_size:
                        grid[y][x] = PATH
                else:
                    if y < half_size:
                        grid[y][x] = PATH

    def _recursive_backtrack(self, grid, x, y, grid_size, half_size, is_vertical):
        """Carve passages using recursive backtracking."""
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # N, E, S, W (2-cell steps)
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if neighbor is within bounds and in generation area
            if not self._is_valid_neighbor(nx, ny, grid_size, half_size, is_vertical):
                continue

            # Check if neighbor is unvisited (still isolated)
            if not self._is_unvisited(grid, nx, ny, grid_size):
                continue

            # Carve passage between current cell and neighbor
            wall_x, wall_y = x + dx // 2, y + dy // 2
            grid[wall_y][wall_x] = PATH

            # Recursively visit neighbor
            self._recursive_backtrack(grid, nx, ny, grid_size, half_size, is_vertical)

    def _is_valid_neighbor(self, x, y, grid_size, half_size, is_vertical):
        """Check if coordinates are valid and in generation area."""
        if not (0 <= x < grid_size and 0 <= y < grid_size):
            return False

        if is_vertical:
            return x < half_size
        else:
            return y < half_size

    def _is_unvisited(self, grid, x, y, grid_size):
        """Check if cell is unvisited (has walls on all sides)."""
        if grid[y][x] != PATH:
            return False

        # Check if all surrounding walls exist (cell is isolated)
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            wall_x, wall_y = x + dx, y + dy
            if 0 <= wall_x < grid_size and 0 <= wall_y < grid_size:
                if grid[wall_y][wall_x] == PATH:
                    return False  # Has at least one passage, so visited

        return True

    def _mirror(self, grid, grid_size, half_size, is_vertical):
        """Mirror the generated half to create symmetry."""
        for i in range(half_size):
            mirror_i = grid_size - 1 - i
            for j in range(grid_size):
                if is_vertical:
                    grid[j][mirror_i] = grid[j][i]
                else:
                    grid[mirror_i][j] = grid[i][j]
