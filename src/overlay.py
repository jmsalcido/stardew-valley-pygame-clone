import pygame.display

from src import settings


class Overlay:

    def __init__(self, player) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.player = player

        overlay_path = '../graphics/overlay'
        self.tools_surface = {tool: pygame.image.load(f'{overlay_path}/{tool}.png').convert_alpha() for tool in
                              self.player.tools}
        self.seeds_surface = {seed: pygame.image.load(f'{overlay_path}/{seed}.png').convert_alpha() for seed in
                              self.player.seeds}

    def display(self):
        self._display_item('tool')
        self._display_item('seed')

    def _display_item(self, item_attr: str):
        # if item_attr != 'seed' or item_attr != 'tool':
        #     raise Exception("Wrong attr")
        surface = getattr(self, f'{item_attr}s_surface')[getattr(self.player, f'selected_{item_attr}')]
        surface_rect = surface.get_rect(midbottom=settings.OVERLAY_POSITIONS[item_attr])
        self.display_surface.blit(surface, surface_rect)
