import pygame
from globals_ import dis
from copy import deepcopy

class Button():
    """
    Kwargs:\n
    > center: bool\n
    Makes the button centered on coords given instead of topleft\n
    > text: list[text: string, font: pygame.Font, colour: tuple[int, int, int]]\n
    Adds text to the button (not dymanic)\n
    > dynamicText: int\n
    Makes text move with button (only y-axis movement)
    """
    def __init__(self, x, y, image, hoverimg, pressedimg, **kwargs):
        self.dis = dis
        self.pressed = False
        self.returnpressed = False
        self.prevPressed = False

        self.image = image
        self.hoverimg = hoverimg
        self.pressedimg = pressedimg
        self.curImage = self.image
        if kwargs.get('center', None):
            self.rect = self.curImage.get_rect(center=(x, y))
        else:
            self.rect = self.curImage.get_rect(topleft=(x, y))

        self.textList = kwargs.get('text', None)
        if self.textList:
            self.textSurf = self.textList[1].render(self.textList[0], False, self.textList[2])
            self.textRect = self.textSurf.get_rect(center = self.rect.center)

        self.textMovement = kwargs.get('dynamicText', 0)

    def update(self):
        # Buttons are complicated, don't question the logic
        self.returnpressed = False
        self.pressed == False

        mousepos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mousepos):
            self.curImage = self.hoverimg
            if pygame.mouse.get_pressed()[0]:
                self.curImage = self.pressedimg
                self.pressed = True
            else:
                self.pressed = False
        else:
            self.curImage = self.image
            self.pressed = False

        if not self.pressed and self.prevPressed == True:
            self.returnpressed = True

        self.prevPressed = True if self.pressed else False
        
        self.dis.blit(self.curImage, self.rect)
        if self.textList:
            self.textRect = self.textSurf.get_rect(center = (self.rect.centerx, self.rect.centery - 1))
            if self.curImage == self.hoverimg or self.curImage == self.pressedimg: self.textRect.y += self.textMovement
            self.dis.blit(self.textSurf, self.textRect)

    def isPressed(self):
        return self.returnpressed

class ScrollWheelY():
    def __init__(self, x, y, maxY, width, height):
        self.dis = dis

        self.image = pygame.Surface((width, height))
        self.image.fill((255, 255, 255, 100))
        self.rect = self.image.get_rect(topleft = (x, y))

        self.minY = y
        self.maxY = maxY

        self.prevPressed = False
        self.prevPos = 0

    def update(self):
        mousePos = pygame.mouse.get_pos()
        self.prevPos = deepcopy(self.rect.y)
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(mousePos[0], mousePos[1]):
            self.prevPressed = True
            self.rect.centery = mousePos[1]

        elif self.prevPressed and pygame.mouse.get_pressed()[0]: 
            self.rect.centery = mousePos[1]
        else:
            self.prevPressed = False

        if self.rect.y < self.minY:
            self.rect.y = self.minY
        elif self.rect.bottom > self.maxY:
            self.rect.bottom = self.maxY

        self.dis.blit(self.image, self.rect)

    def getChange(self):
        "Returns change in y position"
        return self.rect.y - self.prevPos

    def getValue(self):
        "Returns a value from 0-1 representing the value of the slider"
        return self.rect.y

class TickBox():
    """
    Tickbox with text\n
    Coords are based off of the box location\n
    No dynamic text changes
    """
    def __init__(self, x, y, offimg, onimg, textstr, textfont, textcolour, antialias = False, center = False, textspacing = 0, defaultOn = False):
        self.dis = dis
        
        self.offimg = offimg
        self.onimg = onimg

        self.tickButton = Button(x, y, self.offimg, self.offimg, self.offimg, center = center)
        self.setState(defaultOn)

        self.textSurface = textfont.render(textstr, antialias, textcolour)
        self.textRect = self.textSurface.get_rect(centery = self.tickButton.rect.centery, x = self.tickButton.rect.right + textspacing)

    def getValue(self):
        return self.isOn

    def moveChildren(self, dy):
        self.tickButton.rect.y += dy
        self.textRect.y += dy

    def setState(self, state: bool):
        if state:
            self.isOn = True
            self.tickButton.image = self.onimg
            self.tickButton.hoverimg = self.onimg
            self.tickButton.pressedimg = self.onimg
        else:
            self.isOn = False
            self.tickButton.image = self.offimg
            self.tickButton.hoverimg = self.offimg
            self.tickButton.pressedimg = self.offimg

    def update(self):
        self.tickButton.update()
        self.dis.blit(self.textSurface, self.textRect)

        if self.tickButton.isPressed():
            self.setState(not self.isOn)
            # self.isOn = not self.isOn
