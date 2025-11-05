class TileUtils:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.half_tile = tile_size // 2

    def pixel_to_tile(self, pixel_x, pixel_y):
        return int(pixel_x // self.tile_size), int(pixel_y // self.tile_size)

    def tile_to_pixel_center(self, tile_x, tile_y):
        return (
            tile_x * self.tile_size + self.half_tile,
            tile_y * self.tile_size + self.half_tile
        )

    def get_tile_offset_from_center(self, pixel_x, pixel_y):
        tile_x, tile_y = self.pixel_to_tile(pixel_x, pixel_y)
        center_x, center_y = self.tile_to_pixel_center(tile_x, tile_y)
        return pixel_x - center_x, pixel_y - center_y
