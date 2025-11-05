import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType1(MazeGenerator):
    def __init__(self, min_wall_length=1, max_wall_length=5, orientation='vertical'):
        self.min_wall_length = min_wall_length
        self.max_wall_length = max_wall_length
        self.orientation = orientation

    def generate(self, grid_size):
        grid = [[PATH] * grid_size for _ in range(grid_size)]
        self._scatter_walls(grid, grid_size)
        return grid

    def _scatter_walls(self, grid, grid_size):
        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1

        for line in range(1, half_size, 2):
            self._fill_line(grid, grid_size, line, is_vertical)

        self._mirror(grid, grid_size, half_size, is_vertical)

    def _fill_line(self, grid, grid_size, line, is_vertical):
        position = 0
        start_with_path = random.choice([True, False])

        while position < grid_size:
            if start_with_path:
                position = self._place_segment(grid, grid_size, line, position, PATH, 1, is_vertical)
                position = self._place_segment(grid, grid_size, line, position, WALL,
                                              self._random_wall_length(), is_vertical)
            else:
                position = self._place_segment(grid, grid_size, line, position, WALL,
                                              self._random_wall_length(), is_vertical)
                position = self._place_segment(grid, grid_size, line, position, PATH, 1, is_vertical)

    def _place_segment(self, grid, grid_size, line, start, cell_type, length, is_vertical):
        for i in range(length):
            if start + i >= grid_size:
                break
            x, y = (line, start + i) if is_vertical else (start + i, line)
            grid[y][x] = cell_type
        return start + length

    def _random_wall_length(self):
        return random.randint(self.min_wall_length, self.max_wall_length)

    def _mirror(self, grid, grid_size, half_size, is_vertical):
        for i in range(half_size):
            mirror_i = grid_size - 1 - i
            for j in range(grid_size):
                if is_vertical:
                    grid[j][mirror_i] = grid[j][i]
                else:
                    grid[mirror_i][j] = grid[i][j]
