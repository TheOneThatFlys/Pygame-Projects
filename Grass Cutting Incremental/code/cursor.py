import pygame
from globals_ import dis

class Cursor():
    def __init__(self, groups: dict[str, pygame.sprite.Group]):
        self.dis = dis
        self.size = 5
        self.setSize(self.size)

        self.groups = groups

    def setSize(self, size: int):
        self.image = pygame.Surface((size, size))
        self.image.set_alpha(100)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.size = size

    def getSize(self):
        return self.size

    def collidingPopup(self) -> bool:
        mousepos = pygame.mouse.get_pos()
        for sprite in self.groups["popups"].sprites():
            if sprite.rect.collidepoint(mousepos):
                return True

        return False

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

        if self.rect.centerx > 500 or self.collidingPopup():
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            return
        elif self.size != self.rect.height:
            self.setSize(self.size)
            
        if pygame.mouse.get_visible():
                pygame.mouse.set_visible(False)
        self.dis.blit(self.image, self.rect)
