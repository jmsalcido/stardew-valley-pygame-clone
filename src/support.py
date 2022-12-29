from os import walk
import pygame

from src import settings


def _import_image_surface(path, storage, func):
    for _, __, img_files in walk(path):
        for image_file in img_files:
            full_path = f"{path}/{image_file}"
            image_surface = pygame.image.load(full_path).convert_alpha()
            func(storage, image_surface, image_file)
    return storage


def import_folder(path):
    surface_list = []
    _import_image_surface(path, surface_list, lambda storage, image_surface, image_file: storage.append(image_surface))
    return surface_list


def import_folder_dict(path):
    def _save_into_dict(storage, image_surface, image_file):
        storage[image_file.split('.')[0]] = image_surface

    surface_dict = {}
    _import_image_surface(path, surface_dict, _save_into_dict)
    return surface_dict


def game_tile_pos_tuple(x, y):
    return x * settings.TILE_SIZE, y * settings.TILE_SIZE
