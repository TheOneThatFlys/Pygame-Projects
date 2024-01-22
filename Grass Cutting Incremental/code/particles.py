import pygame
import random
from loading import descriptionfont
from utils import customFormat

class MoneyParticle(pygame.sprite.Sprite):
    def __init__(self, groupDict, x, y, value):
        super().__init__(groupDict["particles"])
        self.value = value
        self.image = descriptionfont.render(f"${customFormat(self.value)}", True, (255, 255, 255))
        self.rect = self.image.get_rect(center = (x, y))

        self.vel = random.randrange(-3, 0)
        self.life = random.randrange(20, 60)

    def update(self):
        self.rect.y += self.vel
        self.life -= 1

        if self.life <= 0:
            self.kill()