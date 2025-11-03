"""
Test Phase A5: Patrol Behavior
Tests greedy pathfinding and patrol behavior with quadrant waypoints.
"""

import sys
sys.path.insert(0, 'src')

import pygame
from systems.maze import Maze
from systems.collision import CollisionManager
from entities.enemy import Enemy
from ai.behaviors import PatrolBehavior
from ai.pathfinding import get_direction_towards_target, find_nearest_walkable_tile
import configparser

# Initialize pygame (needed for font rendering in Enemy)
pygame.init()


def test_greedy_pathfinding():
    """Test greedy pathfinding direction selection."""
    print("Testing greedy pathfinding...")

    # Create simple test cases
    def always_can_move(direction):
        """Mock function that always allows movement."""
        return True

    def block_right(direction):
        """Mock function that blocks right movement."""
        return direction != 'right'

    # Test 1: Moving right (dx > dy)
    direction = get_direction_towards_target(5, 5, 10, 6, always_can_move)
    assert direction == 'right', f"Expected 'right', got {direction}"
    print("  ✓ Greedy pathfinding prefers larger axis")

    # Test 2: Moving up (dy > dx)
    direction = get_direction_towards_target(5, 10, 6, 5, always_can_move)
    assert direction == 'up', f"Expected 'up', got {direction}"
    print("  ✓ Greedy pathfinding handles vertical movement")

    # Test 3: Blocked primary direction - tries secondary
    direction = get_direction_towards_target(5, 5, 10, 6, block_right)
    assert direction in ['down', 'up'], f"Expected fallback direction, got {direction}"
    print("  ✓ Greedy pathfinding falls back when blocked")

    # Test 4: Already at target
    direction = get_direction_towards_target(5, 5, 5, 5, always_can_move)
    assert direction is None, f"Expected None at target, got {direction}"
    print("  ✓ Greedy pathfinding returns None at target")

    print()


def test_find_nearest_walkable():
    """Test finding nearest walkable tile."""
    print("Testing find_nearest_walkable_tile...")

    # Create a test maze
    maze = Maze(
        grid_size=20,
        tile_size=40,
        wall_density=0.2,
        max_wall_length=4,
        max_attempts=100
    )

    # Test finding walkable tile near center
    center_x, center_y = 10, 10
    walkable = find_nearest_walkable_tile(maze, center_x, center_y, max_search_radius=10)

    assert walkable is not None, "Should find a walkable tile"
    wx, wy = walkable
    assert not maze.is_wall(wx, wy), "Found tile should not be a wall"
    print(f"  Found walkable tile at {walkable} near ({center_x}, {center_y})")
    print("  ✓ find_nearest_walkable_tile works")
    print()


def test_patrol_waypoints():
    """Test patrol waypoint calculation."""
    print("Testing patrol waypoint calculation...")

    # Create test maze and enemy
    maze = Maze(
        grid_size=20,
        tile_size=40,
        wall_density=0.2,
        max_wall_length=4,
        max_attempts=100
    )

    # Create config
    config = configparser.ConfigParser()
    config.add_section('Maze')
    config.set('Maze', 'tile_size', '40')
    config.add_section('Player')
    config.set('Player', 'corner_forgiveness', '6')
    config.add_section('Attributes')
    config.set('Attributes', 'speed_min', '1')
    config.set('Attributes', 'speed_max', '4')
    config.set('Attributes', 'awareness_min', '2')
    config.set('Attributes', 'awareness_max', '8')
    config.add_section('Movement')
    config.set('Movement', 'update_interval', '10')
    config.set('Movement', 'wander_direction_change_interval', '2.0')
    config.add_section('Colors')
    config.set('Colors', 'enemy', '255, 200, 100')

    collision_manager = CollisionManager(maze, config)

    # Create enemy
    start_x, start_y = maze.get_start_position()
    enemy = Enemy(start_x, start_y, config, collision_manager)

    # Create patrol behavior
    patrol = PatrolBehavior(enemy)

    # Check waypoints
    assert len(patrol.waypoints) == 4, f"Should have 4 waypoints, got {len(patrol.waypoints)}"
    print(f"  Waypoints calculated:")
    for i, (wx, wy) in enumerate(patrol.waypoints):
        print(f"    Waypoint {i}: ({wx}, {wy})")
        # Verify waypoints are not walls
        assert not maze.is_wall(wx, wy), f"Waypoint {i} at ({wx}, {wy}) should not be a wall"

    print("  ✓ All waypoints are valid (not walls)")
    print("  ✓ Patrol waypoints calculated correctly")
    print()


