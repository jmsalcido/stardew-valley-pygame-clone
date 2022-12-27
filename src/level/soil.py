import pygame.sprite
import pytmx
from pygame import Rect
from pygame.sprite import AbstractGroup

from src import settings


class SoilTile(pygame.sprite.Sprite):

    def __init__(self, pos, surface, groups) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.z = settings.LAYERS['soil']


class SoilLayer:
    def __init__(self, all_sprites) -> None:
        super().__init__()
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.soil_surface = pygame.image.load('../graphics/soil/o.png')
        self.grid = None
        self.hit_rects = None
        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        farmable_tiles = pytmx.load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles()
        h_tiles = ground.get_width() // settings.TILE_SIZE
        v_tiles = ground.get_height() // settings.TILE_SIZE
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]

        for x, y, _ in farmable_tiles:
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * settings.TILE_SIZE
                    y = index_row * settings.TILE_SIZE
                    rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        rect: Rect
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // settings.TILE_SIZE
                y = rect.y // settings.TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    x = index_col * settings.TILE_SIZE
                    y = index_row * settings.TILE_SIZE
                    SoilTile((x, y), self.soil_surface, (self.all_sprites, self.soil_sprites,))
