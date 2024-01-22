import pygame
from loading import grass as grassimg
from upgrade import grassUpgrades
import random

class Grass(pygame.sprite.Sprite):
    def __init__(self, groups, x, y):
        super().__init__([groups["render"], groups["grass"]])

        self.image = grassimg
        self.rect = self.image.get_rect(topleft = (x, y))

class Controller():
    def __init__(self, groups, topleft, bottomright):
        self.groups = groups

        self.timer = 0

        self.topleft = topleft
        self.bottomright = bottomright

        self.grassSize = grassimg.get_width()
        grassArea = ((bottomright[0]-topleft[0]) - 10) // self.grassSize
        self.emptySlots: list = self.getEmpty((grassArea, grassArea))

        #Upgradables
        self.delay = 60
        self.max = 10

    def getEmpty(self, size: tuple[int, int]) -> list[tuple[int, int]]:
        returnlist = []
        for x in range(size[0]):
            for y in range(size[1]):
                returnlist.append((x, y))
        return returnlist

    def generateGrass(self):
        # Grass(self.groups, random.randint(self.topleft[0], self.bottomright[0] - 8), random.randint(self.topleft[1], self.bottomright[1] - 16))

        arrPos = random.choice(self.emptySlots)
        x, y = arrPos[0] * self.grassSize, arrPos[1] * self.grassSize
        self.emptySlots.remove(arrPos)
        Grass(self.groups, x, y)
    
    def killGrass(self, grass: Grass):
        arrPos = grass.rect.x // self.grassSize, grass.rect.y // self.grassSize
        self.emptySlots.append(arrPos)
        grass.kill()

    def update(self):
        self.timer += 1
        if self.timer > self.delay:
            self.timer = 0

        speedAmount = grassUpgrades.getUpgrade("speed").amount

        self.delay = 61 - speedAmount
        if self.delay < 1: self.delay = 1

        nGenerated = 1
        # Calculate overflow speed into double/triple etc.
        leftover = speedAmount - 60
        if leftover > 0:
            nGenerated += leftover // 60
            if random.randint(0, 60) < leftover % 60:
                nGenerated += 1

        if self.timer == self.delay:
            if len(self.groups["grass"].sprites()) + nGenerated <= self.max:
                for _ in range(nGenerated):
                    self.generateGrass()
