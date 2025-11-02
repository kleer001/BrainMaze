# 🧠 Brain Maze

> *Leave your thoughts behind to learn the facts ahead*

An educational maze game where you play as a brain navigating procedurally generated mazes, placing thought-mines to capture roaming facts. Built with Python and Pygame.

[![Made with Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Powered by Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg)](https://www.pygame.org/)
[![Built with Claude](https://img.shields.io/badge/Built_with-Claude_AI-purple.svg)](https://www.anthropic.com/)

---

## 🎮 Features

- 🧠 **Play as a Brain** - Navigate mazes in real-time
- 💭 **Thought Mines** - Place strategic traps for wandering facts
- 🐱 **Educational Themes** - Learn facts about cats, bears, vehicles, and more
- 🤖 **Smart AI** - Enemies with randomized behaviors and personalities
- ⚡ **Power-ups** - Speed boosts, shields, extra mines (and cursed variants!)
- 🎨 **Procedural Mazes** - Every level is unique
- 🏆 **Progressive Difficulty** - Scales with player skill

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Pygame 2.5+

### Installation

```bash
# Clone the repository
git clone https://github.com/Kleer001/brain-maze.git
cd brain-maze

# Install dependencies
pip install pygame

# Run the game
python main.py
```

---

## 🎯 How to Play

- **WASD / Arrow Keys** - Move your brain
- **M** - Drop a thought mine
- **ESC** - Pause menu

**Goal:** Capture all facts by luring them into your thought mines. Avoid getting caught!

---

## 🛠️ Development Status

**Current Phase:** 🏗️ Phase A - Core Movement & Collision

| Phase | Status | Features |
|-------|--------|----------|
| **A** | 🏗️ In Progress | Player movement, maze generation, basic AI |
| **B** | ⏳ Planned | Mine system |
| **C** | ⏳ Planned | Powerups |
| **D** | ⏳ Planned | Polish & progression |

See [DEVELOPER_ROADMAP.md](DEVELOPER_ROADMAP.md) for detailed implementation plan.

---

## 📚 Documentation

- [Game Design Document](GAME_DESIGN_DOCUMENT.md) - Complete game mechanics
- [Developer Roadmap](DEVELOPER_ROADMAP.md) - Phased implementation guide

---

## 🎨 Project Structure

```
brain_maze/
├── main.py              # Game loop
├── entities/            # Player, enemies, mines
├── systems/             # Maze, collision, effects
├── ui/                  # HUD, trivia panel
├── ai/                  # Behaviors, pathfinding
├── config/              # INI configuration files
└── assets/data/         # Fact databases (JSON)
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