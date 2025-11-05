import random
import pygame
from collections import deque

WALL = 1
PATH = 0


class Maze:
    def __init__(self, grid_size, tile_size, min_wall_length=1, max_wall_length=5, 
                 orientation='vertical', max_attempts=100):
        self.grid_size = grid_size
        self.tile_size = tile_size
        self.min_wall_length = min_wall_length
        self.max_wall_length = max_wall_length
        self.orientation = orientation
        self.max_attempts = max_attempts
        self.grid = []
        self.start_pos = None
        self.end_pos = None
        self._generate()

    def _generate(self):
        for _ in range(self.max_attempts):
            self.grid = [[PATH] * self.grid_size for _ in range(self.grid_size)]
            self._scatter_walls()
            self._find_start_end_positions()
            
            if self._is_connected(self.start_pos, self.end_pos) and self._is_fully_traversable():
                return
        
        self.grid = [[PATH] * self.grid_size for _ in range(self.grid_size)]
        self._find_start_end_positions()

    def _scatter_walls(self):
        is_vertical = self.orientation == 'vertical'
        half_size = self.grid_size // 2 + 1
        
        for line in range(1, half_size, 2):
            self._fill_line(line, is_vertical)
        
        self._mirror(half_size, is_vertical)

    def _fill_line(self, line, is_vertical):
        position = 0
        start_with_path = random.choice([True, False])
        
        while position < self.grid_size:
            if start_with_path:
                position = self._place_segment(line, position, PATH, 1, is_vertical)
                position = self._place_segment(line, position, WALL, 
                                              self._random_wall_length(), is_vertical)
            else:
                position = self._place_segment(line, position, WALL, 
                                              self._random_wall_length(), is_vertical)
                position = self._place_segment(line, position, PATH, 1, is_vertical)

    def _place_segment(self, line, start, cell_type, length, is_vertical):
        for i in range(length):
            if start + i >= self.grid_size:
                break
            x, y = (line, start + i) if is_vertical else (start + i, line)
            self.grid[y][x] = cell_type
        return start + length

    def _random_wall_length(self):
        return random.randint(self.min_wall_length, self.max_wall_length)

    def _mirror(self, half_size, is_vertical):
        for i in range(half_size):
            mirror_i = self.grid_size - 1 - i
            for j in range(self.grid_size):
                if is_vertical:
                    self.grid[j][mirror_i] = self.grid[j][i]
                else:
                    self.grid[mirror_i][j] = self.grid[i][j]

    def _is_connected(self, start, end):
        if start == end:
            return True
        
        visited = {start}
        queue = deque([start])
        
        while queue:
            x, y = queue.popleft()
            
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) == end:
                    return True
                if self._is_valid_path(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return False

    def _is_fully_traversable(self):
        if not self.start_pos:
            return False
        
        total_paths = sum(1 for row in self.grid for cell in row if cell == PATH)
        
        visited = {self.start_pos}
        queue = deque([self.start_pos])
        
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if self._is_valid_path(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return len(visited) == total_paths

    def _is_valid_path(self, x, y):
        return (0 <= x < self.grid_size and 
                0 <= y < self.grid_size and 
                not self.is_wall(x, y))

    def _find_start_end_positions(self):
        corner_pairs = [
            ((1, 1), (self.grid_size - 2, self.grid_size - 2)),
            ((self.grid_size - 2, 1), (1, self.grid_size - 2))
        ]
        start_corner, end_corner = random.choice(corner_pairs)
        
        self.start_pos = self._find_path_near(start_corner) or (1, 1)
        self.end_pos = self._find_path_near(end_corner) or (self.grid_size - 2, self.grid_size - 2)

    def _find_path_near(self, corner):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                x, y = corner[0] + dx, corner[1] + dy
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size and not self.is_wall(x, y):
                    return (x, y)
        return None

    def get_start_position(self):
        return self.start_pos

    def get_end_position(self):
        return self.end_pos

    def is_wall(self, x, y):
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return True
        return self.grid[y][x] == WALL

    def can_move_to(self, from_x, from_y, to_x, to_y):
        return not self.is_wall(to_x, to_y)

    def render(self, surface, colors):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                  self.tile_size, self.tile_size)
                
                if self.grid[y][x] == WALL:
                    color = colors['wall']
                elif (x, y) == self.start_pos:
                    color = colors['start']
                elif (x, y) == self.end_pos:
                    color = colors['end']
                else:
                    color = colors['floor']
                
                pygame.draw.rect(surface, color, rect)