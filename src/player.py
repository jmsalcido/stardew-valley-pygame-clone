import pygame

from timer import Timer
from support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group) -> None:
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        self.timers = {
            'tool_use': Timer(350, self.use_tool),
            'tool_switch': Timer(200, self.switch_tool),
            'seed_use': Timer(350, self.use_seed),
            'seed_switch': Timer(200, self.switch_seed)
        }

        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def use_tool(self):
        pass

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
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}

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

        if self.timers['tool_use'].active:
            pass

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
        self.rect.centerx = self.pos.x

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
        self.update_timers()
