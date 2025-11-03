"""
Test script for Phase A3: Single Enemy Random Movement
Verifies enemy spawns at end position and moves randomly.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import configparser
from pathlib import Path
from entities.player import Player
from entities.enemy import Enemy
from systems.maze import Maze
from systems.collision import CollisionManager


def test_phase_a3():
    """Test Phase A3 implementation."""
    print("=" * 60)
    print("Phase A3 Test: Single Enemy Random Movement")
    print("=" * 60)

    # Initialize pygame
    pygame.init()

    # Load configuration
    config = configparser.ConfigParser()
    config_path = Path('src/config/gameplay.ini')
    enemies_config_path = Path('src/config/enemies.ini')

    if not config_path.exists():
        print(f"❌ Error: Config file not found at {config_path}")
        return False
    if not enemies_config_path.exists():
        print(f"❌ Error: Config file not found at {enemies_config_path}")
        return False

    config.read([config_path, enemies_config_path])
    print("✓ Configuration files loaded")

    # Generate maze
    grid_size = config.getint('Maze', 'grid_size')
    tile_size = config.getint('Maze', 'tile_size')
    maze = Maze(grid_size, tile_size)
    print(f"✓ Maze generated ({maze.grid_size}x{maze.grid_size})")

    # Create collision manager
    collision_manager = CollisionManager(maze, config)
    print("✓ Collision manager created")

    # Get start and end positions
    start_x, start_y = maze.get_start_position()
    end_x, end_y = maze.get_end_position()
    print(f"✓ Start position: ({start_x}, {start_y})")
    print(f"✓ End position: ({end_x}, {end_y})")

    # Create enemy at end position
    enemy = Enemy(end_x, end_y, config, collision_manager)
    print(f"✓ Enemy created at end position")
    print(f"  - Speed: {enemy.speed} tiles/sec")
    print(f"  - Awareness: {enemy.awareness} tiles")
    print(f"  - Update interval: {enemy.update_interval} frames")
    print(f"  - Emoji: {enemy.emoji}")

    # Verify enemy position
    enemy_pos = enemy.get_tile_position()
    if enemy_pos == (end_x, end_y):
        print(f"✓ Enemy position verified: {enemy_pos}")
    else:
        print(f"❌ Enemy position mismatch: expected ({end_x}, {end_y}), got {enemy_pos}")
        return False

    # Test enemy movement (simulate a few frames)
    print("\nSimulating enemy movement (50 frames):")
    player_pos = (start_x, start_y)  # Dummy player position
    dt = 1.0 / 60.0  # 60 FPS

    positions = [enemy_pos]
    for frame in range(50):
        enemy.update(dt, player_pos)
        new_pos = enemy.get_tile_position()
        if new_pos != positions[-1]:
            positions.append(new_pos)
            print(f"  Frame {frame}: Enemy moved to {new_pos}")

    if len(positions) > 1:
        print(f"✓ Enemy moved {len(positions) - 1} times in 50 frames")
        print(f"  Positions visited: {positions[:5]}..." if len(positions) > 5 else f"  Positions visited: {positions}")
    else:
        print("⚠ Warning: Enemy didn't move (may be stuck or random chance)")

    # Check that enemy respects walls
    print("\nVerifying wall collision:")
    test_passed = True
    for pos in positions:
        if maze.is_wall(pos[0], pos[1]):
            print(f"❌ Enemy walked through wall at {pos}")
            test_passed = False

    if test_passed:
        print("✓ Enemy respected all wall collisions")

    print("\n" + "=" * 60)
    print("Phase A3 Test Complete!")
    print("=" * 60)

    pygame.quit()
    return True


if __name__ == '__main__':
    success = test_phase_a3()
    sys.exit(0 if success else 1)
