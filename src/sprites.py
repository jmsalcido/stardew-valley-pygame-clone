import pygame

from src import settings


class Generic(pygame.sprite.Sprite):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main']) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
