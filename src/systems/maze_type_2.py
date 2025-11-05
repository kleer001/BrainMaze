import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType2(MazeGenerator):
    def __init__(self, north_bias=0.5):
        self.north_bias = north_bias

    def generate(self, grid_size):
        grid = [[WALL] * grid_size for _ in range(grid_size)]

        for y in range(0, grid_size, 2):
            for x in range(0, grid_size, 2):
                grid[y][x] = PATH
                self._carve_passage(grid, x, y, grid_size)

        return grid

    def _carve_passage(self, grid, x, y, grid_size):
        can_go_north = y >= 2
        can_go_west = x >= 2

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
