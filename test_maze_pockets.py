"""
Test for isolated pockets in maze generation.
Check if all path cells are reachable from start position.
"""

import sys
sys.path.insert(0, 'src')

from systems.maze import Maze
from collections import deque

def count_reachable_cells(maze):
    """
    Count how many path cells are reachable from start using BFS.

    Returns:
        tuple: (reachable_count, total_path_count, has_pockets)
    """
    start_x, start_y = maze.start_pos

    # BFS from start
    queue = deque([maze.start_pos])
    visited = set([maze.start_pos])

    while queue:
        x, y = queue.popleft()

        # Check all 4 neighbors
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy

            # Check if valid and unvisited path
            if (0 <= nx < maze.grid_size and
                0 <= ny < maze.grid_size and
                not maze.is_wall(nx, ny) and
                (nx, ny) not in visited):
                visited.add((nx, ny))
                queue.append((nx, ny))

    # Count total path cells
    total_paths = 0
    for y in range(maze.grid_size):
        for x in range(maze.grid_size):
            if not maze.is_wall(x, y):
                total_paths += 1

    reachable = len(visited)
    has_pockets = reachable < total_paths

    return reachable, total_paths, has_pockets

def test_multiple_mazes():
    """Test multiple maze generations for pockets."""
    print("Testing 10 mazes for isolated pockets...")
    print()

    pocket_count = 0
    total_mazes = 10

    for i in range(total_mazes):
        maze = Maze(
            grid_size=20,
            tile_size=40,
            wall_density=0.2,
            max_wall_length=4,
            max_attempts=100
        )

        reachable, total_paths, has_pockets = count_reachable_cells(maze)

        if has_pockets:
            pocket_count += 1
            unreachable = total_paths - reachable
            print(f"  Maze {i+1}: ❌ HAS POCKETS - {unreachable} unreachable cells ({reachable}/{total_paths} reachable)")
        else:
            print(f"  Maze {i+1}: ✓ Fully connected ({reachable}/{total_paths} reachable)")

    print()
    print(f"Result: {pocket_count}/{total_mazes} mazes have isolated pockets")

    if pocket_count > 0:
        print()
        print("⚠️  WARNING: Isolated pockets detected!")
        print("   This means some areas are unreachable from the start position.")
        print("   Enemies/powerups spawned in pockets would be inaccessible.")
    else:
        print()
        print("✓ All mazes are fully traversable with no isolated pockets!")

    return pocket_count == 0

def visualize_reachability():
    """Visualize a maze showing reachable vs unreachable areas."""
    print()
    print("Visualizing maze reachability:")
    print()

    maze = Maze(
        grid_size=20,
        tile_size=40,
        wall_density=0.2,
        max_wall_length=4,
        max_attempts=100
    )

    # Get reachable cells
    start_x, start_y = maze.start_pos
    queue = deque([maze.start_pos])
    reachable = set([maze.start_pos])

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < maze.grid_size and
                0 <= ny < maze.grid_size and
                not maze.is_wall(nx, ny) and
                (nx, ny) not in reachable):
                reachable.add((nx, ny))
                queue.append((nx, ny))

    # Print maze with reachability
    for y in range(maze.grid_size):
        for x in range(maze.grid_size):
            if (x, y) == maze.start_pos:
                print('S', end='')  # Start
            elif (x, y) == maze.end_pos:
                print('E', end='')  # End
            elif maze.is_wall(x, y):
                print('█', end='')  # Wall
            elif (x, y) in reachable:
                print('·', end='')  # Reachable path
            else:
                print('X', end='')  # UNREACHABLE pocket!
        print()

    print()
    print("Legend: S=Start, E=End, █=Wall, ·=Reachable, X=UNREACHABLE POCKET")

    total_paths = sum(1 for y in range(maze.grid_size) for x in range(maze.grid_size) if not maze.is_wall(x, y))
    unreachable = total_paths - len(reachable)

    if unreachable > 0:
        print(f"⚠️  Found {unreachable} unreachable cells!")
    else:
        print("✓ All cells are reachable!")
    print()

if __name__ == '__main__':
    print("=" * 60)
    print("Maze Traversability Test")
    print("=" * 60)
    print()

    all_connected = test_multiple_mazes()
    visualize_reachability()

    print("=" * 60)
    if all_connected:
        print("✓ All tests passed - No pockets detected!")
    else:
        print("⚠️  Some mazes have isolated pockets!")
    print("=" * 60)
