# Also includes GUI because lazy

from button import Button, ScrollWheelY, TickBox
from loading import *
from utils import customFormat, tempTexture
from globals_ import cash, dis

class Upgrade():
    def __init__(self, x, y, title, description, priceformula, max):
        self.dis = dis
        self.image = upgrade_frame
        self.rect = self.image.get_rect(topleft = (x, y))

        self.titletext = title
        self.description = descriptionfont.render(description, False, (255, 255, 255))
        self.priceformula = priceformula

        self.buyButton = Button(
            self.rect.x + 2 * (self.rect.width//3), 
            self.rect.y + 55, 
            upgrade_button["default"], 
            upgrade_button["hover"], 
            upgrade_button["pressed"], 
            center = True, 
            text=["Buy", buttonfont, (255, 255, 255)]
            )

        self.amount = 0

        self.max = max
        self.isMax = False

    def update(self):
        if self.amount >= self.max:
            self.isMax = True

        self.dis.blit(self.image, self.rect)

        self.title = titlefont.render(f"{self.titletext} ({str(self.amount)})", False, (255, 255, 255))
        self.dis.blit(self.title, self.title.get_rect(center=(self.rect.centerx, self.rect.y + 15)))

        self.dis.blit(self.description, self.description.get_rect(center=(self.rect.centerx, self.rect.y + 35)))
        
        if not self.isMax:
            priceSurf = titlefont.render("$" + customFormat(self.priceformula(self.amount)), False, (255, 255, 255))
        else:
            priceSurf = titlefont.render("MAX", False, (255, 255, 255))

        priceRect = priceSurf.get_rect(center = (self.rect.x + (self.rect.width//3), self.rect.y + 55))
        self.dis.blit(priceSurf, priceRect)

        self.buyButton.update()

        if self.buyButton.isPressed():
            if not self.isMax:
                if cash.amount - self.priceformula(self.amount) >= 0:
                    cash.amount = cash.amount - self.priceformula(self.amount)
                    self.amount += 1

class UpgradePanel():
    def __init__(self, upgradeDict: dict):
        self.dis = dis

        self.scrollWheel = ScrollWheelY(500, 80, 450, 5, 25)
        self.scrollOffset = 0
        self.upgradeDict = upgradeDict

    def getUpgrade(self, upgrade: str) -> Upgrade:
        return self.upgradeDict[upgrade]

    def update(self):
        for _, upgrade in self.upgradeDict.items():
            upgrade.update()

        for i in range(len(self.upgradeDict) + 1):
            self.dis.blit(seperator, (500, (i * 80 + 80) + self.scrollOffset))
        self.dis.blit(seperator, (500, 0)) # Hides scrolling
        self.dis.blit(seperator, (500, 80))

        self.scrollWheel.update()

        dy = -self.scrollWheel.getChange()
        self.scrollOffset += dy
        for _, upgrade in self.upgradeDict.items():
            upgrade.rect.y += dy
            upgrade.buyButton.rect.y += dy

class MenuPanel():
    def __init__(self, settingsDict: dict):
        self.dis = dis

        self.scrollWheel = ScrollWheelY(500, 80, 450, 5, 25)
        self.scrollOffset = 0
        self.settingsDict = settingsDict

    def getSetting(self, setting: str):
        return self.settingsDict[setting]

    def update(self):
        for _, upgrade in self.settingsDict.items():
            upgrade.update()

        for i in range(len(self.settingsDict) + 1):
            self.dis.blit(seperator, (500, (i * 80 + 80) + self.scrollOffset))
        self.dis.blit(seperator, (500, 0)) # Hides scrolling
        self.dis.blit(seperator, (500, 80))

        self.scrollWheel.update()

        dy = -self.scrollWheel.getChange()
        self.scrollOffset += dy
        for _, setting in self.settingsDict.items():
            setting.moveChildren(dy)

grassUpgrades = UpgradePanel({
    "value": Upgrade(500, 85, "Value", "More cash / grass", lambda amount: 10 * 1.2 ** amount, 9999),
    "max": Upgrade(500, 165, "Max Grass", "Increases max grass", lambda amount: 10 * 1.1 ** amount, 8888),
    "speed": Upgrade(500, 245, "Grow Speed", "Increases grow speed", lambda amount: 100 * 1.5 ** amount, 9999),
    "area": Upgrade(500, 325, "Harvest Area", "Increases cursor size", lambda amount: 250 * 1.4 ** amount, 8),
})

roombaUpgrades = UpgradePanel({
    "roomba": Upgrade(500, 85, "\"Smart\" Roomba", "Smartest in the market", lambda _: 10000, 1),
    "speed": Upgrade(500, 165, "Roomba Speed", "Vroom vroom", lambda amount: 10000 * 3 ** amount, 8),
    "turning": Upgrade(500, 245, "Turning Speed", "Roomba turns faster", lambda amount: 15000 * 3 ** amount, 8),
    "chroma": Upgrade(500, 325, "Chroma", "Why?", lambda _: 100000000000000000, 1)
})

rebirthUpgrades = UpgradePanel({
})

menuPanel = MenuPanel({
    "particles": TickBox(525, 120, tickbox["off"], tickbox["on"], "Money particles", descriptionfont, (255, 255, 255), center = True, defaultOn = True, textspacing = 10),
    "fps": TickBox(525, 200, tickbox["off"], tickbox["on"], "FPS counter", descriptionfont, (255, 255, 255), center = True, textspacing = 10)
})

panelButtons = {
    "grass": Button(
        505,
        455,
        grass_panel_button["default"],
        grass_panel_button["hover"],
        grass_panel_button["pressed"],
        ),

    "roomba": Button(
        550,
        455,
        roomba_panel_button["default"],
        roomba_panel_button["hover"],
        roomba_panel_button["pressed"],
        ),

    "rebirth": Button(
        595,
        455,
        rebirth_panel_button["default"],
        rebirth_panel_button["hover"],
        rebirth_panel_button["pressed"],
        ),

    "menu": Button(
        640,
        455,
        menu_button["default"],
        menu_button["hover"],
        menu_button["pressed"]
    )
}
