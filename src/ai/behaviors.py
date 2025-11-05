import random
from ai.pathfinding import find_path_bfs, find_nearest_walkable_tile
from utils.direction import ALL_DIRECTIONS

class Behavior:
    def __init__(self, enemy):
        self.enemy = enemy

    def update(self, dt, player_pos):
        raise NotImplementedError("Subclasses must implement update()")

class WandererBehavior(Behavior):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.current_direction = None
        self.direction_timer = 0.0
        self.change_interval = enemy.config.getfloat('Movement', 'wander_direction_change_interval')

    def update(self, dt, player_pos):
        self.direction_timer -= dt

        if self.direction_timer <= 0 or self.current_direction is None:
            self.current_direction = self._select_new_direction()
            self.direction_timer = self.change_interval

        return self.current_direction

    def _select_new_direction(self):
        valid_directions = [d for d in ALL_DIRECTIONS if self.enemy.can_move_in_direction(d)]
        return random.choice(valid_directions) if valid_directions else None

class PatrolBehavior(Behavior):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.maze = enemy.collision_manager.maze
        self.waypoints = self._calculate_quadrant_waypoints()
        self.current_waypoint_index = 0
        self.waypoint_threshold = 0
        self.cached_path = None
        self.path_index = 0

    def _calculate_quadrant_waypoints(self):
        grid_size = self.maze.grid_size
        half_size = grid_size // 2
        quarter_size = grid_size // 4

        quadrant_centers = [
            (quarter_size, quarter_size),
            (half_size + quarter_size, quarter_size),
            (quarter_size, half_size + quarter_size),
            (half_size + quarter_size, half_size + quarter_size),
        ]

        waypoints = []
        for center_x, center_y in quadrant_centers:
            walkable = find_nearest_walkable_tile(self.maze, center_x, center_y, max_search_radius=10)
            waypoints.append(walkable if walkable else (center_x, center_y))

        return waypoints

    def _is_walkable(self, x, y):
        if x < 0 or x >= self.maze.grid_size or y < 0 or y >= self.maze.grid_size:
            return False
        return not self.maze.is_wall(x, y)

    def update(self, dt, player_pos):
        enemy_x, enemy_y = self.enemy.tile_x, self.enemy.tile_y
        target_x, target_y = self.waypoints[self.current_waypoint_index]

        if enemy_x == target_x and enemy_y == target_y:
            self._advance_to_next_waypoint()
            target_x, target_y = self.waypoints[self.current_waypoint_index]

        if self.cached_path is None or self.path_index >= len(self.cached_path):
            self.cached_path = find_path_bfs(enemy_x, enemy_y, target_x, target_y, self._is_walkable)
            self.path_index = 0

            if self.cached_path is None:
                return None

        if self.path_index < len(self.cached_path):
            direction = self.cached_path[self.path_index]

            if self.enemy.can_move_in_direction(direction):
                self.path_index += 1
                return direction
            else:
                self.cached_path = None
                self.path_index = 0
                return None

        return None

    def _advance_to_next_waypoint(self):
        self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.waypoints)
        self.cached_path = None
        self.path_index = 0
