# py "O:\Year 9\Music\James Bond - Template 1\Thing3\Roguelike\src\main.py"

# TODO:
#   - Interactable stuff (with e?)
#   - More rooms 
#   - More weapons
#   - More enemies

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

import constants
from level import Level
from loader import assets, maps, fonts

class Game():
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(constants.SCREENSIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Roguelike Tower")

        assets.load(constants.HOMEPATH + "\\assets", constants.SCALERATIO)
        maps.load(constants.HOMEPATH + "\\maps")
        fonts.load(constants.HOMEPATH + "\\assets\\fonts", constants.FONTSIZES)

        self.level = Level(self.window)

        self.currentScreen = "level"
        self.screens = {
            "level": self.level
        }

        self.font = pygame.font.Font(None, 20)

    def changeScreen(self, screen: str):
        self.currentScreen = screen
    
    def run(self):
        running = True
        while running == True:
            self.clock.tick(constants.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F3:
                        self.level.debugging = not self.level.debugging

            self.window.fill((20, 20, 18))
            self.screens[self.currentScreen].run()
            if self.level.debugging:
                self.window.blit(self.font.render(str(int(self.clock.get_fps())), True, (255, 255, 255)), (5, 5))
            pygame.display.update()

        pygame.quit()

def cleanMapFiles():
    for dirpath, dirname, filenames in os.walk("maps"):
        for filename in filenames:
            if filename.startswith("_"):
                path = os.path.join(dirpath, filename)
                os.rename(path, os.path.join(dirpath, filename[1:]))

if __name__ == "__main__":
    cleanMapFiles()
    game = Game()
    game.run()