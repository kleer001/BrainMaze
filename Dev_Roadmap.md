# Developer Roadmap: Brain Maze
## Phased Implementation Guide

---

## Project Structure

```
/brain_maze
├── main.py                 # Game loop, state management, level transitions
├── config/
│   ├── gameplay.ini        # Speeds, timers, spawn distances
│   ├── enemies.ini         # AI behavior parameters
│   └── powerups.ini        # Powerup durations and effects
├── entities/
│   ├── player.py           # Player sprite, movement, collision
│   ├── enemy.py            # Enemy base class with AI
│   ├── mine.py             # Mine sprite and trigger logic
│   └── powerup.py          # Powerup types and movement
├── systems/
│   ├── maze.py             # Procedural generation (recursive backtracker)
│   ├── collision.py        # Collision detection manager
│   ├── effects.py          # Screen shake, particles
│   └── game_state.py       # Level tracking, inventory, score
├── ui/
│   ├── hud.py              # Top bar (mines, level, shield)
│   ├── trivia_panel.py     # Bottom fact display
│   └── pause_menu.py       # ESC menu with controls/facts
├── ai/
│   ├── behaviors.py        # Movement behaviors (wander, seek, flee, etc.)
│   └── pathfinding.py      # A* for powerup movement
├── assets/
│   └── data/
│       ├── cats.json       # Cat facts
│       ├── bears.json      # Bear facts
│       └── ...
└── tests/
    ├── test_player.py
    ├── test_maze.py
    └── ...
```

---

## Development Phases

### Phase A: Core Movement & Collision

#### **A1: Player Movement (No Walls)**
**Goal:** Get player sprite moving smoothly on screen

**Tasks:**
1. Set up basic Pygame window (800×800)
2. Create `Player` class inheriting `pygame.sprite.Sprite`
3. Implement WASD/arrow key input handling
4. Update player position at 60 FPS
5. Draw player as colored rectangle

**Files:**
- `main.py` (minimal game loop)
- `entities/player.py`

**Testing:**
- Player moves in all 4 directions
- Movement is smooth and responsive
- Diagonal movement works correctly

**Estimated Time:** 2-3 hours

---

#### **A2: Maze Generation & Wall Collision**
**Goal:** Player navigates procedurally generated maze

**Tasks:**
1. Create `Maze` class with recursive backtracker algorithm
2. Generate 20×20 grid with start/end points
3. Render walls as colored tiles
4. Implement `pygame.Rect` collision detection
5. Prevent player from moving through walls

