import os
import pygame

FPS = 60
ONE_OVER_FPS = 1 / FPS
SCREENSIZE = (1600, 900)
HALFSCREENSIZE = (SCREENSIZE[0] // 2, SCREENSIZE[1] // 2)
NATIVERESOLUTION = (480, 270)
SCALERATIO = SCREENSIZE[0] // NATIVERESOLUTION[0]
NATIVETILESIZE = 16
SCALEDTILESIZE = SCALERATIO * NATIVETILESIZE

HOMEPATH = os.path.dirname(__file__)[:-4]

FONTSIZES = [16, 32, 48]
BUBBLETEXTCOLOUR = (221, 223, 235)
BUBBLEBGCOLOUR = (32, 33, 38)

DEBUGCOLOURS = {
    "particle": (255, 0, 0),
    "render": (0, 0, 255),
    "collide": (255, 255, 255)
}

FUNCTIONALINDEXES = {
    "collide": 23,
    "player": 48,
    "enemy": 73,
    "trapdoor": 108,
}

KEYBINDS: dict[str, dict[str, int]] = {
    "movement": {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "right": pygame.K_d,
        "left": pygame.K_a,
    },

    "equip": {
        1: pygame.K_1,
        2: pygame.K_2,
    }
}

MAXINTERACTDISTANCE = SCALEDTILESIZE * 2
MAX_PLAYER_IFRAMES = 30

#  ----------------------------- Stats ----------------------------- #

ENEMYSTATS = {
    "skeleton": {
        "speed": 7,
        "damage": 5,
        "health": 50,
    }
}