"""
Test to verify that the wall sliding bug is fixed.
This test specifically checks that a player cannot slide between walls.
"""

import sys
import os
import configparser

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from systems.maze import Maze
from systems.collision import CollisionManager
from entities.player import Player


def test_wall_sliding_bug():
    """
    Test that player cannot slide through walls.
    This creates a scenario where the player tries to move into a wall
    while being slightly off-center.
    """
    print("Testing wall sliding bug fix...")

    # Load config
    config = configparser.ConfigParser()
    config.read('src/config/gameplay.ini')

    # Create a simple maze
    maze = Maze(20, 40)
    collision_manager = CollisionManager(maze, config)

    # Find a wall that has a path cell adjacent to it
    test_found = False
    for y in range(maze.grid_size):
        for x in range(maze.grid_size):
            if maze.is_wall(x, y):
                # Check if there's a path cell to the left
                if x > 0 and not maze.is_wall(x - 1, y):
                    # Create player at the path cell to the left of the wall
                    player = Player(x - 1, y, config, collision_manager)

                    # Move player slightly off-center vertically
                    # This simulates the condition that would trigger corner forgiveness
                    player.pos.y += 3  # 3 pixels off center

                    # Try to move right into the wall
                    can_move = player._can_move_in_direction('right')

                    # After the fix, this should return False because there's a wall
                    if can_move:
                        print(f"  ✗ FAILED: Player can move into wall at ({x}, {y}) while off-center!")
                        return False
                    else:
                        print(f"  ✓ PASS: Player correctly blocked from moving into wall at ({x}, {y})")
                        test_found = True
                        break
        if test_found:
            break

    if not test_found:
        print("  ! Warning: Could not find a suitable wall to test")
        return True

    # Test that player CAN still move when there's a valid path
    print("\nTesting that valid movement still works...")
    start_x, start_y = maze.get_start_position()
    player = Player(start_x, start_y, config, collision_manager)

    # Try all four directions to find at least one valid move
    valid_move_found = False
    for direction in ['up', 'down', 'left', 'right']:
        if player._can_move_in_direction(direction):
            print(f"  ✓ PASS: Player can move {direction} from start position")
            valid_move_found = True
            break

    if not valid_move_found:
        print("  ✗ FAILED: Player cannot move in any direction from start!")
        return False

    return True


if __name__ == '__main__':
    print("=" * 70)
    print("Wall Sliding Bug Fix Verification")
    print("=" * 70)
    print()

    try:
        if test_wall_sliding_bug():
            print()
            print("=" * 70)
            print("✓ All wall sliding tests passed!")
            print("=" * 70)
            sys.exit(0)
        else:
            print()
            print("=" * 70)
            print("✗ Wall sliding test FAILED!")
            print("=" * 70)
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
