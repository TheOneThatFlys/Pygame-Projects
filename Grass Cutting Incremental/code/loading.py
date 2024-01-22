# Pre load all assets in one place :)

import pygame
from time import time
from utils import loadButtonFolder

start = time()
pygame.init()

# Add actual path to relative as ./ doesn't work sometimes
path = __file__[:-15]

# Menu
menu_bg = pygame.transform.scale(pygame.image.load(path + "assets\\gui\\menu_bg.png"), (685, 500)).convert()
play_button = loadButtonFolder(path + "assets\\gui\\buttons\\play", (216, 84))
exit_button = loadButtonFolder(path + "assets\\gui\\buttons\\back", (80, 80))

# Popups
popup_bg = pygame.transform.scale(pygame.image.load(path + "assets\\gui\\popup_bg.png"), (400, 250)).convert()

# Fonts
font = pygame.font.Font(path + "assets\\misc\\DisposableDroidBB.ttf", 32)
titlefont = pygame.font.Font(path + "assets\\misc\\DisposableDroidBB.ttf", 20)
descriptionfont = pygame.font.Font(path + "assets\\misc\\DisposableDroidBB.ttf", 16)
buttonfont = pygame.font.Font(path + "assets\\misc\\DisposableDroidBB.ttf", 11)

# Grass things
grass = pygame.transform.scale(pygame.image.load(path + "assets\\objects\\grass.png"), (5, 5)).convert_alpha()
grass_bg = pygame.transform.scale(pygame.image.load(path + "assets\gui\\grass\\grass_bg.png"), (500, 500)).convert()
grass_overlay = pygame.transform.scale(pygame.image.load(path + "assets\\gui\\grass\\grass_overlay.png"), (500, 500)).convert_alpha()

# Upgrade GUI
panel = pygame.transform.scale(pygame.image.load(path + "assets\\gui\\panel_bg.png"), (185, 500)).convert()
panel_button_bg = pygame.transform.scale(pygame.image.load(path + "assets\\gui\\panel_button_bg.png"), (185, 50)).convert()
seperator = pygame.transform.scale(pygame.image.load(path + "assets\\gui\\seperator.png"), (185, 5)).convert_alpha()
upgrade_frame = pygame.transform.scale(pygame.image.load(path + "assets\\gui\\upgrade_frame\\upgrade_frame.png"), (185, 75)).convert_alpha()

# Buttons
upgrade_button = loadButtonFolder(path + "assets\\gui\\buttons\\upgrade_generic", (32, 16))
grass_panel_button = loadButtonFolder(path + "assets\\gui\\buttons\\grass_panel", (40, 40))
roomba_panel_button = loadButtonFolder(path + "assets\\gui\\buttons\\roomba_panel", (40, 40))
rebirth_panel_button = loadButtonFolder(path + "assets\\gui\\buttons\\rebirth_panel", (40, 40))
menu_button = loadButtonFolder(path + "assets\\gui\\buttons\\menu", (40, 40))
popup_close_button = loadButtonFolder(path + "assets\\gui\\buttons\\popup_close", (60, 35))

# TickBoxes
tickbox = {
    "off": pygame.transform.scale(pygame.image.load(path + "assets\\gui\\tickbox\\off.png"), (25, 25)).convert(),
    "on": pygame.transform.scale(pygame.image.load(path + "assets\\gui\\tickbox\\on.png"), (25, 25)).convert(),
}

# Roomba
roomba = {
    "roomba": pygame.transform.scale(pygame.image.load(path + "assets\\objects\\roomba\\roomba.png"), (32, 32)).convert_alpha(),
    "colour": pygame.transform.scale(pygame.image.load(path + "assets\\objects\\roomba\\roomba_colour.png"), (32, 32)).convert_alpha()
}

print(f"Finished loading in {time()-start} seconds!")