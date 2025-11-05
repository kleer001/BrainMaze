from collections import deque

WALL = 1
PATH = 0


class MazeValidator:
    def __init__(self, grid, grid_size):
        self.grid = grid
        self.grid_size = grid_size

    def is_connected(self, start, end):
        if start == end:
            return True

        visited = {start}
        queue = deque([start])

        while queue:
            x, y = queue.popleft()

            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) == end:
                    return True
                if self._is_valid_path(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return False

    def is_fully_traversable(self, start_pos):
        if not start_pos:
            return False

        total_paths = sum(1 for row in self.grid for cell in row if cell == PATH)

        visited = {start_pos}
        queue = deque([start_pos])

        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if self._is_valid_path(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return len(visited) == total_paths

    def _is_valid_path(self, x, y):
        return (0 <= x < self.grid_size and
                0 <= y < self.grid_size and
                self.grid[y][x] != WALL)
