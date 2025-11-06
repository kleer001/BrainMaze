import pygame
import sys
import random
import configparser
import argparse
from pathlib import Path

from entities.player import Player
from entities.enemy import Enemy
from systems.maze import Maze
from systems.collision import CollisionManager
from systems.game_state import GameState
from systems.effects import EffectsManager
from systems.maze_type_1 import MazeType1
from systems.maze_type_2 import MazeType2
from systems.maze_type_3 import MazeType3
from systems.maze_type_4 import MazeType4
from systems.fact_loader import FactLoader
from ui.fact_display import FactDisplay

class BrainMaze:
    """
    Main game class managing the game loop and state.
    """
    
    def __init__(self, maze_type=1):
        """Initialize game systems.

        Args:
            maze_type: Integer specifying which maze generation algorithm to use (1-4)
        """
        pygame.init()
        
        # Load configuration
        self.config = configparser.ConfigParser()
        script_dir = Path(__file__).parent
        config_path = script_dir / 'config' / 'gameplay.ini'
        enemies_config_path = script_dir / 'config' / 'enemies.ini'

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

        # Fact display system
        script_dir = Path(__file__).parent
        data_directory = script_dir.parent / 'assets' / 'data'
        self.fact_loader = FactLoader(str(data_directory))
        display_duration = self.config.getfloat('Facts', 'display_duration')
        tile_size = self.config.getint('Maze', 'tile_size')
        reserved_height = tile_size * 2
        self.fact_display = FactDisplay((self.window_width, self.window_height), display_duration, reserved_height)

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

        # Create maze generator based on type
        generator = self._create_maze_generator(maze_type, min_wall_length, max_wall_length, orientation)
        self.maze = Maze(grid_size, tile_size, min_wall_length, max_wall_length, orientation, max_attempts, generator)
        # Create collision manager
        self.collision_manager = CollisionManager(self.maze, self.config)

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Create player at maze start position
        start_x, start_y = self.maze.get_start_position()
        self.player = Player(start_x, start_y, self.config, self.collision_manager)
        self.all_sprites.add(self.player)

        facts = self.fact_loader.load_theme('cats')

        enemy_configs = [
            ("🐱", "wanderer"),
            ("🐶", "wanderer"),
            ("🐭", "patrol"),
            ("🧀", "patrol")
        ]

        for index, (emoji, behavior) in enumerate(enemy_configs):
            spawn_x, spawn_y = self._find_enemy_spawn_position()
            fact = facts[index % len(facts)] if facts else ""
            enemy = Enemy(spawn_x, spawn_y, self.config, self.collision_manager, emoji, behavior, fact)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def _create_maze_generator(self, maze_type, min_wall_length, max_wall_length, orientation):
        """
        Create the appropriate maze generator based on type.

        Args:
            maze_type: Integer 1-4 specifying which algorithm to use
            min_wall_length: Minimum wall length for type 1
            max_wall_length: Maximum wall length for type 1
            orientation: 'vertical' or 'horizontal' for mirroring direction

        Returns:
            MazeGenerator instance
        """
        if maze_type == 1:
            return MazeType1(min_wall_length, max_wall_length, orientation)
        elif maze_type == 2:
            # Binary tree with default NW bias and mirroring
            return MazeType2(north_bias=0.5, orientation=orientation)
        elif maze_type == 3:
            # Recursive backtracking with mirroring
            return MazeType3(orientation)
        elif maze_type == 4:
            # Sidewinder with mirroring
            return MazeType4(orientation)
        else:
            print(f"Warning: Unknown maze type {maze_type}, defaulting to type 1")
            return MazeType1(min_wall_length, max_wall_length, orientation)

    def _find_enemy_spawn_position(self):
        """
        Find a random valid spawn position for an enemy.

        Returns:
            Tuple of (x, y) tile coordinates
        """
        grid_size = self.maze.grid_size
        max_attempts = 100

        for _ in range(max_attempts):
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)

            # Check if position is walkable
            if not self.maze.is_wall(x, y):
                return (x, y)

        # Fallback to end position if no valid position found
        return self.maze.get_end_position()

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
        self.effects_manager.update(dt)
        self.fact_display.update(dt)

        if not self.fact_display.is_active():
            self.player.update(dt)

            player_tile_pos = self.player.get_tile_position()
            for enemy in self.enemies:
                enemy.update(dt, player_tile_pos)

            self.frame_counter += 1
            if self.frame_counter >= self.collision_check_interval:
                self.frame_counter = 0
                self._check_collisions()

    def _check_collisions(self):
        collided_enemies = pygame.sprite.spritecollide(
            self.player,
            self.enemies,
            False,
            pygame.sprite.collide_rect
        )

        for enemy in collided_enemies:
            if not enemy.is_dying:
                enemy_type, fact = enemy.die()
                if fact:
                    self.fact_display.show(fact)
    
    def render(self):
        self.screen.fill(self.bg_color)

        colors = {
            'floor': self.floor_color,
            'wall': self.wall_color,
            'start': self.start_color,
            'end': self.end_color
        }
        self.maze.render(self.screen, colors)

        self.all_sprites.draw(self.screen)
        self.effects_manager.render(self.screen)
        self.fact_display.render(self.screen)

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
    parser = argparse.ArgumentParser(description='Brain Maze - Educational fact collection game')
    parser.add_argument(
        '--maze-type', '-m',
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        help='Maze generation algorithm: 1=Scattered walls, 2=Binary tree, 3=Recursive backtracking, 4=Sidewinder'
    )
    args = parser.parse_args()

    game = BrainMaze(maze_type=args.maze_type)
    game.run()


if __name__ == '__main__':
    main()