**Files:**
- `systems/maze.py`
- `systems/collision.py`
- Update `main.py` to instantiate maze

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [Maze]
  grid_size = 20
  tile_size = 32
  wall_density = 0.3
  ```

**Testing:**
- Maze generates correctly every time
- Player cannot pass through walls
- Start and end points are valid and distant

**Estimated Time:** 4-6 hours

---

#### **A3: Single Enemy Random Movement**
**Goal:** One enemy roams the maze randomly

**Tasks:**
1. Create `Enemy` class with randomized attributes
2. Implement "Wanderer" behavior (random direction changes)
3. Add enemy to `pygame.sprite.Group`
4. Update enemy position every 10 frames
5. Render enemy as emoji (🐱)

**Files:**
- `entities/enemy.py`
- `ai/behaviors.py` (Wanderer only)
- Update `main.py` to spawn enemy at "end"

**Configuration:**
- `config/enemies.ini`:
  ```ini
  [Attributes]
  speed_min = 1
  speed_max = 4
  awareness_min = 2
  awareness_max = 8
  
  [Spawning]
  spawn_distance_from_player = 12
  max_enemies_on_board = 5
  ```

**Testing:**
- Enemy spawns at end point
- Enemy moves randomly without getting stuck
- Enemy respects wall collisions

**Estimated Time:** 3-4 hours

---

#### **A4: Player-Enemy Collision & Fact Display**
**Goal:** Collision triggers fact display and respawn

**Tasks:**
1. Implement collision detection between player and enemies
2. Create text-based fact list (hardcoded for now)
3. Display random fact in bottom panel on collision
4. Respawn player at start with screen flash
5. Reset mines to 3

**Files:**
- `ui/trivia_panel.py`
- `systems/effects.py` (screen flash)
- Update `systems/collision.py`

**Testing:**
- Collision detection is accurate
- Fact appears immediately after collision
- Player respawns with 5-second invincibility (visual glow)
- Invincibility prevents further collisions

**Estimated Time:** 3-4 hours

---

#### **A5: Multiple AI Behaviors**
**Goal:** Enemies exhibit distinct movement patterns

**Tasks:**
1. Implement all behavior types:
   - Seeker (moves toward player)
   - Patrol (follows fixed path)
   - Flee (moves away from player)
   - Combo (switches based on distance)
2. Assign random behavior to each enemy on spawn
3. Use awareness radius for detection
4. Implement memory system (last seen position)

**Files:**
- Update `ai/behaviors.py` (all behaviors)
- `ai/pathfinding.py` (basic A* for seekers)

**Configuration:**
- `config/enemies.ini`:
  ```ini
  [Behaviors]
  behavior_types = wanderer,seeker,patrol,flee,combo
  seeker_aggression_threshold = 0.5
  flee_trigger_distance = 5
  ```

**Testing:**
- Each behavior type works as expected
- Seekers chase player when in range
- Flee enemies avoid player
- Patrol enemies follow consistent paths
- Combo enemies switch behaviors correctly

**Estimated Time:** 6-8 hours

---

### Phase B: Mines

#### **B1: Mine Placement**
**Goal:** Player can place mines on M key press

**Tasks:**
1. Create `Mine` class
2. Track mine inventory in `GameState`
3. Handle M key input
4. Place mine at player's current position
5. Add glow pulse effect on placement
6. Render mine as 💭 emoji

**Files:**
- `entities/mine.py`
- `systems/game_state.py`
- Update `ui/hud.py` to show mine count

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [Mines]
  max_inventory = 3
  glow_duration = 0.3
  ```

**Testing:**
- M key places mine correctly
- Mine count decreases in HUD
- Cannot place more than 3 mines
- Glow effect displays on placement

**Estimated Time:** 2-3 hours

---

#### **B2: Mine-Enemy Collision**
**Goal:** Mines eliminate enemies and display facts

**Tasks:**
1. Implement mine-enemy collision detection
2. Remove both mine and enemy on collision
3. Return mine to inventory
4. Load facts from JSON file (`cats.json`)
5. Display fact in trivia panel
6. Spawn new enemy if count < 5

**Files:**
- Update `systems/collision.py`
- Update `ui/trivia_panel.py` to load JSON
- Create `assets/data/cats.json`

**Testing:**
- Collision triggers correctly
- Mine returns to inventory
- Fact displays from JSON
- New enemy spawns at correct distance
- Level completes when all enemies eliminated

**Estimated Time:** 3-4 hours

---

### Phase C: Powerups

#### **C1: Powerup Spawning & Movement**
**Goal:** Powerups travel from end to start

**Tasks:**
1. Create `Powerup` class
2. Implement random-weighted pathfinding (end → start)
3. Spawn powerup at end point
4. Update position along path
5. Despawn when reaching start
6. Render as emoji (⚡ for speed, 💭 for mine, etc.)

**Files:**
- `entities/powerup.py`
- Update `ai/pathfinding.py` (random weighting)

**Configuration:**
- `config/powerups.ini`:
  ```ini
  [Spawning]
  spawn_interval = 15.0
  max_active = 2
  ```

**Testing:**
- Powerups spawn at end
- Follow valid paths to start
- Despawn correctly
- Multiple powerups don't overlap

**Estimated Time:** 4-5 hours

---

