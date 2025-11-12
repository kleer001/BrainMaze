import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType2(MazeGenerator):
    def __init__(self, north_bias=0.5, orientation='vertical'):
        self.north_bias = north_bias
        self.orientation = orientation

    def generate(self, grid_size):
        grid = [[WALL] * grid_size for _ in range(grid_size)]
        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1

        for y in range(0, grid_size, 2):
            for x in range(0, grid_size, 2):
                if is_vertical and x >= half_size:
                    continue
                if not is_vertical and y >= half_size:
                    continue

                grid[y][x] = PATH
                self._carve_passage(grid, x, y, grid_size, half_size, is_vertical)

        self._mirror(grid, grid_size, is_vertical)
        self._connect_mirror_line(grid, grid_size, is_vertical)
        return grid

    def _carve_passage(self, grid, x, y, grid_size, half_size, is_vertical):
        can_go_north = y >= 2
        can_go_west = x >= 2

        if is_vertical and x >= half_size:
            can_go_west = False
        if not is_vertical and y >= half_size:
            can_go_north = False

        if not can_go_north and not can_go_west:
            return

        if can_go_north and can_go_west:
            go_north = random.random() < self.north_bias
        else:
            go_north = can_go_north

        if go_north:
            grid[y - 1][x] = PATH
        else:
            grid[y][x - 1] = PATH

    def _connect_mirror_line(self, grid, grid_size, is_vertical):
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
