import pygame
import constants

def scaleCoord(x, y, camera):
    newx = x - camera.pos.x + constants.HALFSCREENSIZE[0]
    newy = y - camera.pos.y + constants.HALFSCREENSIZE[1]

    return (newx, newy)

def scaleRect(rect, camera):
    s = scaleCoord(rect.x, rect.y, camera)
    return pygame.Rect(s[0], s[1], rect.width, rect.height)

def debug(surface, player, camera, group):
    pygame.draw.rect(surface, (0, 255, 0), scaleRect(player.rect, camera), width = 5)
    pygame.draw.rect(surface, (0, 0, 255), scaleRect(player.image.get_rect(bottom=player.rect.bottom, centerx=player.rect.centerx), camera), width = 1)

    for key, value in group.items():
        if key in constants.DEBUGCOLOURS.keys():
            for sprite in value.sprites():
                pygame.draw.rect(surface, constants.DEBUGCOLOURS[key], scaleRect(sprite.rect, camera), width = 1)


if __name__ == "__main__":
    import csv
    data = [[0 for _ in range(20)] for _ in range(20)]
    with open("test.csv", "x") as f:
        w = csv.writer(f)
        w.writerows(data)
        
    with open("test.csv") as f:
        d = []
        lines = f.readlines()
        for l in lines:
            if l != "\n":
                d.append(l)

    with open("test.csv", "w") as f:
        for l in d:
            f.write(l)
