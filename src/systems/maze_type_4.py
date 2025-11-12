import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType4(MazeGenerator):
    def __init__(self, orientation='vertical'):
        self.orientation = orientation

    def generate(self, grid_size):
        grid = [[WALL] * grid_size for _ in range(grid_size)]
        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1

        self._initialize_cells(grid, grid_size, half_size, is_vertical)
        self._sidewinder(grid, grid_size, half_size, is_vertical)
        self._mirror(grid, grid_size, is_vertical)
        self._connect_mirror_line(grid, grid_size, is_vertical)
        return grid

    def _initialize_cells(self, grid, grid_size, half_size, is_vertical):
        for y in range(0, grid_size, 2):
            for x in range(0, grid_size, 2):
                if is_vertical:
                    if x < half_size:
                        grid[y][x] = PATH
                else:
                    if y < half_size:
                        grid[y][x] = PATH

    def _sidewinder(self, grid, grid_size, half_size, is_vertical):
        if is_vertical:
            self._sidewinder_vertical(grid, grid_size, half_size)
        else:
            self._sidewinder_horizontal(grid, grid_size, half_size)

    def _sidewinder_vertical(self, grid, grid_size, half_size):
        for y in range(0, grid_size - 2, 2):
            if y + 1 < grid_size:
                grid[y + 1][0] = PATH

        for x in range(2, half_size, 2):
            run = []
            for y in range(0, grid_size, 2):
                run.append(y)
                at_bottom = (y >= grid_size - 2)
                close_run = at_bottom or random.choice([True, False])

                if close_run:
                    member = random.choice(run)
                    if x - 1 >= 0:
                        grid[member][x - 1] = PATH
                    run = []
                else:
                    if y + 1 < grid_size:
                        grid[y + 1][x] = PATH

    def _sidewinder_horizontal(self, grid, grid_size, half_size):
        for x in range(0, grid_size - 2, 2):
            if x + 1 < grid_size:
                grid[0][x + 1] = PATH

        for y in range(2, half_size, 2):
            run = []
            for x in range(0, grid_size, 2):
                run.append(x)
                at_east = (x >= grid_size - 2)
                close_run = at_east or random.choice([True, False])

                if close_run:
                    member = random.choice(run)
                    if y - 1 >= 0:
                        grid[y - 1][member] = PATH
                    run = []
                else:
                    if x + 1 < grid_size:
                        grid[y][x + 1] = PATH

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
