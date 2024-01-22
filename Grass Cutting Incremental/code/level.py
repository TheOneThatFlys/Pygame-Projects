import pygame
from time import time
from grass import Controller
from cursor import Cursor
from particles import MoneyParticle
from tractor import Tractor
from upgrade import grassUpgrades, roombaUpgrades, rebirthUpgrades, panelButtons, menuPanel
from popups import EarningsPopup
from loading import font, panel, titlefont, path, upgrade_frame, grass_overlay, grass_bg, panel_button_bg
from globals_ import cash, dis, currentScreen
from utils import customFormat, saveToFile, loadFromFile, secondsToFormatted

class Level():
    def __init__(self):
        self.dis = dis
        self.prevTime = time()

        self.visibleSprites = customDraw()
        self.grassSprites = pygame.sprite.Group()
        self.particleSprites = pygame.sprite.Group()
        self.popupGUIs = pygame.sprite.Group()
        self.groups = {"render": self.visibleSprites, "grass": self.grassSprites, "particles": self.particleSprites, "popups": self.popupGUIs}

        self.grassController = Controller(self.groups, (0, 0), (500, 500))
        self.cursor = Cursor(self.groups)
        self.tractor = None

        self.grassOverlay = grass_overlay

        self.upgradePanels = {"grass": grassUpgrades, "roomba": roombaUpgrades, "rebirth": rebirthUpgrades, "menu": menuPanel}
        self.currentPanel = "grass"
        self.upPanel = panel
        self.moneyPanel = upgrade_frame

        self.saveCounter = 0
        self.saveInterval = 60 * 30

        lastTimeOpened = self.load()

        self.displayEarningsBox(lastTimeOpened)

    def getGrassValue(self):
        return (grassUpgrades.getUpgrade("value").amount + 1) * (2 ** (grassUpgrades.getUpgrade("value").amount // 10))

    def getCut(self):
        displayParticles = menuPanel.getSetting("particles").isOn

        for grass in self.groups["grass"]:
            collect = False
            if grass.rect.colliderect(self.cursor.rect):
                collect = True
            else:
               if self.tractor:
                    if grass.rect.colliderect(self.tractor.rect):
                        collect = True

            if collect:
                self.grassController.killGrass(grass)
                grassValue = self.getGrassValue()
                if displayParticles: MoneyParticle(self.groups, grass.rect.centerx, grass.rect.centery, grassValue)
                cash.amount += grassValue

    def calcUpgrades(self):
        self.grassController.max = 10 + grassUpgrades.getUpgrade("max").amount
        self.cursor.setSize(5 + 5 * grassUpgrades.getUpgrade("area").amount)

        if not self.tractor and roombaUpgrades.getUpgrade("roomba").amount == 1:
            self.tractor = Tractor(self.groups, 250, 250)

    def renderGUI(self):
        self.dis.blit(self.upPanel, (500, 0))
        self.dis.blit(panel_button_bg, (500, 450))

        # Upgrade Panel
        for key, button in panelButtons.items():
            button.update()
            if button.isPressed():
                self.currentPanel = key
        self.upgradePanels[self.currentPanel].update()

        # Rendering cash text
        surf = font.render("$" + customFormat(cash.amount), False, (255, 255, 255))
        surf = pygame.transform.scale(surf, (surf.get_width() * 1, surf.get_height() * 1))
        rect = surf.get_rect(center=(600, 40))
        self.dis.blit(self.moneyPanel, (500, 5))
        self.dis.blit(surf, rect)

        # Grass overlay
        self.dis.blit(self.grassOverlay, (0, 0))

        # Grass limit text
        a = titlefont.render(f"{len(self.grassSprites)}/{self.grassController.max}", False, (255, 255, 255))
        b = a.get_rect(topleft = (10, 475))
        self.dis.blit(a, b)

        # FPS counter
        if menuPanel.getSetting("fps").isOn:
            c = titlefont.render(f"FPS: {int(1 / (time() - self.prevTime))}", False, (255, 255, 255))
            d = a.get_rect(topleft = (10, 10))
            self.dis.blit(c, d)
        self.prevTime = time()

        self.popupGUIs.update()

    def displayEarningsBox(self, lastTime):
        timeAway = time() - lastTime
        if timeAway < 2: # Don't display if not enough time closed
            return

        # Calculate money earned
        grassProduced = ((grassUpgrades.getUpgrade("speed").amount // 60) + (grassUpgrades.getUpgrade("speed").amount % 60)) * timeAway
        moneyEarned = grassProduced * (self.getGrassValue() * 0.5)
        cash.amount += moneyEarned
        awayString = secondsToFormatted(timeAway)
        EarningsPopup(self.groups, awayString, moneyEarned)

    def updateParticles(self):
        self.groups["particles"].update()
        self.groups["particles"].draw(self.dis)

    def updateSave(self, forcesave = False):
        self.saveCounter += 1
        if self.saveCounter >= self.saveInterval or forcesave == True:
            self.saveCounter = 0
            data = {
                "money": cash.amount,
                "last-save": time(),
                "upgrades": {},
                "settings": {}
                }
            for panelName, upgrades in self.upgradePanels.items():
                if panelName == "menu": continue # Skip menu
                tempDict = {}
                for key, item in upgrades.upgradeDict.items():
                    tempDict[key] = item.amount
                data["upgrades"][panelName] = tempDict

            for name, setting in menuPanel.settingsDict.items():
                data["settings"][name] = setting.getValue()

            saveToFile(path + "saves\\save.json", data)

    def load(self):
        data = loadFromFile(path + "saves\\save.json")
        cash.amount = data["money"]
        for section, item in data["upgrades"].items():
            for upgrade, amount in item.items():
                self.upgradePanels[section].getUpgrade(upgrade).amount = amount
        
        for name, setting in data["settings"].items():
            menuPanel.settingsDict[name].setState(setting)
        try:
            return data["last-save"]
        except:
            return time()

    def run(self):
        #Caluculations
        self.updateSave()
        self.grassController.update()
        self.getCut()
        self.calcUpgrades()

        #Rendering / updating
        self.dis.blit(grass_bg, (0, 0))
        self.groups["render"].yDraw()
        self.updateParticles()
        if self.tractor: self.tractor.update()
        self.renderGUI()
        self.cursor.update()

class customDraw(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.dis = dis

    def yDraw(self):
        sortedSprites = self.sprites()
        sortedSprites.sort(key=lambda sprite: sprite.rect.y)
        for sprite in sortedSprites:
            self.dis.blit(sprite.image, sprite.rect)