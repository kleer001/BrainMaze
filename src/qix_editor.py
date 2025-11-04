"""
Qix Level Parameter Editor - Tune generation parameters interactively.
Generates mazes procedurally with live parameter adjustment.
"""

import pygame
import configparser
import os
from systems.qix_maze import QixMazeGenerator, WALL, CORRIDOR, CHAMBER


class ParameterEditor:
    """Interactive parameter editor for Qix maze generation."""

    def __init__(self, config_path='config/qix_config.ini'):
        """Initialize editor with config file."""
        pygame.init()

        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.config_path = config_path

        # Display
        self.window_width = self.config.getint('Display', 'window_width')
        self.window_height = self.config.getint('Display', 'window_height')
        self.fps = self.config.getint('Display', 'fps')

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.config.get('Display', 'title'))
        self.clock = pygame.time.Clock()

        # Colors
        self.colors = {
            'background': tuple(map(int, self.config.get('Colors', 'background').split(','))),
            'wall': tuple(map(int, self.config.get('Colors', 'wall').split(','))),
            'corridor': tuple(map(int, self.config.get('Colors', 'corridor').split(','))),
            'chamber': tuple(map(int, self.config.get('Colors', 'chamber').split(','))),
            'start': tuple(map(int, self.config.get('Colors', 'start_tile').split(','))),
            'end': tuple(map(int, self.config.get('Colors', 'end_tile').split(','))),
            'grid': tuple(map(int, self.config.get('Colors', 'grid_lines').split(','))),
        }

        # Grid
        self.grid_width = self.config.getint('Grid', 'width')
        self.grid_height = self.config.getint('Grid', 'height')
        self.tile_size = self.config.getint('Grid', 'tile_size')
        self.maze_width = self.grid_width * self.tile_size
        self.maze_height = self.grid_height * self.tile_size

        # Editable parameters: (type, value, min, max, step)
        self.parameters = {
            'fill_target': ('float', self.config.getfloat('Generation', 'fill_target'), 0.5, 0.95, 0.05),
            'chamber_min_size': ('int', self.config.getint('Generation', 'chamber_min_size'), 3, 7, 1),
            'chamber_max_size': ('int', self.config.getint('Generation', 'chamber_max_size'), 4, 9, 1),
            'corridor_length_min': ('int', self.config.getint('Generation', 'corridor_length_min'), 2, 6, 1),
            'corridor_length_max': ('int', self.config.getint('Generation', 'corridor_length_max'), 6, 15, 1),
        }

        self.param_keys = list(self.parameters.keys())
        self.selected_param = 0
        self.editing = False

        # Maze state
        self.grid = None
        self.start_pos = None
        self.end_pos = None
        self.last_generated = None
        self.generation_count = 0

        # Fonts
        self.font_large = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 14)

        self.running = True
        self.regenerate_maze()

    def regenerate_maze(self):
        """Generate new maze with current parameters."""
        # Update config
        for key, (ptype, val, _, _, _) in self.parameters.items():
            self.config.set('Generation', key, str(val))

        # Generate
        generator = QixMazeGenerator(self.grid_width, self.grid_height, self.config)
        if generator.generate():
            self.grid = generator.get_grid()
            self.start_pos = generator.get_start_pos()
            self.end_pos = generator.get_end_pos()
            self.generation_count += 1
            self.last_generated = f"Generated #{self.generation_count}"

    def handle_events(self):
        """Handle input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.selected_param = (self.selected_param - 1) % len(self.param_keys)
                elif event.key == pygame.K_DOWN:
                    self.selected_param = (self.selected_param + 1) % len(self.param_keys)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                    self.editing = not self.editing
                elif event.key == pygame.K_LEFT and self.editing:
                    self._adjust_param(-1)
                elif event.key == pygame.K_RIGHT and self.editing:
                    self._adjust_param(1)
                elif event.key == pygame.K_SPACE:
                    self.regenerate_maze()
                elif event.key == pygame.K_s:
                    self._save_config()

    def _adjust_param(self, delta):
        """Adjust selected parameter."""
        key = self.param_keys[self.selected_param]
        ptype, val, min_val, max_val, step = self.parameters[key]

        new_val = val + (delta * step)
        new_val = max(min_val, min(max_val, new_val))

        if ptype == 'int':
            new_val = int(new_val)

        self.parameters[key] = (ptype, new_val, min_val, max_val, step)
        self.regenerate_maze()

    def _save_config(self):
        """Save parameters back to INI."""
        for key, (ptype, val, _, _, _) in self.parameters.items():
            self.config.set('Generation', key, str(val))

        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
        self.last_generated = f"✓ Saved to {self.config_path}"

    def render(self):
        """Render everything."""
        self.screen.fill(self.colors['background'])

        if self.grid:
            self._render_maze()

        self._render_ui_panel()
        pygame.display.flip()

    def _render_maze(self):
        """Render maze grid."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)

                if (x, y) == self.start_pos:
                    color = self.colors['start']
                elif (x, y) == self.end_pos:
                    color = self.colors['end']
                elif self.grid[y][x] == WALL:
                    color = self.colors['wall']
                elif self.grid[y][x] == CHAMBER:
                    color = self.colors['chamber']
                else:
                    color = self.colors['corridor']

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.colors['grid'], rect, 1)

    def _render_ui_panel(self):
        """Render parameter panel."""
        panel_y = self.maze_height + 10

        # Title
        title = self.font_large.render("Qix Level Parameter Editor", True, (200, 200, 200))
        self.screen.blit(title, (10, panel_y))

        # Status
        if self.last_generated:
            status = self.font_small.render(self.last_generated, True, (100, 200, 100))
        else:
            status = self.font_small.render("Ready", True, (150, 150, 150))
        self.screen.blit(status, (10, panel_y + 30))

        # Parameters
        y_offset = panel_y + 55
        for i, key in enumerate(self.param_keys):
            ptype, val, min_val, max_val, step = self.parameters[key]

            is_selected = (i == self.selected_param)
            color = (255, 255, 100) if is_selected else (150, 150, 150)
            editing_marker = " [EDIT]" if is_selected and self.editing else ""

            if ptype == 'float':
                text = f"{key}: {val:.2f}  (min: {min_val}, max: {max_val}){editing_marker}"
            else:
                text = f"{key}: {int(val)}  (min: {min_val}, max: {max_val}){editing_marker}"

            rendered = self.font_small.render(text, True, color)
            self.screen.blit(rendered, (10, y_offset))
            y_offset += 25

        # Controls
        y_offset += 10
        controls = [
            "UP/DOWN: Select  |  ENTER: Edit  |  LEFT/RIGHT: Adjust",
            "SPACE: Regenerate  |  S: Save Config  |  ESC: Quit"
        ]

        for control in controls:
            text = self.font_tiny.render(control, True, (150, 150, 200))
            self.screen.blit(text, (10, y_offset))
            y_offset += 18

    def run(self):
        """Main loop."""
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(self.fps)

        pygame.quit()


def main():
    """Entry point."""
    editor = ParameterEditor('config/qix_config.ini')
    editor.run()


if __name__ == '__main__':
    main()