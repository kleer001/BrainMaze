import sys
sys.path.insert(0, 'src')

from systems.maze import Maze
from systems.maze_type_2 import MazeType2
from systems.maze_looper import loop_maze


def count_dead_ends(maze):
    dead_ends = 0
    for y in range(maze.grid_size):
        for x in range(maze.grid_size):
            if not maze.is_wall(x, y):
                open_count = sum(
                    1 for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]
                    if 0 <= x + dx < maze.grid_size
                    and 0 <= y + dy < maze.grid_size
                    and not maze.is_wall(x + dx, y + dy)
                )
                if open_count == 1:
                    dead_ends += 1
    return dead_ends


def test_binary_tree_generation():
    generator = MazeType2(north_bias=0.5)
    maze = Maze(grid_size=21, tile_size=30, generator=generator)

    print(f"Binary tree maze generated: {maze.grid_size}x{maze.grid_size}")
    print(f"Start position: {maze.start_pos}")
    print(f"End position: {maze.end_pos}")

    dead_ends_before = count_dead_ends(maze)
    print(f"Dead ends before looping: {dead_ends_before}")

    return maze, dead_ends_before


def test_maze_looper(maze):
    loop_maze(maze)

    dead_ends_after = count_dead_ends(maze)
    print(f"Dead ends after looping: {dead_ends_after}")

    return dead_ends_after


def main():
    print("Testing Binary Tree maze generation...")
    maze, dead_ends_before = test_binary_tree_generation()

    print("\nTesting maze looper...")
    dead_ends_after = test_maze_looper(maze)

    print("\n" + "="*50)
    if dead_ends_after == 0:
        print("SUCCESS: All dead ends removed!")
    else:
        print(f"WARNING: {dead_ends_after} dead ends remain")

    if dead_ends_before > 0:
        print(f"Removed {dead_ends_before - dead_ends_after} dead ends")

    print("="*50)


if __name__ == "__main__":
    main()
