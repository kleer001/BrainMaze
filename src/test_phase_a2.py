"""
Test script for Phase A2: Maze Generation & Wall Collision
Validates maze generation and collision detection without requiring display.
"""

import sys
import configparser
from pathlib import Path

# Import systems
from systems.maze import Maze
from systems.maze_constants import WALL, PATH
from systems.collision import CollisionManager


def test_maze_generation():
    """Test that maze generates correctly."""
    print("Testing maze generation...")

    maze = Maze(20, 40)

    # Check that maze has grid (should be 2*((20-1)//2)+1 = 19)
    expected_size = 2 * ((20 - 1) // 2) + 1
    assert len(maze.grid) == expected_size, f"Maze should have {expected_size} rows"
    assert len(maze.grid[0]) == expected_size, f"Maze should have {expected_size} columns"

    # Check that start and end positions exist
    assert maze.start_pos is not None, "Start position should be set"
    assert maze.end_pos is not None, "End position should be set"
    assert maze.start_pos != maze.end_pos, "Start and end should be different"

    print(f"  ✓ Maze generated: {len(maze.grid)}x{len(maze.grid[0])} grid")
    print(f"  ✓ Path cells: {maze.path_size}x{maze.path_size}")
    print(f"  ✓ Start position: {maze.start_pos}")
    print(f"  ✓ End position: {maze.end_pos}")

    # Check that we have both walls and paths
    wall_count = sum(1 for row in maze.grid for cell in row if cell == WALL)
    path_count = sum(1 for row in maze.grid for cell in row if cell == PATH)

    assert wall_count > 0, "Maze should have walls"
    assert path_count > 0, "Maze should have paths"
    print(f"  ✓ Maze has {wall_count} wall cells and {path_count} path cells")

    # Check that start and end positions are paths
    start_x, start_y = maze.start_pos
    end_x, end_y = maze.end_pos
    assert maze.grid[start_y][start_x] == PATH, "Start position should be a path"
    assert maze.grid[end_y][end_x] == PATH, "End position should be a path"
    print(f"  ✓ Start and end positions are valid paths")

    return maze


def test_wall_detection(maze):
    """Test wall detection."""
    print("\nTesting wall detection...")

    # Test that we can't move to wall cells
    # Find a wall cell
    wall_found = False
    for y in range(maze.grid_size):
        for x in range(maze.grid_size):
            if maze.grid[y][x] == WALL:
                # Try to move to this wall from an adjacent path (if it exists)
                for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    from_x, from_y = x - dx, y - dy
                    if maze._is_valid_grid_cell(from_x, from_y) and maze.grid[from_y][from_x] == PATH:
                        can_move = maze.can_move_to(from_x, from_y, x, y)
                        assert not can_move, f"Should not be able to move to wall at ({x}, {y})"
                        wall_found = True
                        break
                if wall_found:
                    break
        if wall_found:
            break

    assert wall_found, "Should have found at least one wall to test"
    print(f"  ✓ Wall detection working correctly - can't move to walls")

    # Test that we can move to path cells
    start_x, start_y = maze.start_pos
    path_move_tested = False
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
        to_x, to_y = start_x + dx, start_y + dy
        if maze._is_valid_grid_cell(to_x, to_y) and maze.grid[to_y][to_x] == PATH:
            can_move = maze.can_move_to(start_x, start_y, to_x, to_y)
            assert can_move, f"Should be able to move to path at ({to_x}, {to_y})"
            path_move_tested = True
            break

    assert path_move_tested, "Should have found at least one adjacent path to test"
    print(f"  ✓ Path detection working correctly - can move to paths")


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