#### **C2: Powerup Types & Effects**
**Goal:** All powerup types functional

**Tasks:**
1. Implement powerup effects:
   - Speed Boost (+50%, 10s)
   - Extra Mine (+1 permanent)
   - Shield (1-hit protection, glow)
   - Slowdown (-30%, 10s/permanent)
   - Mine Loss (-1 permanent)
2. Handle effect stacking
3. Display shield glow on player
4. Update HUD to show active effects

**Files:**
- Update `entities/powerup.py`
- Update `entities/player.py` (effect application)
- Update `ui/hud.py` (shield icon)

**Configuration:**
- `config/powerups.ini`:
  ```ini
  [Effects]
  speed_boost_multiplier = 1.5
  speed_boost_duration = 10.0
  slowdown_multiplier = 0.7
  slowdown_duration = 10.0
  
  [Types]
  speed_boost_weight = 30
  extra_mine_weight = 20
  shield_weight = 25
  slowdown_weight = 15
  mine_loss_weight = 10
  ```

**Testing:**
- All powerup types work correctly
- Effects stack properly
- Shield blocks one hit then disappears
- Cursed powerups apply correctly
- Timer-based effects expire

**Estimated Time:** 5-6 hours

---

## Phase D: Polish & Progression

#### **D1: Visual Effects**
**Goal:** Screen shake, particles, animations

**Tasks:**
1. Implement screen shake on collision
2. Create particle system for:
   - Mine explosions
   - Powerup pickup sparkles
   - Invincibility glow particles
3. Maze build-in animation between levels
4. Smooth transitions

**Files:**
- Update `systems/effects.py`

**Estimated Time:** 4-5 hours

---

#### **D2: Level Progression System**
**Goal:** Multiple themes, difficulty scaling

**Tasks:**
1. Implement level-complete screen
2. Load next theme JSON
3. Scale enemy count per formula
4. Increase wall density
5. Track all collected facts in pause menu
6. Add "any key" advance functionality

**Files:**
- Update `systems/game_state.py`
- Update `ui/pause_menu.py`
- Create all theme JSON files

**Estimated Time:** 5-6 hours

---

#### **D3: Audio & Final Polish**
**Goal:** Sound effects, music, final UX touches

**Tasks:**
1. Add sound effects:
   - Mine placement
   - Collision
   - Powerup pickup
   - Level complete
2. Background music
3. Final HUD polish
4. Performance optimization
5. Comprehensive testing

**Estimated Time:** 6-8 hours

---

## Testing Protocol

**Per Phase:**
1. Manual testing of all features
2. Unit tests for critical systems (maze generation, collision)
3. Performance profiling (60 FPS target)

**Integration Testing:**
- Play through 3+ levels without crashes
- Verify all enemy behaviors work together
- Test edge cases (0 mines, all cursed powerups, etc.)

**Playtesting:**
- Kids (target audience) test for difficulty balance
- Adults test for bug discovery

---

## Estimated Timeline

| Phase | Hours | Days (4h/day) |
|-------|-------|---------------|
| A1-A5 | 18-25 | 5-7 |
| B1-B2 | 5-7 | 2-3 |
| C1-C2 | 9-11 | 3-4 |
| D1-D3 | 15-19 | 4-5 |
| **Total** | **47-62** | **14-19** |

---

## Dependencies

**Required Libraries:**
- `pygame >= 2.5.0`
- `configparser` (stdlib)
- `json` (stdlib)

**Installation:**
```bash
pip install pygame
```

---

## Version Control Strategy

**Branches:**
- `main` - stable releases only
- `develop` - active development
- Feature branches: `feature/a1-player-movement`, etc.

**Commits:**
- Commit after each sub-task completion
- Tag at end of each phase: `v0.1-phase-a`, etc.

---

## Next Steps

1. Review both documents with team/stakeholders
2. Set up project repository
3. Create INI config files with default values
4. Begin **Phase A1: Player Movement**

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-01
