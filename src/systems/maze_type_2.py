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

        # Generate one half
        for y in range(0, grid_size, 2):
            for x in range(0, grid_size, 2):
                if is_vertical and x >= half_size:
                    continue
                if not is_vertical and y >= half_size:
                    continue

                grid[y][x] = PATH
                self._carve_passage(grid, x, y, grid_size, half_size, is_vertical)

        # Mirror the generated half
        self._mirror(grid, grid_size, half_size, is_vertical)

        return grid

    def _carve_passage(self, grid, x, y, grid_size, half_size, is_vertical):
        can_go_north = y >= 2
        can_go_west = x >= 2

        # Respect generation boundaries
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

    def _mirror(self, grid, grid_size, half_size, is_vertical):
        """Mirror the generated half to create symmetry."""
        # Mirror only up to center (not including center column/row)
        # This prevents doubling the center axis
        mirror_count = grid_size // 2
        for i in range(mirror_count):
            mirror_i = grid_size - 1 - i
            for j in range(grid_size):
                if is_vertical:
                    grid[j][mirror_i] = grid[j][i]
                else:
                    grid[mirror_i][j] = grid[i][j]
