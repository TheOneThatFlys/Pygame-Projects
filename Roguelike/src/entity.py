
import pygame
import math

_inRadians = float

class Entity(pygame.sprite.Sprite):
    """
    Abstract class for entities
    """
    def __init__(self, groups, speed = 10, canCollide = False, checksCollision = True, collisionSprites = None):
        """
        Params:
        - groups: groups
        - speed: speed of movement
        - canCollide: is part of collision sprites
        - checkCollision: stops moving when colliding
        """
        if isinstance(groups, (list, tuple)):
            g = groups
            self.collisionSprites = collisionSprites
        else:
            g = [groups["render"], groups["update"]]
            if canCollide: g.append(groups["collide"])
            self.collisionSprites: pygame.sprite.Group = groups["collide"]
        super().__init__(g)

        self.checksCollision = checksCollision
        self.speed = speed

        self.movement = pygame.math.Vector2()

        self.zOrder = 0

    def checkCollision(self, dir: str, group: pygame.sprite.Group):
        if dir == "x":
            for sprite in group.sprites():
                if sprite == self: continue
                if self.rect.colliderect(sprite.rect):
                    if self.movement.x > 0:
                        self.rect.right = sprite.rect.left
                    elif self.movement.x < 0:
                        self.rect.left = sprite.rect.right
        if dir == "y":
            for sprite in group.sprites():
                if sprite == self: continue
                if self.rect.colliderect(sprite.rect):
                    if self.movement.y > 0:
                        self.rect.bottom = sprite.rect.top
                    elif self.movement.y < 0:
                        self.rect.top = sprite.rect.bottom

    def setDirection(self, direction: _inRadians, rotateSprite = True):
        """
        Sets the direction of movement of the entity, also changing its sprite\n
        Requires originalImage surface
        """
        self.movement.xy = math.cos(direction), math.sin(direction)
        c = self.rect.center
        if rotateSprite:
            self.image = pygame.transform.rotate(self.originalImage, -math.degrees(direction))
            self.rect = self.image.get_rect(center = c)

    def move(self, dt):
        if self.movement.magnitude() != 0:
            self.movement.normalize_ip()

        self.rect.x += self.movement.x * self.speed * dt
        if self.checksCollision: self.checkCollision("x", self.collisionSprites)

        self.rect.y += self.movement.y * self.speed * dt
        if self.checksCollision: self.checkCollision("y", self.collisionSprites)

    def update(self, dt):
        self.move(dt)
        
class AnimatedEntity(Entity):
    def __init__(self, groups, animations: dict[str, list[pygame.Surface]], initialAnimation = "idle-right", speed = 10, canCollide = False, checksCollision = True, collisionSprites = None):
        super().__init__(groups, speed, canCollide, checksCollision, collisionSprites)
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
            self.image = self.animations[self.currentAnimation][int(self.animationIndex)]
            self.animationIndex += dt

    def update(self, dt):
        super().update(dt)
        self.animate(dt)