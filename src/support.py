from os import walk
import pygame

from src import settings


def import_folder(path):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = f"{path}/{image}"
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list


def game_tile_pos_tuple(x, y):
    return x * settings.TILE_SIZE, y * settings.TILE_SIZE
