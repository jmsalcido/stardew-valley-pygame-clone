from enum import Enum
from random import randint, choice

import pygame

from src import settings
from src.player import PlayerInventoryManager
from src.support import game_tile_pos_tuple, import_folder
from src.timer import Timer


class Generic(pygame.sprite.Sprite):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main']) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


class WildFlower(Generic):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main']) -> None:
        super().__init__(pos, surface, groups, z)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main'], duration=200) -> None:
        super().__init__(pos, surface, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask_surface = pygame.mask.from_surface(self.image)
        new_surface = mask_surface.to_surface()
        new_surface.set_colorkey((0, 0, 0))
        self.image = new_surface

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class TreeType(Enum):
    SMALL = 0,
    LARGE = 1


class Tree(Generic):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main'], name=None,
                 player_inventory_manager=None) -> None:
        super().__init__(pos, surface, groups, z)
        self.all_sprites = self.groups()[0]
        self.health = 5
        self.alive = True

        self.name = name

        self.apples_surface = pygame.image.load('../graphics/fruit/apple.png')
        self.apple_pos = settings.APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self._tree_type: TreeType = TreeType.SMALL if name == 'Small' else TreeType.LARGE
        stump_path = f'../graphics/stumps/{"small.png" if self._tree_type == TreeType.SMALL else "large.png"}'
        self.stump_surface = pygame.image.load(stump_path)
        self.invul_timer = Timer(200)

        self._player_inventory_manager: PlayerInventoryManager = player_inventory_manager

    def damage(self):
        self.health -= 1

        apple_sprites = self.apple_sprites.sprites()
        if len(apple_sprites) > 0:
            random_apple = choice(apple_sprites)
            Particle(random_apple.rect.topleft, random_apple.image, (self.all_sprites,), z=settings.LAYERS['fruit'])
            random_apple.kill()
            self._player_inventory_manager.add_to_inventory('apple')

    def check_health(self):
        if self.health <= 0:
            if self._tree_type == TreeType.SMALL:
                self._player_inventory_manager.add_to_inventory('wood', 3)
            elif self._tree_type == TreeType.LARGE:
                self._player_inventory_manager.add_to_inventory('wood', 5)
            self.alive = False
            Particle(self.rect.topleft, self.image, (self.all_sprites,), z=settings.LAYERS['fruit'], duration=300)
            self.image = self.stump_surface
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic(pos=(x, y), surface=self.apples_surface, groups=(self.apple_sprites, self.groups()[0],),
                        z=settings.LAYERS['fruit'])

    def update(self, dt):
        if self.alive:
            self.check_health()


class Water(Generic):

    def __init__(self, pos, frames, groups, z=settings.LAYERS['water']) -> None:
        self.frames = frames
        self.frame_index = 0
        surface = self.frames[self.frame_index] if self.frames is not None else None
        super().__init__(pos=pos, surface=surface, groups=groups, z=z)

    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class LevelSpriteFactory:
    @staticmethod
    def create(clazz, x, y, surface, groups, z, **kwargs):
        if clazz == Water:
            water_frames = import_folder('../graphics/water')
            return Water(game_tile_pos_tuple(x, y), water_frames, groups=groups, z=z)
        elif clazz == Generic:
            return Generic(game_tile_pos_tuple(x, y), surface, groups=groups, z=z)
        elif clazz == WildFlower:
            return WildFlower((x, y), surface, groups=groups, z=z)
        elif clazz == Tree:
            return Tree((x, y), surface, groups=groups, z=z, **kwargs)
        else:
            raise Exception(f"There is no class for: {clazz}")
