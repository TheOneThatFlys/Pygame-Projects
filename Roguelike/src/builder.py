
import pygame
import pygame.freetype
import csv
import os
import constants
from loader import assets

class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, img, pos, value):
        super().__init__(groups)
        self.image = img
        self.rect = self.image.get_rect(topleft=pos)

        self.value = value

class Builder():
    def __init__(self):
        pygame.init()
        self.dis = pygame.display.set_mode(constants.SCREENSIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Level Builder")
        assets.load("assets", constants.SCALERATIO)
        

        self.layers = {
            0: pygame.sprite.Group(),
            1: pygame.sprite.Group(),
            2: pygame.sprite.Group(),
            3: pygame.sprite.Group(),
        }

        self.fonts = {
            8: pygame.freetype.SysFont(None, 8),
            16: pygame.freetype.SysFont(None, 16),
        }

        self.tileImages = assets.loadTileSet(assets["tiles.dungeon"], constants.SCALEDTILESIZE)
        self.nativeTileImages = [pygame.transform.scale(image, (constants.NATIVETILESIZE, constants.NATIVETILESIZE)) for image in self.tileImages]
        self.tileDimensions = assets["tiles.dungeon"].get_width() // constants.SCALEDTILESIZE, assets["tiles.dungeon"].get_height() // constants.SCALEDTILESIZE
        self.tileSelected = 0
        self.layer = 0

        self.GUISEPX = constants.SCREENSIZE[0] - constants.SCALEDTILESIZE * 10

        self.buttons = pygame.sprite.Group()
        i = 0
        for y in range(self.tileDimensions[1]):
            for x in range(self.tileDimensions[0]):
                s = pygame.sprite.Sprite()
                s.image = self.nativeTileImages[i]
                s.val = i
                s.rect = s.image.get_rect(topleft = (self.GUISEPX + 8 + x * constants.NATIVETILESIZE, 128 + y * constants.NATIVETILESIZE))
                self.buttons.add(s)
                i += 1

        self.building = False
        self.clearing = False
        self.shiftPressed = False

        self.camera = Camera(((constants.SCREENSIZE[0] - self.GUISEPX)//2, constants.SCREENSIZE[1]//2))

        # default 32 x 32 room generator
        SIZE = 16
        tilelocations = []
        for i in range(SIZE + 2):
            tilelocations.append((i, 0))
            tilelocations.append((0, i))
            tilelocations.append((i, SIZE + 1))
            tilelocations.append((SIZE + 1, i))

        for x, y in tilelocations:
            Tile(self.layers[3], self.tileImages[23], (x * constants.SCALEDTILESIZE, y * constants.SCALEDTILESIZE), 23)

    def getScaledPos(self, x_y: tuple[int, int]):
        newx = x_y[0] + self.camera.pos.x - constants.HALFSCREENSIZE[0]
        newy = x_y[1] + self.camera.pos.y - constants.HALFSCREENSIZE[1]

        return (newx, newy)

    def saveLayout(self):
        # Parse tile data into more readable stuff
        layers: dict[int, list[tuple[int, int, int]]] = {}
        for key, layer in self.layers.items():
            layers[key] = []
            for tile in layer.sprites():
                layers[key].append((
                    tile.rect.x // constants.SCALEDTILESIZE,
                    tile.rect.y // constants.SCALEDTILESIZE,
                    tile.value
                ))

        # return if no tiles placed
        for _, layer in layers.items():
            if len(layer) > 0:
                break
        else:
            print("Nothing to save!")
            return

        # Convert tiles to 2d arr
        smallestx = 1e10
        biggestx = -1e10
        smallesty = 1e10
        biggesty = -1e10

        for key, layer in layers.items():
            for sprite in layer:
                if sprite[0] < smallestx: smallestx = sprite[0]
                if sprite[0] > biggestx: biggestx = sprite[0]
                if sprite[1] < smallesty: smallesty = sprite[1]
                if sprite[1] > biggesty: biggesty = sprite[1]

        if biggestx < smallestx or biggesty < smallesty:
            raise Exception("b < s for some reason") 

        # generate 2d arr to fit
        nx = len(range(smallestx, biggestx)) + 1
        ny = len(range(smallesty, biggesty)) + 1

        tilemaps = {}
        for i in range(4):
            tilemaps[i] = [[-1 for _ in range(nx)] for _ in range(ny)]

        for key, layer in layers.items():
            for spritex, spritey, value in layer:

                scaledx = int(nx * ((spritex - smallestx) / nx))
                scaledy = int(ny * ((spritey - smallesty) / ny))

                tilemaps[key][scaledy][scaledx] = value

        foldername = input("Enter folder name: ")
        os.mkdir(os.path.join("maps", foldername))
        for name, map in tilemaps.items():
            path = os.path.join("maps", foldername, f"{name}.csv")
            with open(path, "x") as f:
                w = csv.writer(f)
                for row in map:
                    w.writerow(row)

            # Get rid of empty lines
            with open(path) as f:
                d = []
                lines = f.readlines()
                for l in lines:
                    if l != "\n":
                        d.append(l)

            with open(path, "w") as f:
                for l in d:
                    f.write(l)

        print("Save success")

    def loadLayout(self):
        fp = input("Enter foldername: ")
        for key, item in self.layers.items():
            item.empty()
            path = os.path.join("maps", fp, f"{key}.csv")
            with open(path, "r") as f:
                r = csv.reader(f)
                for y, row in enumerate(r):
                    for x, val in enumerate(row):
                        Tile(item, self.tileImages[int(val)], (x * constants.SCALEDTILESIZE, y * constants.SCALEDTILESIZE), val)

    def run(self):
        running = True
        while running == True:
            self.clock.tick(constants.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.layer += 1
                        if self.layer > len(self.layers) - 1: self.layer = len(self.layers) - 1

                    elif event.key == pygame.K_q:
                        self.layer -= 1
                        if self.layer < 0: self.layer = 0

                    elif self.shiftPressed:
                        if event.key == pygame.K_w:
                            x = self.tileSelected - self.tileDimensions[1]
                            if x // self.tileDimensions[1] >= 0:
                                self.tileSelected = x

                        elif event.key == pygame.K_a:
                            x = self.tileSelected - 1
                            if x % self.tileDimensions[1] >= 0:
                                self.tileSelected = x

                        elif event.key == pygame.K_s:
                            x = self.tileSelected + self.tileDimensions[1]
                            if x // self.tileDimensions[1] < self.tileDimensions[1]:
                                self.tileSelected = x

                        elif event.key == pygame.K_d:
                            x = self.tileSelected + 1
                            if x % self.tileDimensions[1] < self.tileDimensions[0]:
                                self.tileSelected = x

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.building = True
                        mp = pygame.mouse.get_pos()
                        if mp[0] > self.GUISEPX:
                            for sprite in self.buttons.sprites():
                                if sprite.rect.collidepoint(mp):
                                    self.tileSelected = sprite.val
                                
                    elif event.button == 3:
                        self.clearing = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.building = False
                    elif event.button == 3:
                        self.clearing = False

            # Update
            if self.building:
                x, y = self.getScaledPos(pygame.mouse.get_pos())
                x -= x % constants.SCALEDTILESIZE
                y -= y % constants.SCALEDTILESIZE
                if pygame.mouse.get_pos()[0] < self.GUISEPX:
                    for sprite in self.layers[self.layer].sprites():
                        if sprite.rect.collidepoint((x, y)):
                            sprite.kill()
                            break
                    Tile(self.layers[self.layer], self.tileImages[self.tileSelected], (x, y), self.tileSelected)

            if self.clearing:
                x, y = self.getScaledPos(pygame.mouse.get_pos())
                x -= x % constants.SCALEDTILESIZE
                y -= y % constants.SCALEDTILESIZE
                if pygame.mouse.get_pos()[0] < self.GUISEPX:
                    for sprite in self.layers[self.layer].sprites():
                        if sprite.rect.collidepoint((x, y)):
                            sprite.kill()
                            break

            self.shiftPressed = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
                self.saveLayout()
            if [pygame.K_LCTRL] and keys[pygame.K_l]:
                self.loadLayout()
            if keys[pygame.K_LSHIFT]: self.shiftPressed = True

            self.camera.update()

            # Render
            self.dis.fill((0, 0, 0))
            self.camera.render(self.dis, self.layers, self.layer)

            # GUI
            pygame.draw.rect(self.dis, (0, 0, 0), [self.GUISEPX, 0, constants.SCREENSIZE[0] - self.GUISEPX, constants.SCREENSIZE[1]])
            pygame.draw.line(self.dis, (255, 255, 255), (self.GUISEPX, 0), (self.GUISEPX, constants.SCREENSIZE[1]))

            surfLayer, rectLayer = self.fonts[16].render(f"Layer: {self.layer}", (255, 255, 255))
            rectLayer.topleft = (self.GUISEPX + 8, 8)
            self.dis.blit(surfLayer, rectLayer)

            self.dis.blit(self.tileImages[self.tileSelected], (self.GUISEPX + 8, rectLayer.bottom + 8))
            pygame.draw.rect(self.dis, (255, 255, 255), self.tileImages[self.tileSelected].get_rect(topleft = (self.GUISEPX + 8, rectLayer.bottom + 8)), 1)
            self.fonts[8].render_to(self.dis, (self.GUISEPX + 8, 84), f"ID: {self.tileSelected}", (255, 255, 255))

            self.buttons.draw(self.dis)
            pygame.draw.rect(self.dis, (255, 255, 255), self.buttons.sprites()[self.tileSelected], 1)

            pygame.display.update()

        pygame.quit()

class Camera():
    def __init__(self, position: pygame.math.Vector2 | tuple[int, int]):
        self.pos = pygame.math.Vector2(position)
        self.vecMovement = pygame.math.Vector2()

        self.speed = 10

    def update(self):
        keys = pygame.key.get_pressed()
        self.vecMovement.xy = (0, 0)
        if not keys[pygame.K_LSHIFT] and not keys[pygame.K_LCTRL]:
            if keys[pygame.K_w]: self.vecMovement.y -= 1
            if keys[pygame.K_a]: self.vecMovement.x -= 1
            if keys[pygame.K_s]: self.vecMovement.y += 1
            if keys[pygame.K_d]: self.vecMovement.x += 1
        if self.vecMovement.magnitude() != 0:
            self.vecMovement.normalize_ip()

        self.pos.x += self.vecMovement.x * self.speed
        self.pos.y += self.vecMovement.y * self.speed

    def render(self, surface: pygame.Surface, groups: dict[int, pygame.sprite.Group], currentLayer):
        for layer, group in groups.items():
            if layer != currentLayer:
                for sprite in sorted(group.sprites(), key = lambda sprite: sprite.rect.y):

                    x = sprite.rect.x - self.pos.x + constants.HALFSCREENSIZE[0]
                    y = sprite.rect.y - self.pos.y + constants.HALFSCREENSIZE[1]
                    img = sprite.image.copy()
                    img.set_alpha(100)
                    surface.blit(img, (x, y))
            else:
                for sprite in sorted(group.sprites(), key = lambda sprite: sprite.rect.y):

                    x = sprite.rect.x - self.pos.x + constants.HALFSCREENSIZE[0]
                    y = sprite.rect.y - self.pos.y + constants.HALFSCREENSIZE[1]

                    surface.blit(sprite.image, (x, y))

if __name__ == "__main__":
    b = Builder()
    b.run()