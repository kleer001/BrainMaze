import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType3(MazeGenerator):
    """Recursive backtracking maze generator."""

    def __init__(self, orientation='vertical'):
        # Orientation parameter kept for API compatibility but not used
        self.orientation = orientation

    def generate(self, grid_size):
        grid = [[WALL] * grid_size for _ in range(grid_size)]

        # Initialize all cells (every other cell is a potential path)
        for y in range(0, grid_size, 2):
            for x in range(0, grid_size, 2):
                grid[y][x] = PATH

        # Pick random starting cell
        start_x = random.randrange(0, grid_size, 2)
        start_y = random.randrange(0, grid_size, 2)

        # Generate maze using recursive backtracking across entire grid
        self._recursive_backtrack(grid, start_x, start_y, grid_size)

        return grid

    def _recursive_backtrack(self, grid, x, y, grid_size):
        """Carve passages using recursive backtracking across the full grid."""
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # N, E, S, W (2-cell steps)
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if neighbor is within bounds
            if not (0 <= nx < grid_size and 0 <= ny < grid_size):
                continue

            # Check if neighbor cell exists
            if grid[ny][nx] != PATH:
                continue

            # Check if neighbor is unvisited (all adjacent cells are walls)
            # Since we haven't carved the passage yet, if the neighbor has any
            # PATH adjacent cells, it has already been visited
            is_unvisited = True
            for ddx, ddy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                adj_x, adj_y = nx + ddx, ny + ddy
                if 0 <= adj_x < grid_size and 0 <= adj_y < grid_size:
                    if grid[adj_y][adj_x] == PATH:
                        is_unvisited = False
                        break

            if not is_unvisited:
                continue

            # Carve passage between current cell and neighbor
            wall_x, wall_y = x + dx // 2, y + dy // 2
            grid[wall_y][wall_x] = PATH

            # Recursively visit neighbor
            self._recursive_backtrack(grid, nx, ny, grid_size)
