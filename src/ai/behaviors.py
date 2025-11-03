"""
AI behaviors for enemies.
Phase A3: Wanderer behavior only - random direction changes.
"""

import random


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
