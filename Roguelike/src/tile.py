import pygame
import constants
from loader import assets


_TRAPDOOROPEN = 133
_TRAPDOORCLOSED = 108

class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, img, pos):
        super().__init__(groups)
        self.image = img
        self.rect = self.image.get_rect(topleft=pos)

class Trapdoor(Tile):
    def __init__(self, groups, pos):
        super().__init__([groups["floor"], groups["update"], groups["interactable"]], assets["tiles.dungeon.tileAt"][_TRAPDOORCLOSED], pos)
        self.type = "trapdoor"
        self.displayText = ["Defeat all enemies first!"]
        self.child = None

        self.open = False

    def toggleOpen(self):
        self.open = True
        self.image = assets["tiles.dungeon.tileAt"][_TRAPDOOROPEN]
        self.displayText = [constants.BUBBLETEXTCOLOUR, "Press ", (163, 10, 10), "e", constants.BUBBLETEXTCOLOUR, " to enter the next floor!"]

    def update(self, dt):
        pass