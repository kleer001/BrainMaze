# 🧠 Brain Maze

> *Chase knowledge through the corridors of curiosity*

An educational maze game where you play as a brain navigating procedurally generated mazes, chasing and capturing roaming facts to learn. Built with Python and Pygame.

[![Made with Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Powered by Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg)](https://www.pygame.org/)
[![Built with Claude](https://img.shields.io/badge/Built_with-Claude_AI-purple.svg)](https://www.anthropic.com/)

---

## 🎮 Features

- 🧠 **Play as a Brain** - Navigate mazes in real-time
- 🏃 **Chase & Capture** - Hunt down roaming facts to learn from them
- 🐱 **Educational Themes** - Learn facts about cats, bears, vehicles, and more
- 🤖 **Smart AI** - Enemies with varied movement behaviors (wander, patrol)
- ✨ **Learning Moments** - Display facts after each capture
- 💣 **Mine System** - Trap enemies with limited mine inventory
- 🎨 **Procedural Mazes** - 4 different maze generation algorithms with mirroring
- 🏆 **Progressive Levels** - Complete levels by capturing 3 facts each
- 📊 **Level Progress Tracking** - Track your fact collection journey

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Pygame 2.5+

### Installation

```bash
# Clone the repository
git clone https://github.com/kleer001/BrainMaze.git
cd BrainMaze

# Install dependencies
pip install pygame

# Run the game
python src/main.py
```

---

## 🎯 How to Play

- **WASD / Arrow Keys** - Move your brain
- **SPACE** - Place a mine to trap enemies
- **ESC** - Pause menu

**Goal:** Chase and capture roaming facts to learn! Each level requires capturing 3 facts. Use your limited mine inventory strategically to trap enemies and complete your fact collection.

---

## 🛠️ Development Status

**Current Phase:** 🎯 Phase B - Capture Mechanics & Polish

| Phase | Status | Features |
|-------|--------|----------|
| **A** | ✅ Complete | Player movement, maze generation, enemy AI behaviors |
| **B** | ✅ Complete | Capture mechanics, fact display, level progression |
| **C** | 🏗️ In Progress | Visual effects, mine system |
| **D** | ⏳ Planned | Additional polish & powerups |

**Implemented Features:**
- ✅ Player movement with wall collision
- ✅ 4 procedurally generated maze types with symmetry
- ✅ Enemy AI with wander and patrol behaviors
- ✅ Fact capture and display system
- ✅ Level complete screen with fact summary
- ✅ Mine placement system with limited inventory
- ✅ Multiple educational themes (loaded from JSON)
- ✅ Progress tracking across levels

See [Dev_Roadmap.md](Dev_Roadmap.md) for detailed implementation plan.

---

## 📚 Documentation

- [Game Design Document](GAME_DESIGN_DOCUMENT.md) - Complete game mechanics
- [Developer Roadmap](DEVELOPER_ROADMAP.md) - Phased implementation guide

---

## 🎨 Project Structure

```
BrainMaze/
├── src/
│   ├── main.py              # Game loop & main entry point
│   ├── entities/            # Player, enemies
│   ├── systems/             # Maze generators, collision, effects, game state
│   ├── ui/                  # Fact display, level complete screen
│   └── config/              # INI configuration files
├── assets/data/         # Educational fact databases (JSON)
└── tests/               # Test suites for maze generation & behaviors
```

---

## 🤝 Contributing

This is a solo development project created by **Kleer001** with assistance from **Anthropic's Claude AI**. 

While contributions aren't currently being accepted, feel free to fork the project for your own educational purposes!

---

## 📝 License

[License TBD]

---

## 🙏 Acknowledgments

- 🤖 Built with [Claude](https://www.anthropic.com/) by Anthropic
- 🎮 Powered by [Pygame](https://www.pygame.org/)
- 💡 Inspired by classic maze chase games

---

**Made with 🧠 and 🤖 by Kleer001**