class GameState:
    def __init__(self, config):
        self.config = config
        self.max_mines = config.getint('Mines', 'max_inventory')
        self.mine_count = self.max_mines
        self.current_level = 1

    def reset_mines(self):
        self.mine_count = self.max_mines

    def get_mine_count(self):
        return self.mine_count

    def add_mine(self):
        if self.mine_count < self.max_mines:
            self.mine_count += 1

    def remove_mine(self):
        if self.mine_count > 0:
            self.mine_count -= 1
            return True
        return False
