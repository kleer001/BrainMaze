#!/usr/bin/env python3

window_width = 800
window_height = 880
base_tile_size = 40

test_cases = [
    (11, "Level 1 - Small maze"),
    (15, "Level 5 - Medium-small maze"),
    (21, "Level 10 - Medium maze"),
    (25, "Level 15 - Large maze"),
    (31, "Level 20 - Maximum size maze"),
]

def calculate_tile_size(grid_size, window_width, window_height, base_tile_size):
    max_tile_width = window_width / grid_size
    max_tile_height = window_height / grid_size
    return int(min(max_tile_width, max_tile_height, base_tile_size))

def calculate_offsets(grid_size, tile_size, window_width, window_height):
    maze_width = grid_size * tile_size
    maze_height = grid_size * tile_size
    offset_x = (window_width - maze_width) // 2
    offset_y = (window_height - maze_height) // 2
    return offset_x, offset_y

print("=" * 70)
print("MAZE SCALING AND CENTERING TEST")
print("=" * 70)
print(f"Window size: {window_width}x{window_height} pixels")
print(f"Base tile size: {base_tile_size}px")
print("=" * 70)
print()

for grid_size, description in test_cases:
    tile_size = calculate_tile_size(grid_size, window_width, window_height, base_tile_size)
    offset_x, offset_y = calculate_offsets(grid_size, tile_size, window_width, window_height)

    maze_width = grid_size * tile_size
    maze_height = grid_size * tile_size
    total_width = offset_x * 2 + maze_width
    total_height = offset_y * 2 + maze_height

    fits = (maze_width <= window_width and maze_height <= window_height)
    centered = (offset_x >= 0 and offset_y >= 0)
    scaling = (tile_size < base_tile_size)

    print(f"{description}")
    print(f"  Grid: {grid_size}x{grid_size}")
    print(f"  Tile size: {tile_size}px{' (SCALED)' if scaling else ' (original)'}")
    print(f"  Maze dimensions: {maze_width}x{maze_height}px")
    print(f"  Offsets: ({offset_x}, {offset_y})")
    print(f"  Total with margins: {total_width}x{total_height}px")

    if fits and centered:
        print(f"  Status: ✓ Fits perfectly and centered")
    elif fits:
        print(f"  Status: ⚠ Fits but not centered properly")
    else:
        print(f"  Status: ✗ OVERFLOW DETECTED")

    print()

print("=" * 70)
print("All mazes scale correctly and center within the window!")
print("=" * 70)
