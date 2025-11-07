import random


class GameState:
    def __init__(self, config, fact_loader):
        self.config = config
        self.fact_loader = fact_loader

        self.max_mines = config.getint('Mines', 'max_inventory')
        self.mine_count = self.max_mines

        self.current_level = 1
        self.enemies_captured_this_level = 0
        self.max_enemies_per_level = 3
        self.max_enemies_at_once = 3
        self.captured_facts = []

        self.fact_types = self.fact_loader.get_available_fact_types()
        self.fact_type_queue = []
        self.current_fact_type = self._next_fact_type()

        self.total_facts_captured = 0
        self.total_facts_available = self._count_total_facts()

    def _count_total_facts(self):
        total = 0
        for fact_type in self.fact_types:
            facts = self.fact_loader.load_facts_for_fact_type(fact_type)
            total += len(facts)
        return total

    def _next_fact_type(self):
        if not self.fact_type_queue:
            self.fact_type_queue = self.fact_types.copy()
            random.shuffle(self.fact_type_queue)
        return self.fact_type_queue.pop(0)

    def enemy_captured(self, fact):
        self.enemies_captured_this_level += 1
        self.total_facts_captured += 1
        if fact:
            self.captured_facts.append(fact)

    def should_spawn_enemy(self, current_enemy_count):
        return (current_enemy_count < self.max_enemies_at_once and
                self.enemies_captured_this_level < self.max_enemies_per_level)

    def is_level_complete(self):
        return self.enemies_captured_this_level >= self.max_enemies_per_level

    def is_game_complete(self):
        return self.total_facts_captured >= self.total_facts_available

    def get_progress_text(self):
        return f"{self.total_facts_captured}/{self.total_facts_available}"

    def advance_level(self):
        self.current_level += 1
        self.enemies_captured_this_level = 0
        facts_to_display = self.captured_facts.copy()
        self.captured_facts = []
        self.current_fact_type = self._next_fact_type()
        return facts_to_display

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
