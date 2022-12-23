import pygame

from src import settings
from src.overlay import Overlay
from src.player import Player
from src.sprites import Generic


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.setup()

    def setup(self):
        self.player = Player((640, 360), self.all_sprites)
        self.overlay = Overlay(self.player)
        Generic(pos=(0, 0),
                surface=pygame.image.load(f'../graphics/world/ground.png').convert_alpha(),
                groups=self.all_sprites,
                z=settings.LAYERS['ground'])

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        self.overlay.display()


class CameraGroup(pygame.sprite.Group):

    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - settings.SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - settings.SCREEN_HEIGHT / 2
        for layer in settings.LAYERS.values():
            for sprite in self.sprites():
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
