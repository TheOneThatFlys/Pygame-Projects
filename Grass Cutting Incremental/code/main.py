# exec(open("C:\\Users\\18.a.yue\\OneDrive - The King's School Grantham\\Year 9\\Music\\James Bond - Template 1\\Thing3\\Grass Cutting Incremental\\code\\startup.py").read(), globals())

# TODO:
# Make code better
# Settings save
# Upgradable offline earnings
# Grass -> different colours?
# Rebirth (maybe implement ^ ?)
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
del os

import pygame

pygame.display.set_mode((685, 500)) # Do this before loading to prevent video errors

from level import Level
from menu import Menu
from loading import grass
from globals_ import dis, currentScreen

class Game():
    def __init__(self):
        self.window = pygame.display.get_surface()
        self.dis = dis
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.menu = Menu()

        pygame.display.set_caption("G R A S S")
        pygame.display.set_icon(pygame.transform.scale(grass, (40, 60)))

        currentScreen.value = "menu"
        self.screens = {
            "menu": self.menu,
            "level": self.level
        }
    
    def run(self):
        running = True
        while running == True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.level.updateSave(forcesave = True)

            self.window.fill((0, 0, 0))
            self.dis.fill((0, 0, 0))
            self.screens[currentScreen.value].run()
            if currentScreen.value == "exit": 
                running = False
            self.window.blit(self.dis, (0, 0))

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()