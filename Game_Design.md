# Game Design Document: Brain Maze
## Educational Fact Collection Game

---

## 1. Core Concept

**Genre:** Real-time maze navigation, educational puzzle  
**Target Audience:** Children (8-12 years)  
**Core Loop:** Navigate procedural mazes, place thought-mines to capture roaming facts, avoid being caught

**Tagline:** *"Leave your thoughts behind to learn the facts ahead"*

---

## 2. Game Mechanics

### 2.1 Player
- **Sprite:** Brain emoji 🧠
- **Movement:** WASD/Arrow keys, continuous real-time
- **Base Speed:** Equal to fastest enemy type
- **Abilities:**
  - Place mines (M key, 3 in inventory)
  - Collect powerups
  - 5-second invincibility after respawn (visual glow)

### 2.2 Enemies (Facts)
- **Sprite:** Thematic emojis (🐱 for cat level, 🐻 for bear level, etc.)
- **Behavior:** Randomized per individual
- **Attributes:**
  - **Speed:** 1-4 tiles per second (randomized)
  - **Awareness:** Detection radius 2-8 tiles
  - **Aggression:** 0-10 scale (affects chase intensity)
  - **Memory:** 0-3 turns remembering last player position
  - **Pack Behavior:** Boolean (moves toward allies when isolated)
  - **Territoriality:** Boolean (prefers home zone patrol)
  
- **AI Behaviors (modular):**
  - **Wanderer:** Random direction changes
  - **Seeker:** Moves toward player when in detection range
  - **Patrol:** Follows fixed path in territory
  - **Flee:** Moves away from player when detected
  - **Combo:** Switches behavior based on distance/conditions

- **Spawning:**
  - All spawn at level start from "end" point
  - Max 5 on board at once
  - New enemies spawn when count < 5 (minimum 12 tiles from player)
  - **No respawning after elimination**

- **AI Update Rate:** Every 10 frames (~6 updates/second at 60 FPS)

### 2.3 Mines (Thought Mines)
- **Sprite:** 💭 (thought bubble)
- **Inventory:** 3 maximum
- **Placement:** M key, instant drop at current position (brief glow pulse)
- **Trigger:** Enemy collision
- **Effect:** Both enemy and mine removed, mine returns to inventory
- **Special Types (future):**
  - Limited-turn duration
  - Non-returning consumables

### 2.4 Powerups
- **Movement Pattern:** Spawn at "end", pathfind toward "start" using random-weighted corridor choices
- **Collision:** Auto-pickup on player contact
- **Types:**
  
  **Beneficial:**
  - **Speed Boost:** +50% speed, 10 seconds
  - **Extra Mine:** +1 mine inventory (permanent for level)
  - **Shield:** Absorbs 1 hit, visual glow
  
  **Cursed:**
  - **Slowdown:** -30% speed, 10 seconds OR permanent
  - **Mine Loss:** -1 mine inventory (permanent for level)
  
- **Stacking:** Multiple powerups active simultaneously

### 2.5 Maze
- **Algorithm:** Recursive backtracker (single-width corridors)
- **Style:** Pac-Man inspired, guaranteed solvable path
- **Size:** 20×20 tiles (static across levels)
- **Special Locations:**
  - **Start:** Player spawn/respawn point
  - **End:** Enemy spawn point (opposite from start)
- **Progression:**
  - Same size, increasing wall density
  - Same size, increasing enemy count

### 2.6 Collision System
- **Player vs. Enemy:**
  - Screen flash
  - Player respawns at start with 5-second invincibility
  - Mines reset to 3
  - No lives system
  
- **Enemy vs. Mine:**
  - Both removed
  - Fact displayed in trivia panel
  - Mine returns to inventory
  
- **Player vs. Powerup:**
  - Auto-pickup
  - Effect applied immediately

---

## 3. Progression System

### 3.1 Level Structure
- **Theme per Level:** Cats → Bears → Vehicles → Flags → Food → etc.
- **Enemy Count Formula:** `min(15, max(3, 3 + level × 2))`
  - Level 1: 3 enemies
  - Level 2: 5 enemies
  - Level 3: 7 enemies
  - Level 7: 15 enemies (capped)

### 3.2 Win Condition
- Eliminate all enemies on current level
- Brief pause → level complete screen

### 3.3 Level Complete Screen
- Display all collected facts from level
- "Press any key to continue"
- Loads next level with new theme

### 3.4 Difficulty Scaling
- Wall density increases (20% → 40% by level 10)
- Enemy count increases per formula
- Enemy attribute ranges widen (faster speeds, higher aggression at higher levels)

---

## 4. UI/UX

### 4.1 HUD (Top Bar)
- Mines remaining: 💭 × 3
- Current level: "Level 5: Bears"
- Shield status: 🛡️ (when active)

### 4.2 Trivia Panel (Bottom)
- Displays current fact text
- Persists until next fact collected
- Empty when no facts collected yet

### 4.3 Pause Menu (ESC)
- Resume button
- Controls reference
- **All collected facts in current session**

### 4.4 Visual Effects
- **Screen shake:** Enemy collision, mine explosion
- **Particle effects:** Mine placement glow, powerup pickup sparkles
- **Invincibility glow:** Pulsing aura after respawn
- **Shield glow:** Constant aura while active
- **Maze build-in:** Animated transition between levels

### 4.5 Controls
- **WASD / Arrow Keys:** Movement
- **M:** Drop mine
- **ESC:** Pause menu
- **Any Key:** Advance from level complete screen

---

## 5. Content Structure

### 5.1 Fact Database
- JSON files per theme: `/assets/data/cats.json`, `/assets/data/bears.json`
- Structure:
  ```json
  {
    "theme": "cats",
    "emoji": "🐱",
    "facts": [
      "Cats have 32 muscles in each ear!",
      "A group of cats is called a clowder.",
      "Cats spend 70% of their lives sleeping."
    ]
  }
  ```

### 5.2 Themes (Planned)
1. Cats 🐱
2. Bears 🐻
3. Vehicles 🚗
4. Flags 🏁
5. Food 🍕
6. Ocean Animals 🐠
7. Birds 🦅
8. Space ☄️

---

## 6. Technical Specifications

### 6.1 Performance Targets
- 60 FPS constant
- Max 15 enemies + 3 mines + 2 powerups = 20 sprites
- Efficient pathfinding (A* limited to 10 tile lookahead)

### 6.2 Asset Requirements
- Emoji rendering for sprites
- Simple colored tiles for maze (walls, floor, start, end)
- Particle system for effects

### 6.3 Configuration
- INI files in `/config/` directory
- Tunable values:
  - Movement speeds
  - Powerup durations
  - Enemy spawn distances
  - Invincibility duration
  - Enemy count formula parameters

---

## 7. Future Enhancements

### 7.1 Potential Features
- Multiplayer co-op (two brains)
- Boss enemies (mega-facts requiring multiple mines)
- Achievement system
- Custom maze editor
- Daily challenge mode
- Leaderboards (facts collected per minute)

### 7.2 Accessibility
- Colorblind mode (shape coding for powerups)
- Adjustable game speed
- Text-to-speech for facts
- High contrast mode

---

## 8. Design Pillars

1. **Educational First:** Every interaction teaches something
2. **Forgiving:** No permanent failure, respawn system
3. **Strategic Depth:** Mine placement matters more than reflexes
4. **Emergent AI:** Simple rules create complex enemy personalities
5. **Satisfying Feedback:** Every action has clear visual/audio response

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-01
