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
from ui.level_complete import LevelCompleteScreen

class BrainMaze:
    def __init__(self, maze_type=None):
        pygame.init()

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

        self.window_width = self.config.getint('Display', 'window_width')
        self.window_height = self.config.getint('Display', 'window_height')
        self.fps = self.config.getint('Display', 'fps')

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.config.get('Display', 'window_title'))

        self.clock = pygame.time.Clock()

        self.bg_color = self._parse_color('background')
        self.wall_color = self._parse_color('wall')
        self.floor_color = self._parse_color('floor')
        self.start_color = self._parse_color('start_tile')
        self.end_color = self._parse_color('end_tile')

        self.running = True
        self.debug_maze_type = maze_type  # Store for debugging

        data_directory = script_dir.parent / 'assets' / 'data'
        self.fact_loader = FactLoader(str(data_directory))
        self.game_state = GameState(self.config, self.fact_loader)

        self.effects_manager = EffectsManager(self.config, (self.window_width, self.window_height))
        display_duration = self.config.getfloat('Facts', 'display_duration')
        tile_size = self.config.getint('Maze', 'tile_size')
        reserved_height = tile_size * 2
        self.fact_display = FactDisplay((self.window_width, self.window_height), display_duration, reserved_height)
        self.level_complete_screen = LevelCompleteScreen((self.window_width, self.window_height))

        self.collision_check_interval = self.config.getint('Effects', 'collision_check_interval')
        self.frame_counter = 0

        self._initialize_level()

    def _parse_color(self, color_key):
        return tuple(map(int, self.config.get('Colors', color_key).split(',')))

    def _initialize_level(self):
        grid_size = self.config.getint('Maze', 'grid_size')
        min_wall_length = self.config.getint('Maze', 'min_wall_length')
        max_wall_length = self.config.getint('Maze', 'max_wall_length')
        orientation = self.config.get('Maze', 'orientation')
        max_attempts = self.config.getint('Maze', 'max_generation_attempts')
        tile_size = self.config.getint('Maze', 'tile_size')
        border_width = self.config.getint('Maze', 'border_width')

        # Use debug_maze_type if specified, otherwise random
        maze_type = self.debug_maze_type if self.debug_maze_type is not None else random.randint(1, 4)
        generator = self._create_maze_generator(maze_type, min_wall_length, max_wall_length, orientation)
        self.maze = Maze(grid_size, tile_size, min_wall_length, max_wall_length, orientation, max_attempts, generator, border_width)
        self.collision_manager = CollisionManager(self.maze, self.config)

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        start_x, start_y = self.maze.get_start_position()
        self.player = Player(start_x, start_y, self.config, self.collision_manager)
        self.all_sprites.add(self.player)

        self.available_facts = self.fact_loader.load_facts_for_fact_type(self.game_state.current_fact_type).copy()
        random.shuffle(self.available_facts)

        for _ in range(self.game_state.max_enemies_at_once):
            self._spawn_enemy()

    def _create_maze_generator(self, maze_type, min_wall_length, max_wall_length, orientation):
        if maze_type == 1:
            return MazeType1(min_wall_length, max_wall_length, orientation)
        elif maze_type == 2:
            return MazeType2(north_bias=0.5, orientation=orientation)
        elif maze_type == 3:
            return MazeType3(orientation)
        elif maze_type == 4:
            return MazeType4(orientation)
        else:
            return MazeType1(min_wall_length, max_wall_length, orientation)

    def _find_enemy_spawn_position(self):
        grid_size = self.maze.grid_size
        max_attempts = 100

        for _ in range(max_attempts):
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)

            if not self.maze.is_wall(x, y):
                return (x, y)

        return self.maze.get_end_position()

    def _spawn_enemy(self):
        if not self.available_facts:
            return

        emoji = self.fact_loader.get_emoji_for_fact_type(self.game_state.current_fact_type)
        behavior = random.choice(['wanderer', 'patrol'])
        spawn_x, spawn_y = self._find_enemy_spawn_position()
        fact = self.available_facts.pop()

        enemy = Enemy(spawn_x, spawn_y, self.config, self.collision_manager, emoji, behavior, fact)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.level_complete_screen.is_active():
                        if self.game_state.is_game_complete():
                            self.running = False
                        else:
                            self.level_complete_screen.hide()
                            self._initialize_level()

        if not self.level_complete_screen.is_active():
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
    
    def update(self, dt):
        if self.level_complete_screen.is_active():
            return

        self.effects_manager.update(dt)
        self.fact_display.update(dt)
        self.player.update(dt)

        if not self.fact_display.is_active() and not self.player.is_frozen:
            player_tile_pos = self.player.get_tile_position()
            for enemy in self.enemies:
                enemy.update(dt, player_tile_pos)

            self.frame_counter += 1
            if self.frame_counter >= self.collision_check_interval:
                self.frame_counter = 0
                self._check_collisions()

            # Removed respawn logic - enemies are eliminated when hit, not replaced
            # if self.game_state.should_spawn_enemy(len(self.enemies)):
            #     self._spawn_enemy()

            if self.game_state.is_level_complete() and not self.fact_display.is_active():
                facts = self.game_state.advance_level()
                progress_text = self.game_state.get_progress_text()
                is_game_over = self.game_state.is_game_complete()
                self.level_complete_screen.show(facts, progress_text, is_game_over)

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
                    self.game_state.enemy_captured(fact)
                    self.fact_display.show(fact)
                    self.player.freeze()
                    self.effects_manager.trigger_capture_glow(self.player.rect.centerx, self.player.rect.centery)
    
    def render(self):
        if self.level_complete_screen.is_active():
            self.level_complete_screen.render(self.screen)
        else:
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
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()


def main():
    parser = argparse.ArgumentParser(description='BrainMaze - An educational maze game')
    parser.add_argument('-m', '--maze-type', type=int, choices=[1, 2, 3, 4],
                        help='Specify maze type (1-4) for debugging. If not specified, maze type is random.')
    args = parser.parse_args()

    game = BrainMaze(maze_type=args.maze_type)
    game.run()


if __name__ == '__main__':
    main()