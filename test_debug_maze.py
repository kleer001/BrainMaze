#!/usr/bin/env python3
"""
Quick test to verify debug mode works in maze generation.
This will generate a small maze with debug mode enabled to visualize the carving process.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from systems.maze import Maze
import configparser
from pathlib import Path

def test_debug_mode():
    """Test maze generation with debug mode enabled."""
    print("Testing maze generation with debug mode enabled...")
    print("This should take longer as it adds a 0.1 second delay per cell carved.")
    print()

    # Temporarily enable debug mode in config
    config_path = Path('config/maze_config.ini')
    config = configparser.ConfigParser()

    if config_path.exists():
        config.read(config_path)
        original_debug_mode = config.get('Debug', 'debug_mode', fallback='false')

        # Enable debug mode
        config.set('Debug', 'debug_mode', 'true')
        with open(config_path, 'w') as f:
            config.write(f)

        print("Debug mode enabled in config file.")
        print("Generating a small 11x11 maze with 0.1 second delay per cell...")
        print()

        try:
            # Generate a small maze
            maze = Maze(grid_size=11, tile_size=32)

            print()
            print("Maze generation complete!")
            print(f"Start position: {maze.start_pos}")
            print(f"End position: {maze.end_pos}")
            print(f"Grid size: {maze.grid_size}x{maze.grid_size}")

            # Count path cells
            path_cells = sum(1 for row in maze.grid for cell in row if cell == 0)
            total_cells = maze.grid_size * maze.grid_size
            print(f"Path cells: {path_cells}/{total_cells} ({path_cells/total_cells*100:.1f}%)")

        finally:
            # Restore original debug mode
            config.set('Debug', 'debug_mode', original_debug_mode)
            with open(config_path, 'w') as f:
                config.write(f)
            print()
            print(f"Debug mode restored to: {original_debug_mode}")
    else:
        print(f"Config file not found at {config_path}")
        print("The maze will use default settings (debug_mode = false)")

if __name__ == '__main__':
    test_debug_mode()
