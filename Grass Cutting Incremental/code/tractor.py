import pygame
from math import cos, sin, radians

from utils import getDistance, hueShift, getVector2Angle, getTurningDirection, closeTo
from upgrade import roombaUpgrades
from loading import roomba
from globals_ import dis

#Its a roomba but too late to change it now
class Tractor():
    def __init__(self, groups, x, y):
        self.dis = dis

        self.image = roomba["roomba"]
        self.rect = self.image.get_rect(center=(x, y))

        self.laserSurface = pygame.Surface((16, 16))
        self.laserSurface.fill((255, 0, 0))
        self.laserSurface.set_alpha(100)

        self.doChroma = False

        self.grassSprites = groups["grass"]
        self.groups = groups

        self.speed = 2
        self.turningSpeed = 2
        self.direction = 0
        self.targetDirection = 0
        self.moveVec = pygame.math.Vector2()

    def calculateDirection(self):
        shortestDistance = 65536
        shortestPosition = ()
        for grass in self.grassSprites.sprites():
            distance = getDistance(self.rect.center, grass.rect.center)
            if distance < shortestDistance:
                shortestDistance = distance
                shortestPosition = grass.rect.center
                self.targetPos = grass.rect.center

        if shortestPosition == (): return # Return if no grass is found

        dx = shortestPosition[0] - self.rect.centerx
        dy = shortestPosition[1] - self.rect.centery

        self.moveVec.x = dx
        self.moveVec.y = dy

        self.moveVec.scale_to_length(self.speed)

    def calculateTurning(self):
        self.targetDirection = getVector2Angle(self.moveVec)

        if not closeTo(self.direction, self.targetDirection, self.turningSpeed + 1):
            direction = getTurningDirection(int(self.direction), int(self.targetDirection))
            if direction == "clockwise":
                # Clockwise
                self.direction -= self.turningSpeed
            else:
                # Anti-clockwise
                self.direction += self.turningSpeed
        
        if self.direction > 180:
            self.direction = -180
        elif self.direction < -180:
            self.direction = 180
        
        self.image = pygame.transform.rotate(roomba["roomba"], -self.direction)

        prevPos = self.rect.center
        self.rect = self.image.get_rect(center = prevPos)

        # pygame.draw.line(self.dis, (255, 0, 0), self.rect.center, (self.rect.centerx + cos(radians(self.direction)) * 50, self.rect.centery + sin(radians(self.direction)) * 50))

    def calcTrack(self):
        # this doesn't work please help me i can't do maths

        hypotenuse = 20
        theta = -(self.direction - 90)
        dx = -sin(radians(theta)) * hypotenuse
        dy = cos(radians(theta)) * hypotenuse

        x, y = self.rect.centerx + dx, self.rect.centery + dy

    def animateChroma(self):
        self.image = hueShift(self.image, 5)

    def update(self):
        self.calculateDirection()

        # Consider upgrades
        if roombaUpgrades.getUpgrade("chroma").amount == 1 and not self.doChroma: 
            self.doChroma = True
            self.image = roomba["colour"]
        if self.doChroma: self.animateChroma()

        self.speed = 2 + roombaUpgrades.getUpgrade("speed").amount 
        self.turningSpeed = 2 + roombaUpgrades.getUpgrade("turning").amount

        self.calculateTurning()

        # if self.direction > self.targetDirection - (self.turningSpeed + 1) and self.direction < self.targetDirection + (self.turningSpeed + 1):
        if closeTo(self.direction, self.targetDirection, self.turningSpeed + 1):
            self.rect.x += self.moveVec.x
            self.rect.y += self.moveVec.y

        self.dis.blit(self.image, self.rect)