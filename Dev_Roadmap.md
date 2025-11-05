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
│   ├── player.py           # Player sprite, movement, collision, capture effects
│   ├── enemy.py            # Enemy base class with AI
│   └── powerup.py          # Powerup types and movement
├── systems/
│   ├── maze.py             # Procedural generation (recursive backtracker)
│   ├── collision.py        # Collision detection manager
│   ├── effects.py          # Particles, glow effects
│   └── game_state.py       # Level tracking, score, captured facts
├── ui/
│   ├── hud.py              # Top bar (level, score, active effects)
│   ├── fact_display.py     # Fact display during learning moments
│   └── pause_menu.py       # ESC menu with controls/facts
├── ai/
│   ├── behaviors.py        # Movement behaviors (wander, seek, flee, etc.)
│   └── pathfinding.py      # A* for seekers and powerup movement
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

### Phase A: Core Movement & Chase Mechanics

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


---

#### **A4: Player-Enemy Collision & Basic Capture**
**Goal:** Collision captures enemy (basic version, polish comes later)

**Tasks:**
1. Implement collision detection between player and enemies (every 4 frames for economy)
2. Remove captured enemy from game
3. Add basic score tracking to GameState
4. Increment score on capture
5. Add simple visual feedback (brief flash)

**Files:**
- `systems/game_state.py` (score tracking, captured facts list)
- Update `entities/player.py` (capture detection)
- Update `main.py` (collision checking, enemy removal)

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [Capture]
  collision_check_interval = 4  # Check every N frames
  ```

**Testing:**
- Collision detection is accurate (checked every 4 frames)
- Enemy is removed on collision
- Score increments correctly
- Basic visual feedback displays

**Note:** Fact display, freeze effect, and glow are deferred to Phase B


---

#### **A5: Multiple AI Behaviors**
**Goal:** Enemies exhibit distinct movement patterns

**Tasks:**
1. Implement waypoint-based behavior types:
   - Wanderer (variable waypoints - random targets)
   - Patrol (fixed waypoints - quadrant centers)
2. Assign random behavior to each enemy on spawn
3. Use BFS pathfinding for reliable navigation
4. Both behaviors follow same architecture pattern

**Files:**
- Update `ai/behaviors.py` (WandererBehavior, PatrolBehavior)
- `ai/pathfinding.py` (BFS pathfinding)
- `entities/enemy.py` (behavior assignment system)
- `test_a5_behaviors.py` (comprehensive test suite)

**Configuration:**
- `config/enemies.ini`:
  ```ini
  [Behaviors]
  behavior_types = wanderer,patrol
  ```

**Testing:**
- Wanderer navigates to random waypoints successfully
- Patrol follows fixed quadrant waypoints consistently
- Both behaviors handle pathfinding correctly
- Behavior assignment works on enemy spawn


---

### Phase B: Capture Mechanics & Fact Display

#### **B1: Fact Display on Capture**
**Goal:** Display educational facts when enemies are captured

**Tasks:**
1. Create fact display UI (center of screen, readable text)
2. Load facts from JSON file (`cats.json`)
3. Display fact when player captures enemy
4. Keep fact visible for reading time
5. Associate each enemy with a specific fact

**Files:**
- Create `ui/fact_display.py` (fact display panel)
- Create `assets/data/cats.json` (cat facts)
- Update `main.py` (integrate fact display)
- Update `entities/enemy.py` (associate facts with enemies)

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [Facts]
  display_duration = 3.0  # How long to show fact
  ```

**Testing:**
- Facts load correctly from JSON
- Fact displays on enemy capture
- Text is readable and centered
- Fact persists for configured duration


---

#### **B2: Freeze and Glow Effect**
**Goal:** Player freezes for 1 second and glows after capture

**Tasks:**
1. Implement player freeze state (disable movement)
2. Add glow/pulsing effect to player sprite
3. Add flickering animation during freeze
4. Time freeze to align with fact reading (1 second)
5. Resume normal movement after freeze ends

