# Qix Maze Level Editor

Procedural maze generator using Qix algorithm. Guarantees connectivity, single-width corridors, and perfect symmetry.

## Features

- **Qix Algorithm:** Carves from frontier with guaranteed connectivity
- **Perfect Symmetry:** Left-right mirroring with skip on odd-width grids
- **Single-Width Corridors:** No double-thickness passages
- **Interactive Editor:** Real-time visualization
- **JSON Export:** Save mazes for use in games

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python qix_editor.py
```

### Controls

- **SPACE:** Generate new maze
- **E:** Export to JSON
- **R:** Reset grid
- **ESC:** Quit

## Configuration

Edit `qix_config.ini` to adjust:
- Grid size (must be odd width)
- Fill target percentage
- Chamber size ranges
- Corridor length ranges
- Colors and display settings

## Export Format

Mazes export as JSON with grid, start/end positions, and generation config.

```json
{
  "width": 21,
  "height": 21,
  "grid": [[0, 1, 0, ...], ...],
  "start_pos": [1, 1],
  "end_pos": [19, 19],
  "generation_config": { ... }
}
```

## Integration with Brain Maze

1. Copy `qix_algorithm.py` to `src/systems/qix_maze.py`
2. Update `src/systems/maze.py` to use `QixMazeGenerator`
3. Export mazes as JSON and load via game config

## Cell Types

- **0 (WALL):** Impassable wall
- **1 (CORRIDOR):** Single-width playable space
- **2 (CHAMBER):** Wider chamber areas

---

**Built for Brain Maze** - Educational maze collection game