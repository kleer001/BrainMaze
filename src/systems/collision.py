import pygame
from utils.tile_utils import TileUtils
from utils.direction import UP, DOWN, LEFT, RIGHT

class CollisionManager:
    def __init__(self, maze, config):
        self.maze = maze
        self.tile_size = config.getint('Maze', 'tile_size')
        self.corner_forgiveness = config.getint('Player', 'corner_forgiveness')
        self.tile_utils = TileUtils(self.tile_size)

    def can_move_to_tile(self, from_tile_x, from_tile_y, to_tile_x, to_tile_y):
        return self.maze.can_move_to(from_tile_x, from_tile_y, to_tile_x, to_tile_y)

    def check_corner_forgiveness(self, pixel_x, pixel_y, direction):
        tile_x, tile_y = self.tile_utils.pixel_to_tile(pixel_x, pixel_y)
        tile_center_x, tile_center_y = self.tile_utils.tile_to_pixel_center(tile_x, tile_y)
        offset_x, offset_y = self.tile_utils.get_tile_offset_from_center(pixel_x, pixel_y)

        if direction in [UP, DOWN]:
            if abs(offset_x) <= self.corner_forgiveness:
                return (True, tile_center_x, pixel_y)
        elif direction in [LEFT, RIGHT]:
            if abs(offset_y) <= self.corner_forgiveness:
                return (True, pixel_x, tile_center_y)

        return (False, pixel_x, pixel_y)

    def get_tile_from_position(self, pixel_x, pixel_y):
        return self.tile_utils.pixel_to_tile(pixel_x, pixel_y)

    def get_tile_center(self, tile_x, tile_y):
        return self.tile_utils.tile_to_pixel_center(tile_x, tile_y)
