import pygame

from src import settings
from src.support import game_tile_pos_tuple, import_folder


class Generic(pygame.sprite.Sprite):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main']) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z


class WildFlower(Generic):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main']) -> None:
        super().__init__(pos, surface, groups, z)


class Tree(Generic):

    def __init__(self, pos, surface, groups, z=settings.LAYERS['main'], name=None) -> None:
        super().__init__(pos, surface, groups, z)
        self.name = name


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
