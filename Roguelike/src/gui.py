import pygame
import constants
from loader import assets, fonts

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, groups, target, length = 64, height = 8, colour = (255, 70, 75)):
        super().__init__(groups["render"], groups["update"])
        self.image = pygame.Surface((length, height))
        self.rect = self.image.get_rect()

        self.target = target

        self.colour = colour
        self.percentage = 1
        self.redrawImage()

    def setPercentage(self, v):
        self.percentage = v
        self.redrawImage()

    def redrawImage(self):
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, self.colour, [0, 0, self.rect.width * self.percentage, self.rect.height])
        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, self.rect.width, self.rect.height], 3)

    def update(self, dt):
        self.rect.y = self.target.bottom + 4
        self.rect.centerx = self.target.centerx

class InteractPopup(pygame.sprite.Sprite):
    def __init__(self, groups, fontobj: pygame.font.Font, text: list[str | tuple], colour, parent):
        super().__init__(groups["ingame-gui"], groups["update"])
        self.font = fontobj
        self.colour = colour
        self.image = self.renderToImage(text)
        self.rect = self.image.get_rect(centerx = parent.rect.centerx, bottom = parent.rect.top - 8)

        self.parent = parent
        parent.child = self

    def renderToImage(self, text: list[str | tuple]):
        curcolour = self.colour
        fontsurfs = []
        for x in text:
            if isinstance(x, tuple):
                curcolour = x
            else:
                fontsurfs.append(self.font.render(x, True, curcolour))

        totalfont = pygame.Surface((sum([surf.get_width() for surf in fontsurfs]), max([surf.get_height() for surf in fontsurfs])), pygame.SRCALPHA)
        w = 0
        for s in fontsurfs:
            totalfont.blit(s, (w, s.get_rect(centery = totalfont.get_height() // 2).y))
            w += s.get_width()

        # image = pygame.Surface((nTiles * constants.SCALEDTILESIZE, constants.SCALEDTILESIZE), pygame.SRCALPHA)

        # nTiles = fontrect.width // constants.SCALEDTILESIZE + 1
        # image.blit(assets["gui.bubble.left"], (0, 0))
        # image.blit(assets["gui.bubble.right"], (constants.SCALEDTILESIZE * (nTiles - 1), 0))
        # for i in range(nTiles - 2):
        #     image.blit(assets["gui.bubble.middle"], (constants.SCALEDTILESIZE * (i + 1), 0))
        

        image = pygame.Surface((totalfont.get_width(), totalfont.get_height()), pygame.SRCALPHA)
        image.blit(totalfont, totalfont.get_rect(center = image.get_rect().center))

        return totalfont.convert_alpha()

    def kill(self):
        self.parent.child = None
        self.parent = None
        super().kill()

class FixedOverlay(pygame.sprite.Sprite):
    def __init__(self, groups, x, y, image, *, center = False, key = None, font: pygame.font.Font = None):
        super().__init__(groups["gui"])
        self.image = image
        self.rect = self.image.get_rect(topleft = (x, y))
        if center: self.rect.center = (x, y)
        self.key = key
        self.font = font

    def setText(self, text, colour):
        self.image = self.font.render(text, True, colour)
        self.rect = self.image.get_rect(topleft = self.rect.topleft)

class FixedBar(FixedOverlay):
    def __init__(self, groups, x, y, width, height, colour):
        super().__init__(groups, x, y, pygame.Surface((width, height)))

        self.percentage = 1
        self.colour = colour

        self.redrawImage()

    def setPercentage(self, v):
        self.percentage = v
        self.redrawImage()

    def redrawImage(self):
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, self.colour, [0, 0, self.rect.width * self.percentage, self.rect.height])
        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, self.rect.width, self.rect.height], 3)

class FadingOverlay(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos, initialAlpha = 60, endAlpha = 0, fadeTime = 60):
        super().__init__(groups["gui"], groups["update"])
        self.image = image

        self.image.set_alpha(initialAlpha)
        self.rect = self.image.get_rect(center = pos)

        self.alpha = initialAlpha
        self.step = (endAlpha - initialAlpha) / fadeTime
        self.life = fadeTime

    def update(self, dt):

        self.alpha += self.step * dt
        self.image.set_alpha(self.alpha)

        self.life -= dt

        if self.life < 0:
            self.kill()

if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((500, 500))
    assets.load("assets", constants.SCALERATIO)
    fonts.load("assets\\fonts", constants.FONTSIZES)
    running = True
    d = {"gui": pygame.sprite.Group(), "update": pygame.sprite.Group()}
    s = pygame.sprite.Sprite()
    s.rect = pygame.Rect(250, 300, 1, 1)
    a = InteractPopup(d, fonts["alagard-32"], "ASDoIHASD!", (68, 68, 73), s)
    while running == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window.fill((255, 255, 255))
        d["gui"].draw(window)
        pygame.display.update()

    pygame.quit()