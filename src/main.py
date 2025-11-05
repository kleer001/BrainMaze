"""
Brain Maze - Phase A4: Player-Enemy Collision & Respawn System
Educational fact collection game.

Phase A4: Collision triggers respawn with invincibility.
"""

import pygame
import sys
import configparser
from pathlib import Path

# Import entities and systems
from entities.player import Player
from entities.enemy import Enemy
from systems.maze import Maze
from systems.collision import CollisionManager
from systems.game_state import GameState
from systems.effects import EffectsManager

class BrainMaze:
    """
    Main game class managing the game loop and state.
    """
    
    def __init__(self):
        """Initialize game systems."""
        pygame.init()
        
        # Load configuration
        self.config = configparser.ConfigParser()
        config_path = Path('config/gameplay.ini')
        enemies_config_path = Path('config/enemies.ini')

        if not config_path.exists():
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
        if not enemies_config_path.exists():
            print(f"Error: Config file not found at {enemies_config_path}")
            sys.exit(1)

        self.config.read([config_path, enemies_config_path])
        
        # Display setup
        self.window_width = self.config.getint('Display', 'window_width')
        self.window_height = self.config.getint('Display', 'window_height')
        self.fps = self.config.getint('Display', 'fps')
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.config.get('Display', 'window_title'))
        
        self.clock = pygame.time.Clock()
        
        # Load colors
        self.bg_color = tuple(map(int, self.config.get('Colors', 'background').split(',')))
        self.wall_color = tuple(map(int, self.config.get('Colors', 'wall').split(',')))
        self.floor_color = tuple(map(int, self.config.get('Colors', 'floor').split(',')))
        self.start_color = tuple(map(int, self.config.get('Colors', 'start_tile').split(',')))
        self.end_color = tuple(map(int, self.config.get('Colors', 'end_tile').split(',')))

        # Game state
        self.running = True
        self.game_state = GameState(self.config)

        # Effects manager
        self.effects_manager = EffectsManager(self.config, (self.window_width, self.window_height))

        # Collision checking (every N frames for economy)
        self.collision_check_interval = self.config.getint('Effects', 'collision_check_interval')
        self.frame_counter = 0

        # Generate maze
        grid_size = self.config.getint('Maze', 'grid_size')
        tile_size = self.config.getint('Maze', 'tile_size')
        min_wall_length = self.config.getint('Maze', 'min_wall_length')
        max_wall_length = self.config.getint('Maze', 'max_wall_length')
        orientation = self.config.get('Maze', 'orientation')
        max_attempts = self.config.getint('Maze', 'max_generation_attempts')
        self.maze = Maze(grid_size, tile_size, min_wall_length, max_wall_length, orientation, max_attempts)
        # Create collision manager
        self.collision_manager = CollisionManager(self.maze, self.config)

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Create player at maze start position
        start_x, start_y = self.maze.get_start_position()
        self.player = Player(start_x, start_y, self.config, self.collision_manager)
        self.all_sprites.add(self.player)

        # Create enemy at maze end position (Phase A3)
        end_x, end_y = self.maze.get_end_position()
        enemy = Enemy(end_x, end_y, self.config, self.collision_manager)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        
    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Continuous key checking for movement
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
    
    def update(self, dt):
        """
        Update game state.

        Args:
            dt: Delta time in seconds
        """
        # Update effects
        self.effects_manager.update(dt)

        # Update player
        self.player.update(dt)

        # Update enemies (need player position for AI)
        player_tile_pos = self.player.get_tile_position()
        for enemy in self.enemies:
            enemy.update(dt, player_tile_pos)

        # Check collisions every N frames for economy
        self.frame_counter += 1
        if self.frame_counter >= self.collision_check_interval:
            self.frame_counter = 0
            self._check_collisions()

    def _check_collisions(self):
        """Check for player-enemy collisions."""
        # Only check if player can take damage
        if not self.player.can_take_damage():
            return

        # Check collision with any enemy
        collided_enemies = pygame.sprite.spritecollide(
            self.player,
            self.enemies,
            False,  # Don't remove enemies on collision
            pygame.sprite.collide_rect
        )

        if collided_enemies:
            # Trigger screen flash
            self.effects_manager.trigger_screen_flash()

            # Respawn player
            self.player.respawn()

            # Reset mine counter
            self.game_state.reset_mines()
    
    def render(self):
        """Draw everything to screen."""
        # Clear screen
        self.screen.fill(self.bg_color)

        # Draw maze
        colors = {
            'floor': self.floor_color,
            'wall': self.wall_color,
            'start': self.start_color,
            'end': self.end_color
        }
        self.maze.render(self.screen, colors)

        # Draw all sprites
        self.all_sprites.draw(self.screen)

        # Draw effects (screen flash, etc.)
        self.effects_manager.render(self.screen)

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            # Delta time in seconds
            dt = self.clock.tick(self.fps) / 1000.0
            
            # Game loop steps
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = BrainMaze()
    game.run()


if __name__ == '__main__':
    main()