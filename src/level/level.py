from typing import Optional

import pygame
from pytmx.util_pygame import load_pygame

from src import settings
from src.level import Rain
from src.level.soil import SoilLayer
from src.level.transition import DayTransition
from src.overlay import Overlay
from src.player import Player, PlayerInventoryManager
from src.sprites import Generic, Water, LevelSpriteFactory, WildFlower, Tree, Interaction


class Level:
    def __init__(self, player_inventory_manager: PlayerInventoryManager):
        self._player_inventory_manager = player_inventory_manager
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.rain = Rain(self.all_sprites)
        self.raining = True

        self.player: Optional[Player] = None
        self.transition = None
        self.overlay = None
        self._bed = None
        self.soil_layer = SoilLayer(self.all_sprites)
        self.setup()

    def setup(self):
        layers = {
            'HouseFloor': {'layer': 'house bottom', 'class': Generic},
            'HouseFurnitureBottom': {'layer': 'house bottom', 'class': Generic},
            'HouseWalls': {'layer': 'main', 'class': Generic},
            'HouseFurnitureTop': {'layer': 'main', 'class': Generic},
            'Fence': {'layer': 'main', 'class': Generic, 'collision': True},
            'Water': {'layer': 'water', 'class': Water},
            'Decoration': {'type': 'object', 'layer': 'main', 'class': WildFlower, 'collision': True},
            'Trees': {'type': 'object', 'layer': 'main', 'class': Tree, 'collision': True},
            'Collision': {'layer': 'main', 'class': Generic, 'collision': True, 'collision_only': True},
        }

        tmx_data = load_pygame('../data/map.tmx')

        for tmx_layer, layer_info in layers.items():
            sprite_group = []
            if not layer_info.get('collision_only'):
                sprite_group.append(self.all_sprites)
            if layer_info.get('collision'):
                sprite_group.append(self.collision_sprites)
            if layer_info.get('type') == 'object':
                for obj in tmx_data.get_layer_by_name(tmx_layer):
                    sprite = LevelSpriteFactory.create(layer_info.get('class'),
                                                       obj.x,
                                                       obj.y,
                                                       obj.image,
                                                       sprite_group,
                                                       settings.LAYERS[layer_info.get('layer')],
                                                       name=obj.name,
                                                       player_inventory_manager=self._player_inventory_manager)

                    if tmx_layer == 'Trees':
                        self.tree_sprites.add(sprite)
            else:
                for x, y, surface in tmx_data.get_layer_by_name(tmx_layer).tiles():
                    LevelSpriteFactory.create(layer_info.get('class'), x, y, surface, sprite_group,
                                              settings.LAYERS[layer_info.get('layer')], )

        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    all_sprites=self.all_sprites,
                    collision_group=self.collision_sprites,
                    interaction_group=self.interaction_sprites,
                    trees_group=self.tree_sprites,
                    soil_layer=self.soil_layer)
                self._player_inventory_manager.add_player(self.player)
            elif obj.name == 'Bed':
                self._bed = Interaction((obj.x, obj.y),
                                        (obj.width, obj.height),
                                        groups=(self.interaction_sprites,),
                                        name='Bed',
                                        transition=DayTransition(self.reset, self.player))
                self.interaction_sprites.add(self._bed)
        self.overlay = Overlay(self.player)

        ground = Generic(pos=(0, 0),
                         surface=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
                         groups=(self.all_sprites,),
                         z=settings.LAYERS['ground'])
        ground.hitbox = None

    def reset(self):
        tree: Tree
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        self.soil_layer.remove_water()

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        if self.raining:
            self.rain.update()

        self.overlay.display()

        if self.player.sleep:
            self._bed.transition.update()


class CameraGroup(pygame.sprite.Group):

    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - settings.SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - settings.SCREEN_HEIGHT / 2
        for layer in settings.LAYERS.values():
            sprite: Generic
            for sprite in sorted(self.sprites(), key=lambda _sprite: _sprite.rect.centery):
                if sprite.z == layer:
                    sprite_offset_rect = sprite.rect.copy()
                    sprite_offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, sprite_offset_rect)

                    if settings.DEBUG:
                        # print collision boxes
                        if getattr(sprite, 'hitbox', None) is not None:
                            pygame.draw.rect(self.display_surface, 'red', sprite_offset_rect, 5)
                            hitbox_rect = sprite.hitbox.copy()
                            hitbox_rect.center = sprite_offset_rect.center
                            pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)

                        if sprite == player:
                            pygame.draw.rect(self.display_surface, 'red', sprite_offset_rect, 5)
                            hitbox_rect = player.hitbox.copy()
                            hitbox_rect.center = sprite_offset_rect.center
                            pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                            target_pos = sprite_offset_rect.center + settings.PLAYER_TOOL_OFFSET[
                                player.status.split("_")[0]]
                            pygame.draw.circle(self.display_surface, 'blue', target_pos, 2)
