"""
Collision detection system with corner forgiveness.
Phase A2: Wall collision with Pac-Man style corner sliding.
"""

import pygame


class CollisionManager:
    """
    Manages collision detection between entities and maze walls.
    Includes corner forgiveness for smooth player movement.
    """

    def __init__(self, maze, config):
        """
        Initialize collision manager.

        Args:
            maze: Maze instance
            config: ConfigParser object with gameplay settings
        """
        self.maze = maze
        self.tile_size = config.getint('Maze', 'tile_size')
        self.corner_forgiveness = config.getint('Player', 'corner_forgiveness')

    def can_move_to_tile(self, from_tile_x, from_tile_y, to_tile_x, to_tile_y):
        """
        Check if movement from one tile to another is valid.

        Args:
            from_tile_x: Starting tile X
            from_tile_y: Starting tile Y
            to_tile_x: Target tile X
            to_tile_y: Target tile Y

        Returns:
            bool: True if movement is valid (no wall blocking)
        """
        return self.maze.can_move_to(from_tile_x, from_tile_y, to_tile_x, to_tile_y)

    def check_corner_forgiveness(self, pixel_x, pixel_y, direction):
        """
        Check if player can move despite being slightly off-center (corner forgiveness).
        This allows smooth movement around corners like in Pac-Man.

        Args:
            pixel_x: Player's current pixel X position
            pixel_y: Player's current pixel Y position
            direction: 'up', 'down', 'left', or 'right'

        Returns:
            tuple: (can_move: bool, adjusted_x: float, adjusted_y: float)
                   If can_move is True and adjustment is needed, adjusted coordinates are provided.
        """
        # Get current tile position
        tile_x = int(pixel_x // self.tile_size)
        tile_y = int(pixel_y // self.tile_size)

        # Get center of current tile
        tile_center_x = tile_x * self.tile_size + self.tile_size // 2
        tile_center_y = tile_y * self.tile_size + self.tile_size // 2

        # Calculate offset from tile center
        offset_x = pixel_x - tile_center_x
        offset_y = pixel_y - tile_center_y

        # Check if we're within forgiveness threshold
        if direction in ['up', 'down']:
            # For vertical movement, check horizontal offset
            if abs(offset_x) <= self.corner_forgiveness:
                # Close enough to center, allow movement
                # Try to snap to center for smoother movement
                return (True, tile_center_x, pixel_y)

        elif direction in ['left', 'right']:
            # For horizontal movement, check vertical offset
            if abs(offset_y) <= self.corner_forgiveness:
                # Close enough to center, allow movement
                # Try to snap to center for smoother movement
                return (True, pixel_x, tile_center_y)

        # Not within forgiveness threshold
        return (False, pixel_x, pixel_y)

    def get_tile_from_position(self, pixel_x, pixel_y):
        """
        Convert pixel position to tile coordinates.

        Args:
            pixel_x: Pixel X position
            pixel_y: Pixel Y position

        Returns:
            tuple: (tile_x, tile_y)
        """
        tile_x = int(pixel_x // self.tile_size)
        tile_y = int(pixel_y // self.tile_size)
        return (tile_x, tile_y)

    def get_tile_center(self, tile_x, tile_y):
        """
        Get pixel position of tile center.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            tuple: (center_x, center_y) in pixels
        """
        center_x = tile_x * self.tile_size + self.tile_size // 2
        center_y = tile_y * self.tile_size + self.tile_size // 2
        return (center_x, center_y)
