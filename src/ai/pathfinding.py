"""
Greedy pathfinding for enemy navigation.
Phase A5: Simple, cheap movement towards targets.
"""

import random
from typing import Tuple, Optional


def get_direction_towards_target(
    current_x: int,
    current_y: int,
    target_x: int,
    target_y: int,
    can_move_callback
) -> Optional[str]:
    """
    Get the best direction to move towards a target using greedy selection.

    Strategy:
    1. Try to move in the axis with the largest distance first
    2. If blocked, try the other axis
    3. If both blocked, try perpendicular directions
    4. If all blocked, return None (stuck)

    Args:
        current_x: Current tile X position
        current_y: Current tile Y position
        target_x: Target tile X position
        target_y: Target tile Y position
        can_move_callback: Function(direction) -> bool that checks if movement is valid

    Returns:
        Direction string ('up', 'down', 'left', 'right') or None if stuck
    """
    # Already at target
    if current_x == target_x and current_y == target_y:
        return None

    # Calculate deltas
    dx = target_x - current_x
    dy = target_y - current_y

    # Determine primary and secondary axes
    if abs(dx) > abs(dy):
        # X axis has larger distance - prioritize horizontal movement
        primary = 'right' if dx > 0 else 'left'
        secondary = 'down' if dy > 0 else 'up' if dy != 0 else None
    elif abs(dy) > abs(dx):
        # Y axis has larger distance - prioritize vertical movement
        primary = 'up' if dy < 0 else 'down'
        secondary = 'right' if dx > 0 else 'left' if dx != 0 else None
    else:
        # Equal distance - randomly choose which to prioritize
        if random.choice([True, False]):
            primary = 'right' if dx > 0 else 'left'
            secondary = 'down' if dy > 0 else 'up'
        else:
            primary = 'up' if dy < 0 else 'down'
            secondary = 'right' if dx > 0 else 'left'

    # Try primary direction first
    if can_move_callback(primary):
        return primary

    # Try secondary direction
    if secondary and can_move_callback(secondary):
        return secondary

    # Both axes blocked - try perpendicular directions
    # Get all perpendicular directions to primary
    all_directions = ['up', 'down', 'left', 'right']
    tried = {primary}
    if secondary:
        tried.add(secondary)

    remaining = [d for d in all_directions if d not in tried]
    random.shuffle(remaining)  # Randomize to avoid predictable stuck patterns

    for direction in remaining:
        if can_move_callback(direction):
            return direction

    # Completely stuck
    return None


def get_direction_away_from_target(
    current_x: int,
    current_y: int,
    target_x: int,
    target_y: int,
    can_move_callback
) -> Optional[str]:
    """
    Get the best direction to move AWAY from a target (for flee behavior).

    Args:
        current_x: Current tile X position
        current_y: Current tile Y position
        target_x: Target tile X position
        target_y: Target tile Y position
        can_move_callback: Function(direction) -> bool that checks if movement is valid

    Returns:
        Direction string ('up', 'down', 'left', 'right') or None if stuck
    """
    # Calculate deltas (inverted for fleeing)
    dx = current_x - target_x
    dy = current_y - target_y

    # Use same logic but with inverted target
    inverted_target_x = current_x + dx
    inverted_target_y = current_y + dy

    return get_direction_towards_target(
        current_x, current_y,
        inverted_target_x, inverted_target_y,
        can_move_callback
    )


def find_nearest_walkable_tile(maze, target_x: int, target_y: int, max_search_radius: int = 10) -> Optional[Tuple[int, int]]:
    """
    Find the nearest walkable tile to a target position.
    Uses BFS to search in expanding circles.

    Args:
        maze: Maze instance
        target_x: Target X coordinate
        target_y: Target Y coordinate
        max_search_radius: Maximum tiles to search from target

    Returns:
        Nearest walkable (x, y) position, or None if none found
    """
    # If target is already walkable, return it
    if not maze.is_wall(target_x, target_y):
        return (target_x, target_y)

    # BFS to find nearest walkable tile
    visited = set()
    queue = [(target_x, target_y, 0)]  # (x, y, distance)
    visited.add((target_x, target_y))

    while queue:
        x, y, dist = queue.pop(0)

        # Check if we've exceeded max search radius
        if dist > max_search_radius:
            break

        # Check all 4 neighbors
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy

            # Check bounds
            if nx < 0 or nx >= maze.grid_size or ny < 0 or ny >= maze.grid_size:
                continue

            # Skip if visited
            if (nx, ny) in visited:
                continue

            visited.add((nx, ny))

            # If walkable, return it
            if not maze.is_wall(nx, ny):
                return (nx, ny)

            # Add to queue for further searching
            queue.append((nx, ny, dist + 1))

    # No walkable tile found
    return None
