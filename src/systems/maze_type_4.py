import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType4(MazeGenerator):
    """Sidewinder maze generator with mirroring."""

    def __init__(self, orientation='vertical'):
        self.orientation = orientation

    def generate(self, grid_size):
        grid = [[WALL] * grid_size for _ in range(grid_size)]
        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1

        # Initialize cells (every other cell is a potential path)
        self._initialize_cells(grid, grid_size, half_size, is_vertical)

        # Generate using sidewinder algorithm
        self._sidewinder(grid, grid_size, half_size, is_vertical)

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

    def _sidewinder(self, grid, grid_size, half_size, is_vertical):
        """Generate maze using sidewinder algorithm."""
        if is_vertical:
            self._sidewinder_vertical(grid, grid_size, half_size)
        else:
            self._sidewinder_horizontal(grid, grid_size, half_size)

    def _sidewinder_vertical(self, grid, grid_size, half_size):
        """Sidewinder working vertically (left to right columns)."""
        # First column - carve all south passages
        for y in range(0, grid_size - 2, 2):
            if y + 1 < grid_size:
                grid[y + 1][0] = PATH

        # Remaining columns in generation area
        for x in range(2, half_size, 2):
            run = []
            for y in range(0, grid_size, 2):
                run.append(y)

                # At bottom edge or randomly decide to close run
                at_bottom = (y >= grid_size - 2)
                close_run = at_bottom or random.choice([True, False])

                if close_run:
                    # Carve west from random cell in run
                    member = random.choice(run)
                    if x - 1 >= 0:
                        grid[member][x - 1] = PATH
                    run = []
                else:
                    # Carve south
                    if y + 1 < grid_size:
                        grid[y + 1][x] = PATH

    def _sidewinder_horizontal(self, grid, grid_size, half_size):
        """Sidewinder working horizontally (top to bottom rows)."""
        # First row - carve all east passages
        for x in range(0, grid_size - 2, 2):
            if x + 1 < grid_size:
                grid[0][x + 1] = PATH

        # Remaining rows in generation area
        for y in range(2, half_size, 2):
            run = []
            for x in range(0, grid_size, 2):
                run.append(x)

                # At east edge or randomly decide to close run
                at_east = (x >= grid_size - 2)
                close_run = at_east or random.choice([True, False])

                if close_run:
                    # Carve north from random cell in run
                    member = random.choice(run)
                    if y - 1 >= 0:
                        grid[y - 1][member] = PATH
                    run = []
                else:
                    # Carve east
                    if x + 1 < grid_size:
                        grid[y][x + 1] = PATH

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
