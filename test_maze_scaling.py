#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from systems.maze import Maze
from systems.maze_type_1 import MazeType1

window_width = 800
window_height = 880

test_cases = [
    (11, "Level 1 - Small maze"),
    (15, "Level 5 - Medium-small maze"),
    (21, "Level 10 - Medium maze"),
    (25, "Level 15 - Large maze"),
    (31, "Level 20 - Maximum size maze"),
]

print("=" * 70)
print("MAZE SCALING AND CENTERING TEST")
print("=" * 70)
print(f"Window size: {window_width}x{window_height} pixels")
print("=" * 70)
print()

for grid_size, description in test_cases:
    generator = MazeType1(1, 3, 'vertical')
    maze = Maze(grid_size, 40, 1, 3, 'vertical', 100, generator, 4, window_width, window_height)

    maze_width = grid_size * maze.tile_size
    maze_height = grid_size * maze.tile_size

    total_width = maze.offset_x * 2 + maze_width
    total_height = maze.offset_y * 2 + maze_height

    fits = (total_width <= window_width and total_height <= window_height)
    centered = (maze.offset_x >= 0 and maze.offset_y >= 0)

    print(f"{description}")
    print(f"  Grid: {grid_size}x{grid_size}")
    print(f"  Tile size: {maze.tile_size}px (base: 40px)")
    print(f"  Maze dimensions: {maze_width}x{maze_height}px")
    print(f"  Offsets: ({maze.offset_x}, {maze.offset_y})")
    print(f"  Total render area: {total_width}x{total_height}px")

    if fits and centered:
        print(f"  Status: ✓ Fits and centered correctly")
    elif fits:
        print(f"  Status: ⚠ Fits but not centered")
    elif centered:
        print(f"  Status: ⚠ Centered but overflows")
    else:
        print(f"  Status: ✗ PROBLEM - overflow and not centered")

    print()

print("=" * 70)
print("Test complete!")
print("=" * 70)
