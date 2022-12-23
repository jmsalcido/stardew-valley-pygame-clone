import pygame


class Timer:
    def __init__(self, duration, func=None) -> None:
        super().__init__()
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.active and current_time - self.start_time >= self.duration:
            self.deactivate()
            if self.func:
                self.func()
