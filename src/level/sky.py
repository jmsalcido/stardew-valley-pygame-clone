from random import randint, choice

import pygame.image

from src import settings
from src.sprites import Generic
from src.support import import_folder


class Drop(Generic):

    def __init__(self, pos, surface, moving, groups, z=settings.LAYERS['rain drops']) -> None:
        super().__init__(pos, surface, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        self.moving = moving
        if moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt):
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites) -> None:
        super().__init__()
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('../graphics/rain/drops/')
        self.rain_floor = import_folder('../graphics/rain/floor/')
        self.floor_w, self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size()

    def create_floor(self):
        Drop(
            surface=choice(self.rain_floor),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=False,
            groups=(self.all_sprites,)
        )

    def create_drops(self):
        Drop(
            surface=choice(self.rain_drops),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=True,
            groups=(self.all_sprites,),
            z=settings.LAYERS['rain drops']
        )

    def update(self):
        self.create_floor()
        self.create_drops()
