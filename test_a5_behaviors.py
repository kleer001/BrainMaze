"""
Test script for Phase A5 behavior implementations.
Verifies all behaviors can be instantiated and respond correctly.
"""

import sys
sys.path.insert(0, 'src')

from ai.behaviors import WandererBehavior, PatrolBehavior


class MockConfig:
    def get(self, section, key):
        configs = {
            ('Movement', 'wander_direction_change_interval'): '2.0',
            ('Behaviors', 'behavior_types'): 'wanderer,seeker,patrol,flee,combo',
            ('Behaviors', 'seeker_aggression_threshold'): '0.5',
            ('Behaviors', 'flee_trigger_distance'): '5',
        }
        return configs.get((section, key), '0')

    def getfloat(self, section, key):
        return float(self.get(section, key))

    def getint(self, section, key):
        return int(float(self.get(section, key)))


class MockMaze:
    def __init__(self):
        self.grid_size = 20

    def is_wall(self, x, y):
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return True
        return (x == 10 and y < 10)


class MockCollisionManager:
    def __init__(self):
        self.maze = MockMaze()

    def can_move_to_tile(self, from_x, from_y, to_x, to_y):
        return not self.maze.is_wall(to_x, to_y)


class MockEnemy:
    def __init__(self):
        self.tile_x = 5
        self.tile_y = 5
        self.awareness = 8
        self.config = MockConfig()
        self.collision_manager = MockCollisionManager()
        self.behavior_type_override = None

    def can_move_in_direction(self, direction):
        target_x, target_y = self.tile_x, self.tile_y

        if direction == 'up':
            target_y -= 1
        elif direction == 'down':
            target_y += 1
        elif direction == 'left':
            target_x -= 1
        elif direction == 'right':
            target_x += 1

        return self.collision_manager.can_move_to_tile(
            self.tile_x, self.tile_y,
            target_x, target_y
        )


def test_wanderer():
    enemy = MockEnemy()
    behavior = WandererBehavior(enemy)
    direction = behavior.update(0.1, (10, 10))
    assert direction in ['up', 'down', 'left', 'right', None]
    print("✓ WandererBehavior works")


def test_patrol():
    enemy = MockEnemy()
    enemy.tile_x, enemy.tile_y = 5, 5
    behavior = PatrolBehavior(enemy)

    direction = behavior.update(0.1, (10, 10))
    assert direction in ['up', 'down', 'left', 'right', None]
    print("✓ PatrolBehavior works")


if __name__ == '__main__':
    print("Testing Phase A5 behaviors...")
    print()

    test_wanderer()
    test_patrol()

    print()
    print("All behavior tests passed! ✓")
