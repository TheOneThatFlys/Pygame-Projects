import pygame
import time
import random
import constants
from player import Player
from enemy import Skeleton, EnemySpawner
from tile import Tile, Trapdoor
from weapon import Hand
from gui import InteractPopup, FixedOverlay
from loader import assets, maps, fonts
from debug import debug

class Level():
    def __init__(self, surface):
        self.dis = surface

        self.groups = {
            "render": pygame.sprite.Group(),
            "update": pygame.sprite.Group(),
            "collide": pygame.sprite.Group(),
            "floor": pygame.sprite.Group(),
            "particle": pygame.sprite.Group(),
            "enemy": pygame.sprite.Group(),
            "gui": pygame.sprite.Group(),
            "ingame-gui" : pygame.sprite.Group(),
            "bottom-weighted-render": pygame.sprite.Group(),
            "interactable": pygame.sprite.Group()
        }

        self.player = Player(self.groups, (0, 0))
        self.camera = FollowCamera(group=self.groups["render"], target=self.player.rect, maxDistance=(400, 200), groups = self.groups)
        self.player.hand = Hand(self.groups, self.player, self.camera)

        t = assets.loadTileSet("tiles.dungeon", 16 * constants.SCALERATIO)
        self.loadMap(maps["testroom"], t)

        self.lastTime = time.time()

        self.debugging = False

        self.cleared = False

    def loadMap(self, tiles: dict[list[list[int]]], images: list[pygame.Surface]):

        tilesize = images[0].get_width()
        for y, row in enumerate(tiles["0"]):
            for x, val in enumerate(row):
                if val == -1: continue
                Tile([self.groups["floor"]], images[val], (x * tilesize, y * tilesize))

        for y, row in enumerate(tiles["1"]):
            for x, val in enumerate(row):
                if val == -1: continue
                Tile([self.groups["render"]], images[val], (x * tilesize, y * tilesize))

        for y, row in enumerate(tiles["3"]):
            for x, val in enumerate(row):
                if val == -1: continue

                pos = (x * tilesize, y * tilesize)

                if val == constants.FUNCTIONALINDEXES["collide"]:
                    Tile([self.groups["collide"]], images[0], pos)
                    
                elif val == constants.FUNCTIONALINDEXES["player"]:
                    self.player.rect.topleft = pos

                elif val == constants.FUNCTIONALINDEXES["enemy"]:
                    # Skeleton(self.groups, pos, self.player)
                    EnemySpawner(self.groups, pos, self.player)

                elif val == constants.FUNCTIONALINDEXES["trapdoor"]:
                    Trapdoor(self.groups, pos)                    

    def updateInteractable(self):
        if not self.cleared:
            if not self.groups["enemy"]:
                self.cleared = True
                for sprite in self.groups["interactable"]:
                    if sprite.type == "trapdoor":
                        sprite.toggleOpen()

        for sprite in self.groups["interactable"]:
            v = pygame.Vector2(self.player.rect.centerx - sprite.rect.centerx, self.player.rect.centery - sprite.rect.centery)
            if v.magnitude() < constants.MAXINTERACTDISTANCE:
                if sprite.child == None:
                    InteractPopup(self.groups, fonts["alagard-32"], sprite.displayText, constants.BUBBLETEXTCOLOUR, sprite)
            elif sprite.child:
                sprite.child.kill()

    def run(self):

        # update
        dt = (time.time() - self.lastTime) * 60
        self.lastTime = time.time()
        self.groups["update"].update(dt)
        self.camera.update()
        self.updateInteractable()

        # draw
        self.camera.lossyFollow(dt)
        self.camera.renderOtherGroup(self.dis, self.groups["floor"])
        self.camera.render(self.dis)
        self.camera.renderOtherGroup(self.dis, self.groups["particle"])
        self.camera.renderOtherGroup(self.dis, self.groups["ingame-gui"])

        self.groups["gui"].draw(self.dis)

        # debug
        if self.debugging:
            debug(self.dis, self.player, self.camera, self.groups)

class FollowCamera():
    def __init__(self, group: pygame.sprite.Group, target: pygame.Rect, maxDistance=(0, 0), groups = None):
        self.groups = groups
        self.renderGroup = group
        self.target = target
        self.pos = pygame.math.Vector2(target.center)
        self.maxDistance = pygame.math.Vector2(maxDistance)

        self.shaking = {
            "amount": 0,
            "strength": 0,
        }

    def centerOn(self):
        self.pos = pygame.math.Vector2(self.target.center)

    def shake(self, amount: int, strength):
        self.shaking["strength"] = strength
        self.shaking["amount"] = amount

    def lossyFollow(self, dt):
        if int(self.pos.x) in range(int(self.target.centerx) - 3, int(self.target.centerx) + 3) and \
           int(self.pos.y) in range(int(self.target.centery) - 3, int(self.target.centery) + 3):
            return

        dx = ((self.target.centerx - self.pos.x) / 20)
        dy = ((self.target.centery - self.pos.y) / 20)

        # Make sure camera never moves less than 1
        if dx < 1 and dx > 0:
            dx = 1
        elif dx < 0 and dx > -1:
            dx = -1
        if dy < 1 and dy > 0:
            dy = 1
        elif dy < 0 and dy > -1:
            dy = -1

        self.pos.x += dx * dt
        self.pos.y += dy * dt

    def update(self):
        if self.shaking["amount"] > 0:
            s = self.shaking["strength"]
            self.pos.x += random.randint(-s - 5, s + 5)
            self.pos.y += random.randint(-s - 5, s + 5)
            self.shaking["amount"] -= 1

    def render(self, surface: pygame.Surface):
        hand = False
        for sprite in sorted(self.renderGroup.sprites(), key = lambda sprite: sprite.rect.centery):
            if sprite in self.groups["bottom-weighted-render"]:
                rect = sprite.image.get_rect(bottom = sprite.rect.bottom, centerx = sprite.rect.centerx)
            else:
                rect = sprite.rect

            x = rect.x - self.pos.x + constants.HALFSCREENSIZE[0]
            y = rect.y - self.pos.y + constants.HALFSCREENSIZE[1]

            if isinstance(sprite, Hand):
                hand = [sprite, x, y]

            surface.blit(sprite.image, (x, y))
        if hand: surface.blit(hand[0].image, (hand[1], hand[2]))
        

    def renderOtherGroup(self, surface: pygame.Surface, group: pygame.sprite.Group):
        for sprite in group.sprites():
            x = sprite.rect.x - self.pos.x + constants.HALFSCREENSIZE[0]
            y = sprite.rect.y - self.pos.y + constants.HALFSCREENSIZE[1]
            surface.blit(sprite.image, (x, y))

