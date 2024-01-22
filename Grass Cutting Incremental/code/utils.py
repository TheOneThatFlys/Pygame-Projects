import json
import pygame
from math import floor, sqrt, atan2, degrees
from copy import deepcopy
from globals_ import bigDict

def customFormat(number: int | float) -> str:
    originalNumber = deepcopy(number)
    try:
        number = floor(number)
        magnitude = 0
        while number >= 1000.0:
            magnitude += 1
            number = number/1000.0
        return(f'{floor(number*100.0)/100.0}{bigDict[magnitude]}')
    except KeyError:
        return str(originalNumber)
    except OverflowError:
        return "too much"

def getDistance(pos1: tuple[int, int], pos2: tuple[int, int]) -> float:
    "Returns distance between two points in a 2D plane"
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return sqrt(dx ** 2 + dy ** 2)

def getVector2Angle(vector: pygame.math.Vector2) -> float:
    "Returns angle of a vector, assuming 0 is facing upwards, in degrees"
    angle = degrees(atan2(vector.y, vector.x))
    return angle

def saveToFile(path: str, data: dict):
    string = json.dumps(data, sort_keys=True, indent=4)

    with open(path, "w") as f:
        f.write(string)

def loadFromFile(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    
    return data

def hueShift(image: pygame.Surface, amount) -> pygame.Surface:
    pxArr = pygame.PixelArray(image)

    for y in range(image.get_height()):
        for x in range(image.get_width()):
            rgb = image.unmap_rgb(pxArr[y][x])
            colour = pygame.Color(rgb)
            h, s, l, a = colour.hsla
            colour.hsla = (h + amount) % 360, s, l, a
            pxArr[y][x] = colour

    newImage = pxArr.make_surface()
    pxArr.close()
    return newImage

def tempTexture(width: int, height: int) -> pygame.Surface:
    "Returns a null texture of specified dimensions"
    surface = pygame.Surface((width, height))
    surface.fill((180, 0, 180))
    return surface

def loadButtonFolder(folderpath: str, size: tuple[int, int]) -> dict[str, pygame.Surface]:
    "Returns a dict of loaded button images for default, hover, and pressed"
    return {
        "default": pygame.transform.scale(pygame.image.load(folderpath + "\\default.png"), size).convert_alpha(),
        "hover": pygame.transform.scale(pygame.image.load(folderpath + "\\hover.png"), size).convert_alpha(),
        "pressed": pygame.transform.scale(pygame.image.load(folderpath + "\\pressed.png"), size).convert_alpha()
        }

def closeTo(num1: int | float, num2: int | float, uncertainty: int | float) -> bool:
    "Returns true if num1 is in +- uncertainty of num2"
    if num1 == num2: return True 
    return num1 > num2 - uncertainty and num1 < num2 + uncertainty

def getTurningDirection(startAngle: int, targetAngle: int) -> str:
    "Returns the clockwise or anti-clockwise depending on shortest turning direction"

    clockwise = startAngle
    anticlockwise = startAngle
    clockwiseCounter = 0
    anticlockwiseCounter = 0

    while clockwise != targetAngle:
        clockwise -= 1
        clockwiseCounter += 1
        if clockwise < -180:
            clockwise = 180

    while anticlockwise != targetAngle:
        anticlockwise += 1
        anticlockwiseCounter += 1
        if anticlockwise > 180:
            anticlockwise = -180

    if anticlockwiseCounter < clockwiseCounter:
        return "anticlockwise"
    else:
        return "clockwise"

def secondsToFormatted(s: float | int) -> str:
    """
    Returns string formatted: Days Hours Minutes Seconds\n
    Doesn't include values that are 0
    """
    seconds = int(s % 60)
    minutes = int((s // 60 )% 60)
    hours = int((s // (60 *60) ) % 24)
    days = int(s // (60 * 60 * 24))

    awayString = f"{seconds} Seconds"
    if minutes:
        awayString = f"{minutes} Minutes " + awayString
    if hours:
        awayString = f"{hours} Hours " + awayString
    if days:
        awayString = f"{days} Days " + awayString

    return awayString

...