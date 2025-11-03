"""
A* pathfinding implementation for enemy navigation.
Phase A5: Used by Patrol and Seeker behaviors.
"""

import heapq
from typing import List, Tuple, Optional


class AStarPathfinder:
    """
    A* pathfinding algorithm for navigating the maze.
    """

    def __init__(self, maze):
        """
        Initialize pathfinder with maze reference.

        Args:
            maze: Maze instance with grid data
        """
        self.maze = maze
        self.grid_size = maze.grid_size

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find shortest path from start to goal using A* algorithm.

        Args:
            start: Starting position (tile_x, tile_y)
            goal: Goal position (tile_x, tile_y)

        Returns:
            List of (x, y) positions representing the path, or None if no path exists.
            Path includes both start and goal positions.
        """
        # Validate positions
        if not self._is_valid_position(start) or not self._is_valid_position(goal):
            return None

        # If start and goal are the same
        if start == goal:
            return [start]

        # Priority queue: (f_score, counter, position)
        # counter ensures stable sorting when f_scores are equal
        counter = 0
        open_set = [(0, counter, start)]
        counter += 1

        # Track visited nodes
        came_from = {}

        # g_score: cost from start to node
        g_score = {start: 0}

        # f_score: estimated total cost from start to goal through node
        f_score = {start: self._heuristic(start, goal)}

        # Set of positions in open_set (for faster lookup)
        open_set_positions = {start}

        while open_set:
            # Get node with lowest f_score
            current_f, _, current = heapq.heappop(open_set)
            open_set_positions.discard(current)

            # Check if we reached the goal
            if current == goal:
                return self._reconstruct_path(came_from, current)

            # Check all neighbors
            for neighbor in self._get_neighbors(current):
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + 1

                # If this path to neighbor is better than any previous one
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # Record the best path
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, goal)

                    # Add to open set if not already there
                    if neighbor not in open_set_positions:
                        heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                        counter += 1
                        open_set_positions.add(neighbor)

        # No path found
        return None

    def _heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate Manhattan distance heuristic.

        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)

        Returns:
            Manhattan distance between positions
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """
        Check if position is valid (within bounds and not a wall).

        Args:
            pos: Position (x, y) to check

        Returns:
            True if position is valid
        """
        x, y = pos

        # Check bounds
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False

        # Check if it's a wall
        return not self.maze.is_wall(x, y)

    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions (4-directional).

        Args:
            pos: Current position (x, y)

        Returns:
            List of valid neighboring positions
        """
        x, y = pos
        neighbors = []

        # Check all 4 directions
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # up, down, left, right
            neighbor = (x + dx, y + dy)
            if self._is_valid_position(neighbor):
                neighbors.append(neighbor)

        return neighbors

    def _reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Reconstruct path from came_from mapping.

        Args:
            came_from: Dictionary mapping positions to their predecessors
            current: Goal position

        Returns:
            List of positions from start to goal
        """
        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        # Reverse to get path from start to goal
        path.reverse()
        return path

    def get_next_step(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Get the next step towards goal from start position.

        Args:
            start: Starting position (tile_x, tile_y)
            goal: Goal position (tile_x, tile_y)

        Returns:
            Next position to move to, or None if no path exists
        """
        path = self.find_path(start, goal)

        if path is None or len(path) < 2:
            return None

        # Return second position in path (first is current position)
        return path[1]


def find_nearest_walkable_tile(maze, target_x: int, target_y: int, max_search_radius: int = 10) -> Optional[Tuple[int, int]]:
    """
    Find the nearest walkable tile to a target position.
    Uses BFS to search in expanding circles.

    Args:
        maze: Maze instance
        target_x: Target X coordinate
        target_y: Target Y coordinate
        max_search_radius: Maximum tiles to search from target

    Returns:
        Nearest walkable (x, y) position, or None if none found
    """
    # If target is already walkable, return it
    if not maze.is_wall(target_x, target_y):
        return (target_x, target_y)

    # BFS to find nearest walkable tile
    visited = set()
    queue = [(target_x, target_y, 0)]  # (x, y, distance)
    visited.add((target_x, target_y))

    while queue:
        x, y, dist = queue.pop(0)

        # Check if we've exceeded max search radius
        if dist > max_search_radius:
            break

        # Check all 4 neighbors
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy

            # Check bounds
            if nx < 0 or nx >= maze.grid_size or ny < 0 or ny >= maze.grid_size:
                continue

            # Skip if visited
            if (nx, ny) in visited:
                continue

            visited.add((nx, ny))

            # If walkable, return it
            if not maze.is_wall(nx, ny):
                return (nx, ny)

            # Add to queue for further searching
            queue.append((nx, ny, dist + 1))

    # No walkable tile found
    return None
