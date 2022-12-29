import pygame.sprite
import pytmx
from pygame import Rect

from src import settings
from src.support import import_folder_dict


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
        self.soil_surfaces = import_folder_dict('../graphics/soil/')

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
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    l = 'X' in row[index_col - 1]
                    r = 'X' in row[index_col + 1]

                    tile_type = 'o'

                    tile_dict = {
                        lambda: all((t, b, l, r)): 'x',
                        lambda: l and not any((t, b, r)): 'r',
                        lambda: r and not any((t, b, l)): 'l',
                        lambda: r and l and not any((t, b)): 'lr',
                        lambda: t and not any((l, b, r)): 'b',
                        lambda: b and not any((l, t, r)): 't',
                        lambda: b and t and not any((l, r)): 'tb',
                        lambda: l and b and not any((t, r)): 'tr',
                        lambda: r and b and not any((t, l)): 'tl',
                        lambda: l and t and not any((b, r)): 'br',
                        lambda: r and t and not any((b, l)): 'bl',
                        lambda: all((t, b, r)) and not l: 'tbr',
                        lambda: all((t, b, l)) and not r: 'tbl',
                        lambda: all((l, r, t)) and not b: 'lrb',
                        lambda: all((l, r, b)) and not t: 'lrt',
                    }

                    for predicate, tile_result in tile_dict.items():
                        if predicate():
                            tile_type = tile_result

                    x = index_col * settings.TILE_SIZE
                    y = index_row * settings.TILE_SIZE
                    SoilTile((x, y), self.soil_surfaces[tile_type], (self.all_sprites, self.soil_sprites,))
