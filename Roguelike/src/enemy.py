import pygame
import random
import math

import constants
from entity import AnimatedEntity
from particles import Particle
from gui import HealthBar
from loader import assets

class EnemySpawner(pygame.sprite.Sprite):
    def __init__(self, groups, pos, player, cooldown = 600):
        super().__init__(groups["update"])
        self.groupdict = groups
        self.pos = pos
        self.player = player
        self.countdown = cooldown
        self.cooldown = cooldown

    def update(self, dt):

        self.countdown += dt
        if self.countdown >= self.cooldown:
            Skeleton(self.groupdict, self.pos, self.player)
            self.countdown = 0

class Enemy(AnimatedEntity):
    def __init__(self, groups : dict[str, pygame.sprite.Group], animationFolder: str, idleFrames: int, runFrames: int, deathFrames: int, pos: tuple[int, int], player, *, speed = 5, damage = 10, health = 50):
        super().__init__([groups["render"], groups["enemy"], groups["update"], groups["bottom-weighted-render"]], assets.loadAnimationFolder(animationFolder, idleFrames, runFrames, deathFrames), speed = speed, checksCollision = True, collisionSprites = groups["collide"])
        self.groupdict = groups

        self.image = self.animations[self.currentAnimation][0]
        self.rect = self.image.get_rect(topleft = pos)

        self.player = player
        self.walls: pygame.sprite.Group = groups["collide"]
        self.stats = {
            "damage": damage,
            "health": health,
            "maxhealth": health,
        }

        self.deathFrames = deathFrames
        self.lastFacing = "right"

        self.walkCooldown = random.randint(20, 80)
        self.walkAmount = random.randint(20, 80)

        self.healthBar = HealthBar(groups, self.rect)

        self.dead = False

    def hit(self, damage):
        self.stats["health"] -= damage

        if self.stats["health"] <= 0:
            self.kill()

    def hasLineOfSight(self, rect: pygame.Rect):
        for sprite in self.walls.sprites():
            if len(sprite.rect.clipline(self.rect.center, rect.center)) > 0:
                return False
        return True

    def kill(self):
        self.healthBar.kill()

        self.dead = True
        self.currentAnimation = "death"
        
        self.remove(self.groupdict["enemy"])

    def calculateAnimation(self):
        
        if self.movement.y < 0:
            self.currentAnimation = "run-" + self.lastFacing
        if self.movement.x < 0:
            self.currentAnimation = "run-left"
            self.lastFacing = "left"
        if self.movement.y > 0:
            self.currentAnimation = "run-" + self.lastFacing
        if self.movement.x > 0:
            self.currentAnimation = "run-right"
            self.lastFacing = "right"

        if self.movement.xy == (0, 0): self.currentAnimation = "idle-" + self.lastFacing

    def update(self, dt):
        if self.dead:
            if self.animationIndex >= self.deathFrames:
                for _ in range(20):
                    size = random.randint(4, 8)
                    s = pygame.Surface((size, size))
                    s.fill((random.randint(30, 180), 0, 0))

                    Particle(self.groupdict, s, self.rect.center, random.randint(0, 360), random.randint(0, 3), 30)
                super().kill()

        super().animate(dt)
        if self.dead: return

        if self.walkCooldown < 0:
            super().move(dt)
            self.walkAmount -= dt

            self.setDirection(math.atan2(self.player.rect.centery - self.rect.centery, self.player.rect.centerx - self.rect.centerx), False)

            if self.walkAmount < 0:
                self.walkCooldown = random.randint(20, 80)
                self.walkAmount = random.randint(20, 80)
        else:
            self.movement.xy = 0, 0

        self.walkCooldown -= dt

        self.calculateAnimation()

        self.healthBar.setPercentage(self.stats["health"] / self.stats["maxhealth"])

class Skeleton(Enemy):
    def __init__(self, groups, pos, player):
        super().__init__(
            groups = groups,
            animationFolder = "enemy.skeleton",
            idleFrames = 4,
            runFrames = 6,
            deathFrames = 8,
            pos = pos,
            player = player,
            speed = constants.ENEMYSTATS["skeleton"]["speed"],
            damage = constants.ENEMYSTATS["skeleton"]["damage"],
            health = constants.ENEMYSTATS["skeleton"]["health"],
        )
