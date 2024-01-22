import pygame
import random
import constants
from particles import Particle
from weapon import Hand, WeaponFetcher
from entity import AnimatedEntity
from loader import assets, fonts
from gui import HealthBar, FadingOverlay, FixedBar, FixedOverlay

class Player(AnimatedEntity):
    def __init__(self, groups, pos, health = 500):
        super().__init__(
            [groups["render"], groups["update"], groups["bottom-weighted-render"]],
            assets.loadAnimationFolder("player", 4, 6, 6),
            speed = 10, canCollide = False, checksCollision = True, collisionSprites = groups["collide"]
            )
    
        self.groupdict = groups

        self.image = self.animations[self.currentAnimation][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.get_width(), self.image.get_height()//2)
        self.lastFacing = "right"

        self.hand: Hand = None
        self.healthbar = HealthBar(groups, self.rect, colour = (70, 255, 75))

        self.health = health
        self.maxHealth = health

        # Load GUIs
        self.globalHealthBar = FixedBar(self.groupdict, 5, 20, 192, 24, (255, 70, 75))
        self.globalHealthText = FixedOverlay(self.groupdict, 5, 5, pygame.Surface((1, 1)), font = fonts["alagard-16"])
        self.globalHealthText.setText(f"{self.health}/{self.maxHealth}", (255, 70, 75))

        self.inventory = {
            1: WeaponFetcher.assaultRifle(),
            2: WeaponFetcher.magicWand()
        }

        self.selected = 0

        self.cachedPressed = pygame.key.get_pressed()

        self.dead = False

    def getInput(self):
        self.movement.xy = (0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.movement.y -= 1
            self.currentAnimation = "run-" + self.lastFacing
        if keys[pygame.K_a]:
            self.movement.x -= 1
            self.currentAnimation = "run-left"
            self.lastFacing = "left"
        if keys[pygame.K_s]:
            self.movement.y += 1
            self.currentAnimation = "run-" + self.lastFacing
        if keys[pygame.K_d]:
            self.movement.x += 1
            self.currentAnimation = "run-right"
            self.lastFacing = "right"

        if self.movement.xy == (0, 0): self.currentAnimation = "idle-" + self.lastFacing

        for slot, key in constants.KEYBINDS["equip"].items():
            if keys[key] and not self.cachedPressed[key]:
                if self.selected == slot:
                    self.hand.setWeapon(None)
                    self.selected = 0
                else:
                    self.hand.setWeapon(self.inventory[slot])
                    self.selected = slot

        # if keys[pygame.K_1] and not self.cachedPressed[pygame.K_1]:
        #     if self.selected == 1:
        #         self.hand.setWeapon(None)
        #         self.selected = 0
        #     else:
        #         self.hand.setWeapon(self.inventory[1])
        #         self.selected = 1

        self.cachedPressed = keys

        mousepressed = pygame.mouse.get_pressed()
        if mousepressed[0]:
            self.hand.handleClick()

    def checkEnemyContact(self):
        for enemy in self.groupdict["enemy"]:
            if self.rect.colliderect(enemy.rect):
                self.health -= enemy.stats["damage"]
                self.healthbar.setPercentage(self.health / self.maxHealth)

                self.globalHealthBar.setPercentage(self.health / self.maxHealth)
                self.globalHealthText.setText(f"{self.health}/{self.maxHealth}", (255, 70, 75))

                s = pygame.Surface(constants.SCREENSIZE)
                s.fill((255, 100, 100))
                # FadingOverlay(self.groupdict, s, constants.HALFSCREENSIZE, 30, 0, 60)

                if self.health <= 0:
                    self.kill()

    def kill(self):
        self.hand.kill()
        self.healthbar.kill()
        self.dead = True
        self.currentAnimation = "death"

    def updateDeath(self, dt):
        if self.animationIndex >= 6:
            for _ in range(100):
                size = random.randint(4, 32)
                s = pygame.Surface((size, size))
                s.fill((random.randint(30, 180), 0, 0))
                Particle(self.groupdict, s, self.rect.center, random.randint(0, 360), random.randint(0, 5), 30)

            super().kill()
            s = pygame.font.Font(None, 64).render("Game Over", True, (150, 0, 0), (50, 0, 0))
            FadingOverlay(self.groupdict, s, constants.HALFSCREENSIZE, 255, 0, 600)

        self.animate(dt)
            
    def update(self, dt):
        if self.dead:
            self.updateDeath(dt)
            return

        super().update(dt)
        self.getInput()
        self.checkEnemyContact()

