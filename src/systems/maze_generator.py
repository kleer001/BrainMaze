from abc import ABC, abstractmethod


class MazeGenerator(ABC):
    @abstractmethod
    def generate(self, grid_size):
        pass
