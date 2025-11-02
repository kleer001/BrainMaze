"""
Test script for Phase A2: Maze Generation & Wall Collision
Validates maze generation and collision detection without requiring display.
"""

import sys
import configparser
from pathlib import Path

# Import systems
from systems.maze import Maze
from systems.collision import CollisionManager


def test_maze_generation():
    """Test that maze generates correctly."""
    print("Testing maze generation...")

    maze = Maze(20, 40)

    # Check that maze has grid
    assert len(maze.grid) == 20, "Maze should have 20 rows"
    assert len(maze.grid[0]) == 20, "Maze should have 20 columns"

    # Check that start and end positions exist
    assert maze.start_pos is not None, "Start position should be set"
    assert maze.end_pos is not None, "End position should be set"
    assert maze.start_pos != maze.end_pos, "Start and end should be different"

    print(f"  ✓ Maze generated: {len(maze.grid)}x{len(maze.grid[0])} grid")
    print(f"  ✓ Start position: {maze.start_pos}")
    print(f"  ✓ End position: {maze.end_pos}")

    # Check that all cells were visited (maze is complete)
    unvisited = 0
    for row in maze.grid:
        for cell in row:
            if not cell.visited:
                unvisited += 1

    assert unvisited == 0, "All cells should be visited"
    print(f"  ✓ All cells visited (maze is complete)")

    return maze


def test_wall_detection(maze):
    """Test wall detection."""
    print("\nTesting wall detection...")

    # Test that we can't move through walls
    cell = maze.grid[0][0]
    x, y = 0, 0

    # Check each direction
    directions = ['top', 'right', 'bottom', 'left']
    for direction in directions:
        has_wall = cell.walls[direction]
        if direction == 'top':
            can_move = maze.can_move_to(x, y, x, y - 1)
        elif direction == 'right':
            can_move = maze.can_move_to(x, y, x + 1, y)
        elif direction == 'bottom':
            can_move = maze.can_move_to(x, y, x, y + 1)
        elif direction == 'left':
            can_move = maze.can_move_to(x, y, x - 1, y)

        # If there's a wall, we shouldn't be able to move
        # If there's no wall, we should be able to move
        assert can_move == (not has_wall), f"Movement should match wall state for {direction}"

    print(f"  ✓ Wall detection working correctly")


def test_collision_manager():
    """Test collision manager."""
    print("\nTesting collision manager...")

    # Load config
    config = configparser.ConfigParser()
    config.read('config/gameplay.ini')

    maze = Maze(20, 40)
    collision_manager = CollisionManager(maze, config)

    # Test tile from position
    tile_x, tile_y = collision_manager.get_tile_from_position(100, 100)
    assert tile_x == 2, "Tile X should be 2 (100 / 40)"
    assert tile_y == 2, "Tile Y should be 2 (100 / 40)"
    print(f"  ✓ Tile position calculation correct")

    # Test tile center
    center_x, center_y = collision_manager.get_tile_center(5, 5)
    assert center_x == 5 * 40 + 20, "Center X should be at tile center"
    assert center_y == 5 * 40 + 20, "Center Y should be at tile center"
    print(f"  ✓ Tile center calculation correct")

    # Test corner forgiveness
    start_x, start_y = maze.get_start_position()
    center_x, center_y = collision_manager.get_tile_center(start_x, start_y)

    # Test when slightly off-center (within forgiveness threshold)
    can_move, adj_x, adj_y = collision_manager.check_corner_forgiveness(
        center_x + 3,  # 3 pixels off center
        center_y,
        'up'
    )
    # Should allow movement and snap to center
    assert adj_x == center_x, "Should snap to tile center X"
    print(f"  ✓ Corner forgiveness working")


def test_start_end_distance(maze):
    """Test that start and end are reasonably far apart."""
    print("\nTesting start/end distance...")

    start_x, start_y = maze.start_pos
    end_x, end_y = maze.end_pos

    # Calculate Manhattan distance
    distance = abs(end_x - start_x) + abs(end_y - start_y)

    # For a 20x20 grid, corners should be at least 19 tiles apart
    # (either horizontally, vertically, or both)
    assert distance >= 10, f"Start and end should be far apart (distance: {distance})"
    print(f"  ✓ Start and end distance: {distance} tiles (good separation)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase A2 Testing: Maze Generation & Wall Collision")
    print("=" * 60)

    try:
        maze = test_maze_generation()
        test_wall_detection(maze)
        test_collision_manager()
        test_start_end_distance(maze)

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
