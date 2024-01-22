import math
from entity import Entity

class Particle(Entity):
    def __init__(self, groups, image, pos, direction, speed, life):
        super().__init__([groups["particle"], groups["update"]], speed, False, False)
        self.originalImage = image
        self.image = image
        self.rect = self.image.get_rect(center = pos)
        self.setDirection(math.radians(direction))
        self.life = life

    def update(self, dt):
        self.move(dt)

        self.life -= dt
        if self.life < 0:
            self.kill()

class GravityParticle(Particle):
    def __init__(self, groups, image, pos, direction, speed, life):
        super().__init__(groups, image, pos, direction, speed, life)

    def update(self, dt):
        super().update(dt)

        self.movement.y += dt / 10