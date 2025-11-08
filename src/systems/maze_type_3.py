import random
from systems.maze_generator import MazeGenerator

WALL = 1
PATH = 0


class MazeType3(MazeGenerator):
    """Hunt-and-Kill maze generator with mirroring."""

    def __init__(self, orientation='vertical'):
        self.orientation = orientation

    def generate(self, grid_size):
        # Initialize grid with all walls
        grid = [[WALL] * grid_size for _ in range(grid_size)]

        is_vertical = self.orientation == 'vertical'
        half_size = grid_size // 2 + 1

        # Create visited tracking grid for the generation area
        # Only track odd-coordinate cells (potential path cells)
        self.visited = [[False] * grid_size for _ in range(grid_size)]

        # Pick random starting cell (must be at odd coordinates)
        if is_vertical:
            current_x = random.randrange(1, half_size, 2)
            current_y = random.randrange(1, grid_size, 2)
        else:
            current_x = random.randrange(1, grid_size, 2)
            current_y = random.randrange(1, half_size, 2)

        # Mark starting cell as visited and carve it
        self.visited[current_y][current_x] = True
        grid[current_y][current_x] = PATH

        # Generate maze using Hunt-and-Kill algorithm
        self._hunt_and_kill(grid, current_x, current_y, grid_size, half_size, is_vertical)

        # Mirror the generated half
        self._mirror(grid, grid_size, half_size, is_vertical)

        return grid

    def _hunt_and_kill(self, grid, start_x, start_y, grid_size, half_size, is_vertical):
        """Generate maze using Hunt-and-Kill algorithm."""
        current_x, current_y = start_x, start_y

        while True:
            # Walk phase: random walk from current cell until stuck
            current_x, current_y = self._random_walk(
                grid, current_x, current_y, grid_size, half_size, is_vertical
            )

            # Hunt phase: scan for unvisited cell adjacent to visited cell
            found = self._hunt(grid, grid_size, half_size, is_vertical)

            if found is None:
                # No more unvisited cells, we're done
                break

            current_x, current_y = found

    def _random_walk(self, grid, x, y, grid_size, half_size, is_vertical):
        """Perform random walk from current cell until no unvisited neighbors."""
        current_x, current_y = x, y

        while True:
            # Get unvisited neighbors
            neighbors = self._get_unvisited_neighbors(
                current_x, current_y, grid_size, half_size, is_vertical
            )

            if not neighbors:
                # No unvisited neighbors, walk is complete
                return current_x, current_y

            # Pick random unvisited neighbor
            nx, ny = random.choice(neighbors)

            # Carve passage between current cell and neighbor
            wall_x = (current_x + nx) // 2
            wall_y = (current_y + ny) // 2
            grid[wall_y][wall_x] = PATH

            # Mark neighbor as visited and carve it
            self.visited[ny][nx] = True
            grid[ny][nx] = PATH

            # Move to neighbor
            current_x, current_y = nx, ny

    def _hunt(self, grid, grid_size, half_size, is_vertical):
        """Scan grid for unvisited cell adjacent to visited cell."""
        # Scan row by row, looking for unvisited cells
        for y in range(1, grid_size, 2):
            for x in range(1, grid_size, 2):
                # Check if in generation area
                if not self._is_in_generation_area(x, y, half_size, is_vertical):
                    continue

                # Check if cell is unvisited
                if self.visited[y][x]:
                    continue

                # Check if any neighbor is visited
                visited_neighbors = self._get_visited_neighbors(
                    x, y, grid_size, half_size, is_vertical
                )

                if visited_neighbors:
                    # Pick random visited neighbor to connect to
                    nx, ny = random.choice(visited_neighbors)

                    # Carve passage between this cell and visited neighbor
                    wall_x = (x + nx) // 2
                    wall_y = (y + ny) // 2
                    grid[wall_y][wall_x] = PATH

                    # Mark this cell as visited and carve it
                    self.visited[y][x] = True
                    grid[y][x] = PATH

                    # Return this cell as new starting point for walk
                    return x, y

        # No unvisited cells found
        return None

    def _get_unvisited_neighbors(self, x, y, grid_size, half_size, is_vertical):
        """Get list of unvisited neighbors at 2-cell distance."""
        neighbors = []
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # N, E, S, W

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if neighbor is valid and in generation area
            if not self._is_valid_neighbor(nx, ny, grid_size, half_size, is_vertical):
                continue

            # Check if unvisited
            if not self.visited[ny][nx]:
                neighbors.append((nx, ny))

        return neighbors

    def _get_visited_neighbors(self, x, y, grid_size, half_size, is_vertical):
        """Get list of visited neighbors at 2-cell distance."""
        neighbors = []
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # N, E, S, W

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if neighbor is valid and in generation area
            if not self._is_valid_neighbor(nx, ny, grid_size, half_size, is_vertical):
                continue

            # Check if visited
            if self.visited[ny][nx]:
                neighbors.append((nx, ny))

        return neighbors

    def _is_valid_neighbor(self, x, y, grid_size, half_size, is_vertical):
        """Check if coordinates are valid and in generation area."""
        # Must be within grid bounds
        if not (0 <= x < grid_size and 0 <= y < grid_size):
            return False

        # Must be at odd coordinates (potential cell positions)
        if x % 2 == 0 or y % 2 == 0:
            return False

        # Must be in the generation area (half of the grid)
        return self._is_in_generation_area(x, y, half_size, is_vertical)

    def _is_in_generation_area(self, x, y, half_size, is_vertical):
        """Check if cell is in the generation area."""
        if is_vertical:
            return x < half_size
        else:
            return y < half_size

    def _mirror(self, grid, grid_size, half_size, is_vertical):
        """Mirror the generated half to create symmetry."""
        for i in range(half_size):
            mirror_i = grid_size - 1 - i
            for j in range(grid_size):
                if is_vertical:
                    grid[j][mirror_i] = grid[j][i]
                else:
                    grid[mirror_i][j] = grid[i][j]
