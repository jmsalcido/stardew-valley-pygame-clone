import sys
import pygame

from src.level import Level
from src.player import PlayerInventoryManager
from src.settings import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Pydew Valley')
        self.clock = pygame.time.Clock()
        self._player_inventory_manager = PlayerInventoryManager()
        self.level = Level(self._player_inventory_manager)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000
            self.level.run(dt)
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
