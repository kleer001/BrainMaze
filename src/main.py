"""
Brain Maze - Phase A2: Maze Generation & Wall Collision
Educational fact collection game.

Phase A2: Player navigates procedurally generated maze with wall collision.
"""

import pygame
import sys
import configparser
from pathlib import Path

# Import entities and systems
from entities.player import Player
from systems.maze import Maze
from systems.collision import CollisionManager


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
        if not config_path.exists():
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
        self.config.read(config_path)
        
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

        # Generate maze
        grid_size = self.config.getint('Maze', 'grid_size')
        tile_size = self.config.getint('Maze', 'tile_size')
        self.maze = Maze(grid_size, tile_size)

        # Create collision manager
        self.collision_manager = CollisionManager(self.maze, self.config)

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()

        # Create player at maze start position
        start_x, start_y = self.maze.get_start_position()
        self.player = Player(start_x, start_y, self.config, self.collision_manager)
        self.all_sprites.add(self.player)
        
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
        self.all_sprites.update(dt)
    
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