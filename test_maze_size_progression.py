#!/usr/bin/env python3
"""
Test script to demonstrate maze size progression over levels.
Shows how grid size scales from minimum to maximum over the progression levels.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import configparser
from systems.game_state import GameState
from systems.fact_loader import FactLoader


def test_maze_progression():
    """Test and display maze size progression over levels."""
    # Load config
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / 'src' / 'config' / 'gameplay.ini'
    config.read(config_path)

    # Create fact loader (needed for GameState)
    data_directory = Path(__file__).parent / 'assets' / 'data'
    fact_loader = FactLoader(str(data_directory))

    # Create game state
    game_state = GameState(config, fact_loader)

    print("=" * 60)
    print("MAZE SIZE PROGRESSION TEST")
    print("=" * 60)
    print(f"Min grid size: {game_state.grid_size_min}")
    print(f"Max grid size: {game_state.grid_size_max}")
    print(f"Progression levels: {game_state.grid_size_progression_levels}")
    print("=" * 60)
    print()

    print(f"{'Level':<8} {'Grid Size':<12} {'Total Cells':<12} {'Visual'}")
    print("-" * 60)

    # Test first 25 levels to show progression and plateau
    for level in range(1, 26):
        game_state.current_level = level
        grid_size = game_state.get_grid_size_for_level()
        total_cells = grid_size * grid_size

        # Visual representation (each █ = 2x2 cells)
        visual_blocks = "█" * (grid_size // 2)

        print(f"{level:<8} {grid_size:<12} {total_cells:<12} {visual_blocks}")

    print()
    print("=" * 60)
    print("Progression Summary:")
    print(f"  Level 1 starts at {game_state.grid_size_min}x{game_state.grid_size_min}")
    print(f"  Level {game_state.grid_size_progression_levels} reaches {game_state.grid_size_max}x{game_state.grid_size_max}")
    print(f"  After level {game_state.grid_size_progression_levels}, size stays at maximum")
    print("=" * 60)


if __name__ == '__main__':
    test_maze_progression()
