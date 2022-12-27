import pygame.display

from src import settings
from src.player import Player
from src.timer import Timer


class DayTransition:
    def __init__(self, reset, player: Player) -> None:
        super().__init__()
        self._display_surface = pygame.display.get_surface()
        self._player = player
        self._reset = reset
        self._timer = Timer(2000, self.stop)

        self._image = None
        self._color = 255
        self._speed = 0

    def start(self):
        self._image = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self._color = 255
        self._speed = -1
        self._timer.activate()

    def stop(self):
        self._reset()
        self._player.sleep = False

    def update(self):
        self._timer.update()
        self._color += self._speed
        if self._color <= 0:
            self._color = 0
            self._speed *= -1
        if self._color >= 255:
            self._color = 255
            self._speed = -1
        self._image.fill((self._color, self._color, self._color))
        self._display_surface.blit(self._image, (0, 0))
