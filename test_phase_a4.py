"""
Test Phase A4: Pac-Man style maze generation and collision system.
"""

import sys
sys.path.insert(0, 'src')

from systems.maze import Maze
import configparser

def test_maze_generation():
    """Test Pac-Man style maze generation."""
    print("Testing Pac-Man style maze generation...")

    # Create maze with test parameters
    maze = Maze(
        grid_size=20,
        tile_size=40,
        wall_density=0.2,
        max_wall_length=4,
        max_attempts=100
    )

    # Count walls
    wall_count = 0
    total_cells = maze.grid_size * maze.grid_size

    for row in maze.grid:
        for cell in row:
            if cell == 1:  # WALL
                wall_count += 1

    actual_density = wall_count / total_cells

    print(f"  Grid size: {maze.grid_size}x{maze.grid_size}")
    print(f"  Total cells: {total_cells}")
    print(f"  Wall cells: {wall_count}")
    print(f"  Wall density: {actual_density:.2%} (target: 20%)")
    print(f"  Start position: {maze.start_pos}")
    print(f"  End position: {maze.end_pos}")

    # Verify maze is valid
    assert maze.start_pos is not None, "Start position should be set"
    assert maze.end_pos is not None, "End position should be set"
    assert maze.start_pos != maze.end_pos, "Start and end should be different"

    # Check that start and end are paths
    start_x, start_y = maze.start_pos
    end_x, end_y = maze.end_pos
    assert not maze.is_wall(start_x, start_y), "Start should be on a path"
    assert not maze.is_wall(end_x, end_y), "End should be on a path"

    # Check connectivity
    is_connected = maze._is_connected(maze.start_pos, maze.end_pos)
    assert is_connected, "Start and end should be connected"

    print("  ✓ Maze generation successful")
    print("  ✓ Start and end positions valid")
    print("  ✓ Path connectivity verified")
    print()

def visualize_maze():
    """Visualize a sample maze in ASCII."""
    print("Sample Pac-Man style maze (20x20, 20% walls):")
    print()

    maze = Maze(
        grid_size=20,
        tile_size=40,
        wall_density=0.2,
        max_wall_length=4,
        max_attempts=100
    )

    # Print maze
    for y in range(maze.grid_size):
        for x in range(maze.grid_size):
            if (x, y) == maze.start_pos:
                print('S', end='')  # Start
            elif (x, y) == maze.end_pos:
                print('E', end='')  # End
            elif maze.is_wall(x, y):
                print('█', end='')  # Wall
            else:
                print('·', end='')  # Path
        print()
    print()
    print("Legend: S=Start, E=End, █=Wall, ·=Path")
    print()

if __name__ == '__main__':
    print("=" * 60)
    print("Phase A4 Test Suite")
    print("=" * 60)
    print()

    test_maze_generation()
    visualize_maze()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
