from abc import ABC, abstractmethod


class MazeGenerator(ABC):
    @abstractmethod
    def generate(self, grid_size):
        pass

    def _mirror(self, grid, grid_size, is_vertical):
        half_count = grid_size // 2
        for i in range(half_count):
            mirror_i = grid_size - 1 - i
            for j in range(grid_size):
                if is_vertical:
                    grid[j][mirror_i] = grid[j][i]
                else:
                    grid[mirror_i][j] = grid[i][j]
