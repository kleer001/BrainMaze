import sys
sys.path.insert(0, 'src')

from systems.maze import Maze
from systems.maze_type_1 import MazeType1
from systems.maze_type_2 import MazeType2
from systems.maze_type_3 import MazeType3
from systems.maze_type_4 import MazeType4


def analyze_maze(maze, maze_name):
    """Analyze maze properties."""
    print(f"\n{'='*60}")
    print(f"Testing {maze_name}")
    print(f"{'='*60}")

    # Count walls and paths
    walls = 0
    paths = 0
    for row in maze.grid:
        for cell in row:
            if cell == 1:
                walls += 1
            else:
                paths += 1

    print(f"Grid size: {maze.grid_size}x{maze.grid_size}")
    print(f"Total cells: {maze.grid_size * maze.grid_size}")
    print(f"Walls: {walls} ({walls / (maze.grid_size ** 2) * 100:.1f}%)")
    print(f"Paths: {paths} ({paths / (maze.grid_size ** 2) * 100:.1f}%)")
    print(f"Start position: {maze.start_pos}")
    print(f"End position: {maze.end_pos}")

    # Check mirroring
    is_vertical = True
    is_mirrored = check_mirroring(maze.grid, maze.grid_size, is_vertical)
    print(f"Vertical mirroring: {'✓' if is_mirrored else '✗'}")

    # Visualize small portion
    print("\nTop-left corner (10x10):")
    visualize_corner(maze.grid, 10)

    return walls, paths


def check_mirroring(grid, grid_size, is_vertical):
    """Check if grid is mirrored."""
    for i in range(grid_size // 2):
        mirror_i = grid_size - 1 - i
        for j in range(grid_size):
            if is_vertical:
                if grid[j][i] != grid[j][mirror_i]:
                    return False
            else:
                if grid[i][j] != grid[mirror_i][j]:
                    return False
    return True


def visualize_corner(grid, size):
    """Print a small corner of the maze."""
    for y in range(min(size, len(grid))):
        row = ""
        for x in range(min(size, len(grid[0]))):
            row += "█" if grid[y][x] == 1 else " "
        print(row)


def test_maze_type(maze_type_class, name, *args):
    """Test a specific maze type."""
    try:
        generator = maze_type_class(*args)
        maze = Maze(
            grid_size=21,
            tile_size=30,
            generator=generator
        )
        return analyze_maze(maze, name)
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR testing {name}: {e}")
        print(f"{'='*60}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("Testing All Maze Generation Algorithms")
    print("=" * 60)

    results = []

    # Test Type 1: Scattered walls
    result = test_maze_type(MazeType1, "Type 1: Scattered Walls", 1, 5, 'vertical')
    if result:
        results.append(("Type 1", result))

    # Test Type 2: Binary tree
    result = test_maze_type(MazeType2, "Type 2: Binary Tree", 0.5, 'vertical')
    if result:
        results.append(("Type 2", result))

    # Test Type 3: Recursive backtracking
    result = test_maze_type(MazeType3, "Type 3: Recursive Backtracking", 'vertical')
    if result:
        results.append(("Type 3", result))

    # Test Type 4: Sidewinder
    result = test_maze_type(MazeType4, "Type 4: Sidewinder", 'vertical')
    if result:
        results.append(("Type 4", result))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, (walls, paths) in results:
        print(f"{name:30} - Walls: {walls:4d}, Paths: {paths:4d}")

    print(f"\n{'='*60}")
    print(f"Successfully tested {len(results)}/4 maze types")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
