"""
AI behaviors for enemies.
Phase A3: Wanderer behavior only - random direction changes.
Phase A5: Multiple behaviors - Wanderer, Patrol, Seeker, Flee, Combo.
"""

import random
from ai.pathfinding import get_direction_towards_target, find_nearest_walkable_tile, find_path_bfs


class Behavior:
    """Base class for enemy behaviors."""

    def __init__(self, enemy):
        """
        Initialize behavior.

        Args:
            enemy: Enemy instance this behavior controls
        """
        self.enemy = enemy

    def update(self, dt, player_pos):
        """
        Update behavior state.

        Args:
            dt: Delta time in seconds
            player_pos: Tuple of (x, y) player tile position

        Returns:
            str: Direction to move ('up', 'down', 'left', 'right', or None)
        """
        raise NotImplementedError("Subclasses must implement update()")


class WandererBehavior(Behavior):
    """
    Wanderer behavior - randomly changes direction.
    Enemy roams the maze without regard for player position.
    """

    def __init__(self, enemy):
        """
        Initialize wanderer behavior.

        Args:
            enemy: Enemy instance this behavior controls
        """
        super().__init__(enemy)
        self.current_direction = None
        self.direction_timer = 0.0
        self.change_interval = enemy.config.getfloat('Movement', 'wander_direction_change_interval')

    def update(self, dt, player_pos):
        """
        Update wanderer behavior - randomly change direction.

        Args:
            dt: Delta time in seconds
            player_pos: Tuple of (x, y) player tile position (unused for wanderer)

        Returns:
            str: Direction to move ('up', 'down', 'left', 'right', or None)
        """
        # Update timer
        self.direction_timer -= dt

        # Time to change direction?
        if self.direction_timer <= 0 or self.current_direction is None:
            # Pick a new random direction
            directions = ['up', 'down', 'left', 'right']

            # Try to pick a valid direction (not blocked by wall)
            valid_directions = []
            for direction in directions:
                if self.enemy.can_move_in_direction(direction):
                    valid_directions.append(direction)

            if valid_directions:
                # Pick a random valid direction
                self.current_direction = random.choice(valid_directions)
            else:
                # No valid directions, stay put
                self.current_direction = None

            # Reset timer
            self.direction_timer = self.change_interval

        return self.current_direction


class PatrolBehavior(Behavior):
    """
    Patrol behavior - cycles through 4 waypoints at quadrant centers.
    Enemy patrols between waypoints in the four quadrants of the maze.
    """

    def __init__(self, enemy):
        """
        Initialize patrol behavior and calculate waypoints.

        Args:
            enemy: Enemy instance this behavior controls
        """
        super().__init__(enemy)

        # Get maze reference from enemy's collision manager
        self.maze = enemy.collision_manager.maze

        # Calculate waypoints (centers of 4 quadrants)
        self.waypoints = self._calculate_quadrant_waypoints()

        # Current waypoint index
        self.current_waypoint_index = 0

        # Threshold for "reached waypoint" (in tiles)
        # Set to 0 to require exact position match and prevent oscillation
        self.waypoint_threshold = 0

        # BFS path cache - stores list of directions to follow
        self.cached_path = None
        self.path_index = 0

    def _calculate_quadrant_waypoints(self):
        """
        Calculate waypoints at the centers of the 4 quadrants.

        Returns:
            List of 4 (x, y) waypoint positions
        """
        grid_size = self.maze.grid_size

        # Calculate quadrant centers
        # Quadrant layout:
        #   0 | 1
        #   -----
        #   2 | 3

        half_size = grid_size // 2
        quarter_size = grid_size // 4

        # Calculate ideal center positions
        quadrant_centers = [
            (quarter_size, quarter_size),          # Top-left
            (half_size + quarter_size, quarter_size),  # Top-right
            (quarter_size, half_size + quarter_size),  # Bottom-left
            (half_size + quarter_size, half_size + quarter_size),  # Bottom-right
        ]

        # Find nearest walkable tile to each center
        waypoints = []
        for center_x, center_y in quadrant_centers:
            walkable = find_nearest_walkable_tile(self.maze, center_x, center_y, max_search_radius=10)

            if walkable:
                waypoints.append(walkable)
            else:
                # Fallback to center if no walkable tile found (shouldn't happen)
                waypoints.append((center_x, center_y))

        return waypoints

    def _is_walkable(self, x, y):
        """
        Check if a tile position is walkable (not a wall and in bounds).

        Args:
            x: Tile X position
            y: Tile Y position

        Returns:
            bool: True if walkable, False otherwise
        """
        # Check bounds
        if x < 0 or x >= self.maze.grid_size or y < 0 or y >= self.maze.grid_size:
            return False

        # Check if it's not a wall
        return not self.maze.is_wall(x, y)

    def update(self, dt, player_pos):
        """
        Update patrol behavior - move towards current waypoint using BFS pathfinding.

        Args:
            dt: Delta time in seconds
            player_pos: Tuple of (x, y) player tile position (unused for patrol)

        Returns:
            str: Direction to move ('up', 'down', 'left', 'right', or None)
        """
        # Get current enemy position
        enemy_x, enemy_y = self.enemy.tile_x, self.enemy.tile_y

        # Get current waypoint target
        target_x, target_y = self.waypoints[self.current_waypoint_index]

        # Check if we've reached the waypoint
        if enemy_x == target_x and enemy_y == target_y:
            # Reached waypoint - advance to next one and clear path cache
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.waypoints)
            target_x, target_y = self.waypoints[self.current_waypoint_index]
            self.cached_path = None
            self.path_index = 0

        # Check if we need to calculate a new path
        if self.cached_path is None or self.path_index >= len(self.cached_path):
            # Calculate new path using BFS
            self.cached_path = find_path_bfs(
                enemy_x, enemy_y,
                target_x, target_y,
                self._is_walkable
            )
            self.path_index = 0

            # If no path found, stay still
            if self.cached_path is None:
                return None

        # Follow the cached path
        if self.path_index < len(self.cached_path):
            direction = self.cached_path[self.path_index]

            # Verify the next move is still valid before committing
            if self.enemy.can_move_in_direction(direction):
                self.path_index += 1
                return direction
            else:
                # Path is blocked - recalculate on next update
                self.cached_path = None
                self.path_index = 0
                return None

        return None
