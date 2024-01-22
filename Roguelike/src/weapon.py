from dataclasses import dataclass
from random import random, randrange, randint
import pygame
import math
import constants

from particles import Particle, GravityParticle
from entity import Entity
from loader import assets

class Hand(pygame.sprite.Sprite):
    def __init__(self, groups, player, camera):
        super().__init__([groups["render"], groups["update"]])
        self.usedImage = assets["weapons.hand"]  # Keep a copy of image as rotation slightly increases size
        self.image = self.usedImage
        self.rect = self.image.get_rect()

        self.DISTANCEFROMCENTER = (player.rect.width // 2) + (self.rect.width // 2) - 5
        self.camera = camera
        self.player = player
        self.groupdict = groups
        
        self.direction = pygame.math.Vector2()
        self.angle = 0

        self.weapon: Weapon = None

    def setWeapon(self, weapon):
        self.weapon = weapon

        if weapon == None:
            self.usedImage = assets["weapons.hand"]
        else:
            self.usedImage = weapon.image

        self.rect = self.usedImage.get_rect()

    def handleClick(self):
        if self.weapon == None: return
        if self.weapon.cooldown > self.weapon.fireInterval:
            self.weapon.cooldown = 0
            
            self.weapon.projectile(self.groupdict, self.rect.center, self.angle)

            self.camera.shake(*self.weapon.shake)

    def update(self, dt):
        mousepos = pygame.mouse.get_pos()
        scaledmousepos = (
            mousepos[0] - constants.HALFSCREENSIZE[0] + self.camera.pos.x,
            mousepos[1] - constants.HALFSCREENSIZE[1] + self.camera.pos.y
        )

        self.direction.x = scaledmousepos[0] - self.player.rect.centerx
        self.direction.y = scaledmousepos[1] - self.player.rect.y

        self.direction.scale_to_length(self.DISTANCEFROMCENTER)
        self.angle = math.degrees(math.atan2(self.direction.y, self.direction.x))

        if 90 < self.angle < 180 or -180 < self.angle < -90:
            self.image = pygame.transform.rotate(pygame.transform.flip(self.usedImage, False, True), -self.angle)
        else:
            self.image = pygame.transform.rotate(self.usedImage, -self.angle)
        
        self.rect = self.image.get_rect(center=(self.player.rect.centerx + self.direction.x, self.player.rect.y + self.direction.y))

        if self.weapon: self.weapon.cooldown += dt

class Projectile(Entity):
    def __init__(self, groups, image, pos, dir, speed, damage, life, destroyOnHit = True):
        super().__init__(groups, speed = speed, canCollide = False, checksCollision = False)
        self.remove(groups["render"])
        self.add(groups["particle"])
        self.groupdict = groups
        self.originalImage = image
        self.image = self.originalImage
        self.rect = image.get_rect(center = pos)

        self.pos = pygame.Vector2(pos)
        self.dir = math.radians(dir)
        self.setDirection(self.dir)

        self.speed = speed
        self.damage = damage
        self.destroyOnHit = destroyOnHit

        self.collisionSprites = groups["collide"]
        self.enemySprites = groups["enemy"]

        self.life = life

    def update(self, dt):
        self.setDirection(self.dir)
        super().update(dt)
        self.life -= dt
        if self.life < 0:
            super().kill()

        # Check walls
        for sprite in self.collisionSprites.sprites():
            if sprite.rect.colliderect(self.rect):
                self.kill()
                return
        
        # Check enemies (if enabled)
        for sprite in self.enemySprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.destroyOnHit:
                    self.kill()
                sprite.hit(self.damage)
                return

    def deathParticles(self):
        pass

    def kill(self):
        self.deathParticles()
        super().kill()

class AnimatedProjectile(Projectile):
    def __init__(self, groups, animations: dict[str, list[pygame.Surface]], pos, dir, speed, damage, life, destroyOnHit = True, initialAnimation = None):
        if not initialAnimation: initialAnimation = list(animations.keys())[0]
        super().__init__(groups, animations[initialAnimation][0], pos, dir, speed = speed, damage = damage, life = life, destroyOnHit = destroyOnHit)
        
        self.animations = animations

        self.currentAnimation = initialAnimation
        self.lastAnimation = self.currentAnimation
        self.animationIndex = 0
        self.animationCooldown = 0

    def animate(self, dt):
        self.animationCooldown += dt
        if self.animationCooldown > 10 or self.lastAnimation != self.currentAnimation:
            self.lastAnimation = self.currentAnimation
            if int(self.animationIndex) > len(self.animations[self.currentAnimation]) - 1:
                self.animationIndex = 0
            self.animationCooldown = 0
            self.originalImage = self.animations[self.currentAnimation][int(self.animationIndex)]
            self.animationIndex += dt

    def update(self, dt):
        self.animate(dt)
        super().update(dt)


@dataclass
class Weapon():
    image: pygame.Surface
    projectile: type

    fireInterval: int = 10
    shake: tuple[int, int] = (0, 0)

    cooldown: int = fireInterval
    destroyOnHit: bool = True

class GunProjectile(Projectile):
    def __init__(self, groups, pos, dir):
        super().__init__(groups, assets["projectiles.bullet"], pos, dir, speed = 20, damage = 10, life = 600, destroyOnHit = True)

    def deathParticles(self):
        for _ in range(10):
            size = int(random() * 12) + 4
            colour = int(random() * 256)

            s = pygame.Surface((size, size))
            s.fill((colour, colour, colour))

            Particle(self.groupdict, s, self.rect.center, random() * 360, random() * 5, 30)

class Lightning(Projectile):
    def __init__(self, groups, pos, targetSprite, damage):

        # Calculate lightning direct path
        dv = pygame.Vector2(targetSprite.rect.centerx - pos[0], targetSprite.rect.centery - pos[1])
        image = pygame.Surface((abs(dv.x * 2), abs(dv.y * 2)))
        image.set_colorkey((0, 0, 0))

        # Lightning is centered on the parent and fans out
        startpos = pygame.Vector2(image.get_width()/2, image.get_height()/2)
        endpos = pygame.Vector2(image.get_width()/2 + dv.x, image.get_height()/2 + dv.y)

        minX, maxX = min(startpos.x, endpos.x), max(startpos.x, endpos.x)
        minY, maxY = min(startpos.y, endpos.y), max(startpos.y, endpos.y)

        points = []
        for _ in range(randrange(0, 4)):
            points.append(pygame.Vector2(randint(minX, maxX), randint(minY, maxY)))

        # Sort points by distance from start
        points.sort(key = lambda p: pygame.Vector2(p.x - startpos.x, p.y - startpos.y).magnitude())

        # Draw lightning
        currentPoint = startpos
        for p in points:
            pygame.draw.line(image, (200, 205, 255), currentPoint, p, 3)
            currentPoint = p

        super().__init__(groups, image, pos, 0, 0, damage, 20, False)
        self.rect.center = pos

        self.target = targetSprite

    def update(self, dt):
        self.life -= dt
        if self.life < 0:
            super().kill()

        self.target.hit(self.damage)

class WandProjectile(AnimatedProjectile):
    LATCH_RADIUS = 512

    def __init__(self, groups, pos, dir):
        super().__init__(
            groups, {0: assets.loadAnimation(assets["projectiles.electric_orb"], 6)}, pos, dir, speed = 2, damage = 0.1, life = 600, destroyOnHit = False)

    def update(self, dt):
        super().update(dt)

        for enemy in self.groupdict["enemy"].sprites():
            # Connect lightning things with enemies in range
            dv = pygame.Vector2(enemy.rect.centerx - self.rect.centerx, enemy.rect.centery - self.rect.centery) # Vector to store difference of projectile and enemy
            if dv.magnitude() < self.LATCH_RADIUS:
                if random() > 0.95:
                    Lightning(self.groupdict, self.rect.center, enemy, self.damage)

    def deathParticles(self):
        for _ in range(20):
            image = pygame.Surface((4, 4))
            image.fill((100, 100, 250))
            GravityParticle(self.groupdict, image, self.rect.center, random() * 360, random() * 3, 30)
                
class WeaponFetcher():
    @staticmethod
    def assaultRifle():
        return Weapon(
            image =  assets["weapons.gun"],
            projectile = GunProjectile,
            fireInterval = 10,
            shake = (5, 5)
        )

    @staticmethod
    def magicWand():
        return Weapon(
            image = assets["weapons.wand"],
            projectile = WandProjectile,
            fireInterval = 45,
            shake = (0, 0),
        )

if __name__ == "__main__":
    pygame.init()
    w = pygame.display.set_mode((500, 500))

    groups: dict[str, pygame.sprite.Group] = {
        "render": pygame.sprite.Group(),
        "update": pygame.sprite.Group(),
    }

    image = pygame.Surface((64, 64), pygame.SRCALPHA)
    image.set_colorkey((0, 0, 0))
    pygame.draw.line(image, (255, 0, 0), (32, 32), (0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        w.fill((255, 255, 255))
        groups["update"].update()
        groups["render"].draw(w)
        w.blit(image, (50, 50))

        pygame.display.update()
    pygame.quit()