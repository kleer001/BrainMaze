"""
AI behaviors for enemies.
Phase A3: Wanderer behavior only - random direction changes.
Phase A5: Multiple behaviors - Wanderer, Patrol, Seeker, Flee, Combo.
"""

import random
from ai.pathfinding import get_direction_towards_target, find_nearest_walkable_tile


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
        self.waypoint_threshold = 1

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

    def update(self, dt, player_pos):
        """
        Update patrol behavior - move towards current waypoint.

        Args:
            dt: Delta time in seconds
            player_pos: Tuple of (x, y) player tile position (unused for patrol)

        Returns:
            str: Direction to move ('up', 'down', 'left', 'right', or None)
        """
        # Get current waypoint target
        target_x, target_y = self.waypoints[self.current_waypoint_index]

        # Get enemy position
        enemy_x, enemy_y = self.enemy.tile_x, self.enemy.tile_y

        # Check if we've reached the waypoint
        distance = abs(enemy_x - target_x) + abs(enemy_y - target_y)  # Manhattan distance

        if distance <= self.waypoint_threshold:
            # Reached waypoint - advance to next one
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.waypoints)
            target_x, target_y = self.waypoints[self.current_waypoint_index]

        # Get direction towards current waypoint using greedy pathfinding
        direction = get_direction_towards_target(
            enemy_x, enemy_y,
            target_x, target_y,
            self.enemy.can_move_in_direction
        )

        return direction
