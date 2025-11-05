import pygame
import sys
import configparser
from pathlib import Path
from entities.player import Player
from entities.enemy import Enemy
from systems.maze import Maze
from systems.collision import CollisionManager
from systems.game_state import GameState
from systems.effects import EffectsManager

class ConfigLoader:
    @staticmethod
    def load():
        config = configparser.ConfigParser()
        config_paths = [Path('config/gameplay.ini'), Path('config/enemies.ini')]

        for path in config_paths:
            if not path.exists():
                print(f"Error: Config file not found at {path}")
                sys.exit(1)

        config.read(config_paths)
        return config

class ColorLoader:
    @staticmethod
    def load_from_config(config):
        return {
            'background': ColorLoader._parse_color(config, 'background'),
            'wall': ColorLoader._parse_color(config, 'wall'),
            'floor': ColorLoader._parse_color(config, 'floor'),
            'start': ColorLoader._parse_color(config, 'start_tile'),
            'end': ColorLoader._parse_color(config, 'end_tile')
        }

    @staticmethod
    def _parse_color(config, key):
        return tuple(map(int, config.get('Colors', key).split(',')))

class BrainMaze:
    def __init__(self):
        pygame.init()

        self.config = ConfigLoader.load()
        self._init_display()
        self._init_colors()
        self._init_game_state()
        self._init_maze()
        self._init_sprites()
        self._init_collision_checking()

        self.running = True

    def _init_display(self):
        self.window_width = self.config.getint('Display', 'window_width')
        self.window_height = self.config.getint('Display', 'window_height')
        self.fps = self.config.getint('Display', 'fps')

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.config.get('Display', 'window_title'))
        self.clock = pygame.time.Clock()

    def _init_colors(self):
        colors = ColorLoader.load_from_config(self.config)
        self.bg_color = colors['background']
        self.maze_colors = {
            'floor': colors['floor'],
            'wall': colors['wall'],
            'start': colors['start'],
            'end': colors['end']
        }

    def _init_game_state(self):
        self.game_state = GameState(self.config)
        self.effects_manager = EffectsManager(self.config, (self.window_width, self.window_height))

    def _init_maze(self):
        grid_size = self.config.getint('Maze', 'grid_size')
        tile_size = self.config.getint('Maze', 'tile_size')
        min_wall_length = self.config.getint('Maze', 'min_wall_length')
        max_wall_length = self.config.getint('Maze', 'max_wall_length')
        orientation = self.config.get('Maze', 'orientation')
        max_attempts = self.config.getint('Maze', 'max_generation_attempts')

        self.maze = Maze(grid_size, tile_size, min_wall_length, max_wall_length, orientation, max_attempts)
        self.collision_manager = CollisionManager(self.maze, self.config)

    def _init_sprites(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        start_x, start_y = self.maze.get_start_position()
        self.player = Player(start_x, start_y, self.config, self.collision_manager)
        self.all_sprites.add(self.player)

        end_x, end_y = self.maze.get_end_position()
        enemy = Enemy(end_x, end_y, self.config, self.collision_manager)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def _init_collision_checking(self):
        self.collision_check_interval = self.config.getint('Effects', 'collision_check_interval')
        self.frame_counter = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

    def update(self, dt):
        self.effects_manager.update(dt)
        self.player.update(dt)

        player_tile_pos = self.player.get_tile_position()
        for enemy in self.enemies:
            enemy.update(dt, player_tile_pos)

        self.frame_counter += 1
        if self.frame_counter >= self.collision_check_interval:
            self.frame_counter = 0
            self._check_collisions()

    def _check_collisions(self):
        if not self.player.can_take_damage():
            return

        collided_enemies = pygame.sprite.spritecollide(
            self.player,
            self.enemies,
            False,
            pygame.sprite.collide_rect
        )

        if collided_enemies:
            self.effects_manager.trigger_screen_flash()
            self.player.respawn()
            self.game_state.reset_mines()

    def render(self):
        self.screen.fill(self.bg_color)
        self.maze.render(self.screen, self.maze_colors)
        self.all_sprites.draw(self.screen)
        self.effects_manager.render(self.screen)
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
    game = BrainMaze()
    game.run()

if __name__ == '__main__':
    main()
