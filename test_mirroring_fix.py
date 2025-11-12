#!/usr/bin/env python3
"""
Test to verify maze mirroring works correctly with single center axis.
Ensures no doubling of the center column/row.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from systems.maze_type_1 import MazeType1
from systems.maze_type_2 import MazeType2
from systems.maze_type_3 import MazeType3
from systems.maze_type_4 import MazeType4


def check_vertical_mirroring(grid, grid_size):
    """Check if grid is correctly vertically mirrored (left-right)."""
    center = grid_size // 2
    errors = []

    # Check that left side mirrors to right side
    for i in range(center):
        mirror_i = grid_size - 1 - i
        for j in range(grid_size):
            if grid[j][i] != grid[j][mirror_i]:
                errors.append(f"Mismatch at row {j}: col {i} != col {mirror_i}")

    return len(errors) == 0, errors


def check_no_center_doubling(grid, grid_size, is_vertical):
    """Verify center column/row is unique (not doubled)."""
    center = grid_size // 2

    if is_vertical:
        # Check center column is different from adjacent column
        # (unless they happen to be the same by generation, but shouldn't be copies)
        center_col = [grid[j][center] for j in range(grid_size)]
        left_col = [grid[j][center - 1] for j in range(grid_size)]
        right_col = [grid[j][center + 1] for j in range(grid_size)]

        # Center should not be identical to BOTH neighbors
        # (that would indicate it was overwritten by mirroring)
        identical_to_left = center_col == left_col
        identical_to_right = center_col == right_col

        return not (identical_to_left and identical_to_right)
    else:
        # Check center row
        center_row = grid[center]
        top_row = grid[center - 1]
        bottom_row = grid[center + 1]

        identical_to_top = center_row == top_row
        identical_to_bottom = center_row == bottom_row

        return not (identical_to_top and identical_to_bottom)


def test_maze_type(maze_type, name, grid_size=11):
    """Test a specific maze type."""
    print(f"\nTesting {name} (grid_size={grid_size}):")
    print("-" * 50)

    generator = maze_type
    grid = generator.generate(grid_size)

    # Test 1: Check mirroring is correct
    is_mirrored, errors = check_vertical_mirroring(grid, grid_size)
    if is_mirrored:
        print("✓ Mirroring is correct")
    else:
        print("✗ Mirroring has errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  {error}")

    # Test 2: Check no center doubling
    no_doubling = check_no_center_doubling(grid, grid_size, is_vertical=True)
    if no_doubling:
        print("✓ Center column is unique (not doubled)")
    else:
        print("✗ Center column appears to be doubled")

    # Test 3: Verify center column index
    center = grid_size // 2
    print(f"✓ Center column index: {center} (0-indexed)")

    return is_mirrored and no_doubling


def main():
    """Run tests on all maze types."""
    print("=" * 60)
    print("MAZE MIRRORING FIX VERIFICATION")
    print("=" * 60)

    test_sizes = [11, 13, 15, 21, 31]

    for size in test_sizes:
        print(f"\n{'=' * 60}")
        print(f"Grid Size: {size}x{size}")
        print(f"{'=' * 60}")

        results = []

        # Test each maze type
        type1 = MazeType1(min_wall_length=1, max_wall_length=3, orientation='vertical')
        results.append(test_maze_type(type1, "MazeType1", size))

        type2 = MazeType2(north_bias=0.5, orientation='vertical')
        results.append(test_maze_type(type2, "MazeType2", size))

        type3 = MazeType3(orientation='vertical')
        results.append(test_maze_type(type3, "MazeType3", size))

        type4 = MazeType4(orientation='vertical')
        results.append(test_maze_type(type4, "MazeType4", size))

        print(f"\n{'=' * 60}")
        if all(results):
            print(f"✓ ALL TESTS PASSED for grid size {size}")
        else:
            print(f"✗ Some tests failed for grid size {size}")
        print(f"{'=' * 60}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
