from typing import Optional

import pygame

from src import settings
from src.level.soil import SoilLayer
from src.support import import_folder
from src.timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, all_sprites, collision_group, trees_group, interaction_group, soil_layer) -> None:
        super().__init__(all_sprites)

        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.z = settings.LAYERS['main']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.collision_group = collision_group
        self.interaction_group = interaction_group

        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        self.timers = {
            'tool_use': Timer(350, self.use_tool),
            'tool_switch': Timer(200, self.switch_tool),
            'seed_use': Timer(350, self.use_seed),
            'seed_switch': Timer(200, self.switch_seed),
        }

        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0,
        }

        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        self.trees_group = trees_group
        self.soil_layer: SoilLayer = soil_layer

        self.sleep = False
        self.target_pos = None

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        elif self.selected_tool == 'axe':
            for tree in self.trees_group.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        elif self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)

    def get_target_pos(self):
        self.target_pos = self.rect.center + settings.PLAYER_TOOL_OFFSET[self.status.split("_")[0]]

    def use_seed(self):
        print(self.selected_seed)

    def switch_tool(self):
        self.tool_index += 1
        if self.tool_index >= len(self.tools):
            self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

    def switch_seed(self):
        self.seed_index += 1
        if self.seed_index >= len(self.seeds):
            self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def import_assets(self):
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if self.timers['tool_use'].active or self.sleep:
            return

        if keys[pygame.K_UP]:
            self.status = 'up'
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.status = 'down'
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_LEFT]:
            self.status = 'left'
            self.direction.x = -1
        elif keys[pygame.K_RIGHT]:
            self.status = 'right'
            self.direction.x = 1
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE]:
            if not self.timers['tool_use'].active:
                self.timers['tool_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

        if keys[pygame.K_LCTRL]:
            if not self.timers['seed_use'].active:
                self.timers['seed_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

        if keys[pygame.K_q]:
            if not self.timers['tool_switch'].active:
                self.timers['tool_switch'].activate()

        if keys[pygame.K_e]:
            if not self.timers['seed_switch'].active:
                self.timers['seed_switch'].activate()

        if keys[pygame.K_RETURN]:
            collided_interaction = pygame.sprite.spritecollide(sprite=self,
                                                               group=self.interaction_group,
                                                               dokill=False)
            if collided_interaction:
                collision = collided_interaction[0]
                collision_name = getattr(collision, 'name', None)
                if collision_name == 'Trader':
                    pass
                elif collision_name == 'Bed':
                    if not self.sleep and hasattr(collision, 'transition'):
                        collision.transition.start()
                        self.status = 'left_idle'
                        self.sleep = True

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        # tool use
        if self.timers['tool_use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_group.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
        self.update_timers()
        self.get_target_pos()


class PlayerInventoryManager:

    def __init__(self) -> None:
        super().__init__()
        self._player: Optional[Player] = None

    def add_player(self, player: Player):
        self._player = player

    def add_to_inventory(self, item, quantity=1):
        if self._player is not None:
            self._player.item_inventory[item] += quantity

    def inventory(self):
        return self._player.item_inventory
