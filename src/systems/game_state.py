"""
Game state management system.
Phase A4: Basic mine counter for respawn system (full mine functionality in B1).
"""


class GameState:
    """
    Manages game state including mine inventory and level tracking.
    """

    def __init__(self, config):
        """
        Initialize game state.

        Args:
            config: ConfigParser object with gameplay settings
        """
        self.config = config

        # Mine inventory
        self.max_mines = config.getint('Mines', 'max_inventory')
        self.mine_count = self.max_mines

        # Level tracking (for future phases)
        self.current_level = 1

    def reset_mines(self):
        """Reset mine count to maximum (called on player respawn)."""
        self.mine_count = self.max_mines

    def get_mine_count(self):
        """
        Get current mine count.

        Returns:
            int: Current number of mines
        """
        return self.mine_count

    def add_mine(self):
        """
        Add one mine to inventory (from powerups in future phases).
        Caps at max_mines.
        """
        if self.mine_count < self.max_mines:
            self.mine_count += 1

    def remove_mine(self):
        """
        Remove one mine from inventory.

        Returns:
            bool: True if mine was removed, False if no mines available
        """
        if self.mine_count > 0:
            self.mine_count -= 1
            return True
        return False