**Files:**
- Update `entities/player.py` (freeze state, glow effect, flickering)
- Update `systems/effects.py` (glow/pulse particles)

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [Capture]
  freeze_duration = 1.0
  glow_intensity = 0.8
  flicker_frequency = 10  # Flickers per second
  ```

**Testing:**
- Player freezes immediately on capture
- Glow effect is visible and attractive
- Flickering animation looks good
- Movement resumes after exactly 1 second
- Freeze gives time to start reading fact


---

#### **B3: Enemy Respawning**
**Goal:** Keep the chase going by spawning new enemies

**Tasks:**
1. Implement enemy respawn system
2. Spawn new enemy after capture
3. Maintain max enemy count on board
4. Randomize spawn locations (at safe distance)
5. Track total enemies captured per level

**Files:**
- Update `systems/game_state.py` (respawn logic, capture tracking)
- Update `main.py` (enemy spawning)

**Configuration:**
- `config/enemies.ini`:
  ```ini
  [Spawning]
  spawn_distance_from_player = 12
  max_enemies_on_board = 5
  enemies_per_level = 10  # Total to capture per level
  ```

**Testing:**
- New enemy spawns after capture
- Spawns at safe distance from player
- Max enemy count is respected
- Level completes after capturing all enemies
- Different enemy types spawn with variety


---

### Phase C: Visual Polish & Powerups

#### **C1: Enhanced Capture Effects**
**Goal:** Make captures feel rewarding and exciting

**Tasks:**
1. Implement particle burst on capture
2. Add screen flash effect (subtle, colorful)
3. Create capture sound effect hook
4. Polish glow effect with gradient
5. Add smooth transitions between states

**Files:**
- Update `systems/effects.py` (particles, screen effects)
- Update `entities/player.py` (smooth state transitions)

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [CaptureEffects]
  particle_count = 20
  particle_lifetime = 1.0
  screen_flash_color = 255,255,150  # Warm yellow
  screen_flash_intensity = 0.15
  flash_duration = 0.2
  ```

**Testing:**
- Particle burst looks exciting
- Screen flash is noticeable but not jarring
- All effects sync with capture moment
- Transitions feel smooth


---

#### **C2: Fact Display Polish**
**Goal:** Make facts easy and enjoyable to read

**Tasks:**
1. Design attractive fact panel with border
2. Add background blur/overlay behind fact
3. Implement text wrapping and formatting
4. Add fact source attribution if desired
5. Create fade-in/fade-out animations

