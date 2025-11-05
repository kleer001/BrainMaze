import pygame
from utils.tile_utils import TileUtils

class GridEntity(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y, tile_size):
        super().__init__()
        self.tile_utils = TileUtils(tile_size)
        self.tile_size = tile_size
        self._position_at_tile(tile_x, tile_y)

    def _position_at_tile(self, tile_x, tile_y):
        center_x, center_y = self.tile_utils.tile_to_pixel_center(tile_x, tile_y)
        if hasattr(self, 'rect'):
            self.rect.center = (center_x, center_y)

    def get_tile_position(self):
        if not hasattr(self, 'rect'):
            return (0, 0)
        return self.tile_utils.pixel_to_tile(self.rect.centerx, self.rect.centery)