def test_patrol_cycling():
    """Test patrol waypoint cycling."""
    print("Testing patrol waypoint cycling...")

    # Create test maze and enemy
    maze = Maze(
        grid_size=20,
        tile_size=40,
        wall_density=0.2,
        max_wall_length=4,
        max_attempts=100
    )

    # Create config
    config = configparser.ConfigParser()
    config.add_section('Maze')
    config.set('Maze', 'tile_size', '40')
    config.add_section('Player')
    config.set('Player', 'corner_forgiveness', '6')
    config.add_section('Attributes')
    config.set('Attributes', 'speed_min', '1')
    config.set('Attributes', 'speed_max', '4')
    config.set('Attributes', 'awareness_min', '2')
    config.set('Attributes', 'awareness_max', '8')
    config.add_section('Movement')
    config.set('Movement', 'update_interval', '10')
    config.set('Movement', 'wander_direction_change_interval', '2.0')
    config.add_section('Colors')
    config.set('Colors', 'enemy', '255, 200, 100')

    collision_manager = CollisionManager(maze, config)

    # Create enemy
    start_x, start_y = maze.get_start_position()
    enemy = Enemy(start_x, start_y, config, collision_manager)

    # Create patrol behavior
    patrol = PatrolBehavior(enemy)

    # Initial waypoint
    initial_waypoint = patrol.current_waypoint_index
    print(f"  Initial waypoint index: {initial_waypoint}")

    # Manually move enemy to first waypoint
    wx, wy = patrol.waypoints[patrol.current_waypoint_index]
    enemy.tile_x, enemy.tile_y = wx, wy

    # Update behavior - should advance to next waypoint
    patrol.update(0.1, (0, 0))

    new_waypoint = patrol.current_waypoint_index
    print(f"  After reaching waypoint: {new_waypoint}")

    assert new_waypoint == (initial_waypoint + 1) % 4, "Should advance to next waypoint"
    print("  ✓ Patrol cycles to next waypoint when reached")
    print()


def visualize_patrol():
    """Visualize patrol behavior on ASCII maze."""
    print("Visualizing patrol behavior...")
    print()

    # Create test maze
    maze = Maze(
        grid_size=20,
        tile_size=40,
        wall_density=0.2,
        max_wall_length=4,
        max_attempts=100
    )

    # Create config
    config = configparser.ConfigParser()
    config.add_section('Maze')
    config.set('Maze', 'tile_size', '40')
    config.add_section('Player')
    config.set('Player', 'corner_forgiveness', '6')
    config.add_section('Attributes')
    config.set('Attributes', 'speed_min', '1')
    config.set('Attributes', 'speed_max', '4')
    config.set('Attributes', 'awareness_min', '2')
    config.set('Attributes', 'awareness_max', '8')
    config.add_section('Movement')
    config.set('Movement', 'update_interval', '10')
    config.set('Movement', 'wander_direction_change_interval', '2.0')
    config.add_section('Colors')
    config.set('Colors', 'enemy', '255, 200, 100')

    collision_manager = CollisionManager(maze, config)

    # Create enemy at start
    start_x, start_y = maze.get_start_position()
    enemy = Enemy(start_x, start_y, config, collision_manager)

    # Create patrol behavior
    patrol = PatrolBehavior(enemy)

    # Print maze with waypoints
    print("Maze with patrol waypoints:")
    for y in range(maze.grid_size):
        for x in range(maze.grid_size):
            if (x, y) == (enemy.tile_x, enemy.tile_y):
                print('E', end='')  # Enemy
            elif (x, y) in patrol.waypoints:
                # Show waypoint number
                idx = patrol.waypoints.index((x, y))
                print(str(idx), end='')
            elif (x, y) == maze.start_pos:
                print('S', end='')  # Start
            elif (x, y) == maze.end_pos:
                print('X', end='')  # End
            elif maze.is_wall(x, y):
                print('█', end='')  # Wall
            else:
                print('·', end='')  # Path
        print()
    print()
    print("Legend:")
    print("  E = Enemy current position")
    print("  0,1,2,3 = Patrol waypoints (quadrant centers)")
    print("  S = Start position")
    print("  X = End position")
    print("  █ = Wall")
    print("  · = Path")
    print()

    # Show waypoint details
    print("Waypoint details:")
    for i, (wx, wy) in enumerate(patrol.waypoints):
        print(f"  Waypoint {i}: ({wx:2d}, {wy:2d})")
    print()


if __name__ == '__main__':
    print("=" * 60)
    print("Phase A5 Test Suite: Patrol Behavior")
    print("=" * 60)
    print()

    test_greedy_pathfinding()
    test_find_nearest_walkable()
    test_patrol_waypoints()
    test_patrol_cycling()
    visualize_patrol()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
