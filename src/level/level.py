import pygame
from pytmx.util_pygame import load_pygame

from src import settings
from src.overlay import Overlay
from src.player import Player
from src.sprites import Generic, Water, LevelSpriteFactory, WildFlower


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.setup()

    def setup(self):
        layers = {
            'HouseFloor': {'layer': 'house bottom', 'class': Generic},
            'HouseFurnitureBottom': {'layer': 'house bottom', 'class': Generic},
            'HouseWalls': {'layer': 'main', 'class': Generic},
            'HouseFurnitureTop': {'layer': 'main', 'class': Generic},
            'Fence': {'layer': 'main', 'class': Generic},
            'Water': {'layer': 'water', 'class': Water},
            'Decoration': {'type': 'object', 'layer': 'main', 'class': WildFlower},
            'Trees': {'type': 'object', 'layer': 'main', 'class': WildFlower},
        }

        tmx_data = load_pygame('../data/map.tmx')

        for tmx_layer, layer_info in layers.items():
            if layer_info.get('type') == 'object':
                for obj in tmx_data.get_layer_by_name(tmx_layer):
                    LevelSpriteFactory.create(layer_info.get('class'), obj.x, obj.y, obj.image, (self.all_sprites,),
                                              settings.LAYERS[layer_info.get('layer')], name=obj.name)
            else:
                for x, y, surface in tmx_data.get_layer_by_name(tmx_layer).tiles():
                    LevelSpriteFactory.create(layer_info.get('class'), x, y, surface, (self.all_sprites,),
                                              settings.LAYERS[layer_info.get('layer')])

        self.player = Player((640, 360), self.all_sprites)
        self.overlay = Overlay(self.player)

        Generic(pos=(0, 0),
                surface=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
                groups=(self.all_sprites,),
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
            for sprite in sorted(self.sprites(), key=lambda _sprite: _sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
