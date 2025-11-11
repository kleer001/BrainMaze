import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType3(MazeGenerator):
    def __init__(self, orientation='vertical'):
        self.orientation = orientation

    def generate(self, grid_size):
        grid = [[WALL] * grid_size for _ in range(grid_size)]
        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1
        self.visited = [[False] * grid_size for _ in range(grid_size)]

        if is_vertical:
            start_x = random.randrange(1, half_size, 2)
            start_y = random.randrange(1, grid_size, 2)
        else:
            start_x = random.randrange(1, grid_size, 2)
            start_y = random.randrange(1, half_size, 2)

        self._recursive_backtrack(grid, start_x, start_y, grid_size, half_size, is_vertical)
        self._mirror(grid, grid_size, is_vertical)
        self._connect_mirror_line(grid, grid_size, half_size, is_vertical)
        return grid

    def _recursive_backtrack(self, grid, x, y, grid_size, half_size, is_vertical):
        self.visited[y][x] = True
        grid[y][x] = PATH

        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if not self._is_valid_neighbor(nx, ny, grid_size, half_size, is_vertical):
                continue

            if self.visited[ny][nx]:
                continue

            wall_x, wall_y = x + dx // 2, y + dy // 2
            grid[wall_y][wall_x] = PATH
            self._recursive_backtrack(grid, nx, ny, grid_size, half_size, is_vertical)

    def _is_valid_neighbor(self, x, y, grid_size, half_size, is_vertical):
        if not (0 <= x < grid_size and 0 <= y < grid_size):
            return False

        if x % 2 == 0 or y % 2 == 0:
            return False

        if is_vertical:
            return x < half_size
        else:
            return y < half_size

    def _connect_mirror_line(self, grid, grid_size, half_size, is_vertical):
        mirror_line = grid_size // 2

        if is_vertical:
            for y in range(1, grid_size - 1, 2):
                left_x = mirror_line - 1
                right_x = mirror_line + 1

                if (0 <= left_x < grid_size and 0 <= right_x < grid_size and
                    grid[y][left_x] == PATH and grid[y][right_x] == PATH):
                    if random.random() < 0.5:
                        grid[y][mirror_line] = PATH
        else:
            for x in range(1, grid_size - 1, 2):
                top_y = mirror_line - 1
                bottom_y = mirror_line + 1

                if (0 <= top_y < grid_size and 0 <= bottom_y < grid_size and
                    grid[top_y][x] == PATH and grid[bottom_y][x] == PATH):
                    if random.random() < 0.5:
                        grid[mirror_line][x] = PATH
