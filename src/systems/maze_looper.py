from collections import deque
from systems.maze_constants import PATH, WALL


class MazeLooper:
    def __init__(self, maze):
        self.maze = maze

    def remove_dead_ends(self):
        while True:
            dead_ends = self._find_dead_ends()
            if not dead_ends:
                break

            for dead_end in dead_ends:
                best_wall = self._find_longest_cycle_wall(dead_end)
                if best_wall:
                    wx = dead_end[0] + best_wall[0]
                    wy = dead_end[1] + best_wall[1]
                    self.maze.grid[wy][wx] = PATH

    def _find_dead_ends(self):
        dead_ends = []
        for y in range(self.maze.grid_size):
            for x in range(self.maze.grid_size):
                if not self.maze.is_wall(x, y):
                    open_count = sum(
                        1 for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]
                        if self._is_valid_grid_cell(x + dx, y + dy)
                        and not self.maze.is_wall(x + dx, y + dy)
                    )
                    if open_count == 1:
                        dead_ends.append((x, y))
        return dead_ends

    def _find_longest_cycle_wall(self, pos):
        x, y = pos
        best_direction = None
        max_distance = -1

        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            wall_x = x + dx
            wall_y = y + dy
            beyond_x = wall_x + dx
            beyond_y = wall_y + dy

            if (self._is_valid_grid_cell(wall_x, wall_y) and
                    self.maze.is_wall(wall_x, wall_y) and
                    self._is_valid_grid_cell(beyond_x, beyond_y) and
                    not self.maze.is_wall(beyond_x, beyond_y)):

                distance = self._path_distance(pos, (beyond_x, beyond_y))
                if distance > max_distance:
                    max_distance = distance
                    best_direction = (dx, dy)

        return best_direction

    def _path_distance(self, start, end):
        queue = deque([(start, 0)])
        visited = {start}

        while queue:
            (x, y), dist = queue.popleft()
            if (x, y) == end:
                return dist

            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx = x + dx
                ny = y + dy
                if (self._is_valid_grid_cell(nx, ny) and
                        not self.maze.is_wall(nx, ny) and
                        (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), dist + 1))

        return -1

    def _is_valid_grid_cell(self, x, y):
        return 0 <= x < self.maze.grid_size and 0 <= y < self.maze.grid_size


def loop_maze(maze):
    looper = MazeLooper(maze)
    looper.remove_dead_ends()
    return maze