**Files:**
- Update `ui/fact_display.py` (panel design, animations)

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [FactDisplay]
  panel_width = 600
  panel_padding = 20
  background_alpha = 0.9
  text_size = 18
  fade_duration = 0.3
  ```

**Testing:**
- Facts are easy to read
- Panel doesn't obscure important game elements
- Animations are smooth
- Text wraps correctly
- Different fact lengths display well


---

#### **C3: Powerup Spawning & Movement**
**Goal:** Powerups travel through maze offering blessings and curses

**Tasks:**
1. Create `Powerup` class
2. Implement random-weighted pathfinding (end → start)
3. Spawn powerups at end point periodically
4. Update position along path
5. Despawn when reaching start
6. Render as emoji (⚡ for speed, 🐌 for slow, ❄️ for freeze, etc.)

**Files:**
- Create `entities/powerup.py`
- Update `ai/pathfinding.py` (random weighting for powerup movement)

**Configuration:**
- `config/powerups.ini`:
  ```ini
  [Spawning]
  spawn_interval = 15.0
  max_active = 2
  path_randomness = 0.3  # How much to randomize the path
  ```

**Testing:**
- Powerups spawn at end point
- Follow valid paths through maze
- Despawn correctly when reaching start
- Multiple powerups don't overlap
- Movement looks natural


---

#### **C4: Powerup Types & Effects**
**Goal:** Blessings and curses that affect gameplay

**Tasks:**
1. Implement powerup effects:
   - **Speed Boost** (+50% speed, 10s) ⚡
   - **Slowdown** (-40% speed, 10s) 🐌
   - **Enemy Freeze** (enemies stop moving, 5s) ❄️
   - **Enemy Speed Up** (enemies move faster, 10s) 🔥
   - **Ghost Mode** (pass through enemies, 8s) 👻
2. Handle effect stacking and conflicts
3. Display active effects in HUD
4. Add visual indicators on player when affected
5. Balance blessing/curse probabilities

**Files:**
- Update `entities/powerup.py` (all types and effects)
- Update `entities/player.py` (effect application)
- Update `entities/enemy.py` (freeze and speed effects)
- Update `ui/hud.py` (active effects display)

**Configuration:**
- `config/powerups.ini`:
  ```ini
  [Effects]
  speed_boost_multiplier = 1.5
  speed_boost_duration = 10.0
  slowdown_multiplier = 0.6
  slowdown_duration = 10.0
  enemy_freeze_duration = 5.0
  enemy_speedup_multiplier = 1.4
  enemy_speedup_duration = 10.0
  ghost_mode_duration = 8.0

  [Types]
  # Weighted spawn chances
  speed_boost_weight = 25
  slowdown_weight = 15
  enemy_freeze_weight = 20
  enemy_speedup_weight = 15
  ghost_mode_weight = 25
  ```

**Testing:**
- All powerup types work correctly
- Effects apply and expire properly
- Speed changes are noticeable but balanced
- Enemy freeze stops all enemy movement
- Ghost mode allows passing through enemies without capture
- HUD shows current active effects
- Conflicting effects handle gracefully (e.g., speed boost + slowdown)


---

## Phase D: Level Progression & Themes

#### **D1: Maze Transitions**
**Goal:** Smooth level transitions with visual flair

**Tasks:**
1. Implement level complete screen
2. Show captured facts summary
3. Create maze build-in animation
4. Add "Ready?" countdown before next level
5. Smooth fade transitions

**Files:**
- Update `systems/effects.py` (transitions, animations)
- Create `ui/level_complete.py` (summary screen)


---

#### **D2: Theme System & Difficulty Scaling**
**Goal:** Multiple themes with progressive difficulty

**Tasks:**
1. Create multiple fact theme files (cats, bears, vehicles, etc.)
2. Load different theme per level
3. Scale enemy count with progression
4. Increase maze complexity per level
5. Track all collected facts in pause menu
6. Vary enemy behavior distributions by level

**Files:**
- Update `systems/game_state.py` (theme loading, difficulty scaling)
- Update `ui/pause_menu.py` (fact collection display)
- Create all theme JSON files (cats, bears, vehicles, space, etc.)

**Configuration:**
- `config/gameplay.ini`:
  ```ini
  [Progression]
  starting_enemies = 5
  enemy_increase_per_level = 2
  max_enemies_per_level = 15
  ```

**Testing:**
- Different themes load correctly
- Difficulty increases feel balanced
- Facts don't repeat within a level
- Pause menu shows all captured facts


---

#### **D3: Audio & Final Polish**
**Goal:** Sound effects, music, final UX touches

**Tasks:**
1. Add sound effects:
   - Enemy capture
   - Player freeze/glow
   - Level complete
   - Fact display
2. Background music (optional)
3. Final HUD polish
4. Performance optimization
5. Comprehensive testing

**Testing:**
- All sound effects trigger correctly
- Audio doesn't overlap awkwardly
- Performance stays at 60 FPS
- Game is fun and educational!


---

## Testing Protocol

**Per Phase:**
1. Manual testing of all features
2. Unit tests for critical systems (maze generation, collision)
3. Performance profiling (60 FPS target)

**Integration Testing:**
- Play through 3+ levels without crashes
- Verify all enemy behaviors work together
- Test edge cases (rapid captures, maze corners, etc.)

**Playtesting:**
- Kids (target audience) test for difficulty balance
- Adults test for bug discovery

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
