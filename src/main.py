"""
Brain Maze - Phase A1: Player Movement
Educational fact collection game.

Phase A1: Player moves smoothly in empty space with buffered input.
"""

import pygame
import sys
import configparser
from pathlib import Path

# Import player entity
from entities.player import Player


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
        
        # Game state
        self.running = True
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        
        # Create player at start position (center of grid for now)
        grid_size = self.config.getint('Maze', 'grid_size')
        start_x = grid_size // 2
        start_y = grid_size // 2
        self.player = Player(start_x, start_y, self.config)
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
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Optional: Draw grid lines for development
        self._draw_grid()
        
        # Update display
        pygame.display.flip()
    
    def _draw_grid(self):
        """Draw grid lines for visual reference (development only)."""
        tile_size = self.config.getint('Maze', 'tile_size')
        grid_size = self.config.getint('Maze', 'grid_size')
        grid_color = (50, 50, 60)  # Subtle grid lines
        
        # Vertical lines
        for x in range(grid_size + 1):
            px = x * tile_size
            pygame.draw.line(self.screen, grid_color, (px, 0), (px, self.window_height), 1)
        
        # Horizontal lines
        for y in range(grid_size + 1):
            py = y * tile_size
            pygame.draw.line(self.screen, grid_color, (0, py), (self.window_width, py), 1)
    
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