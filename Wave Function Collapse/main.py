import os
import pygame
import random, time
pygame.init()

class Tile():
    def __init__(self, img, edges):
        self.image = img
        self.edges = edges
        self.validUp = []
        self.validRight = []
        self.validDown = []
        self.validLeft = []
    
    def compareEdges(self, a: str, b: str):
        return a[::-1] == b # Compare with reversed string

    def getValid(self, tiles):
        for i in range(len(tiles)-1):
            tile = tiles[i]
            # Compare up
            if self.compareEdges(self.edges[0], tile.edges[2]):
                self.validUp.append(i)
            # Compare right
            if self.compareEdges(self.edges[1], tile.edges[3]):
                self.validRight.append(i)
            # Compare down
            if self.compareEdges(self.edges[2], tile.edges[0]):
                self.validDown.append(i)
            # Compare left
            if self.compareEdges(self.edges[3], tile.edges[1]):
                self.validLeft.append(i)
    
    def getRotated(self, num):
        img = pygame.transform.rotate(self.image, num * 90)
        edges = [0 for _ in range(4)]
        for i in range(len(self.edges)):
            edges[(i + 4 - num) % 4] = self.edges[i]

        return Tile(img, edges)

    def getFlipped(self, dir):
        if dir == "x":
            img = pygame.transform.flip(self.image, True, False)
            edges = [None for _ in range(4)]
            edges[1] = self.edges[3][::-1]
            edges[3] = self.edges[1][::-1]
            edges[0] = self.edges[0][::-1]
            edges[2] = self.edges[2][::-1]
        else:
            img = pygame.transform.flip(self.image, False, True)
            edges = [None for _ in range(4)]
            edges[0] = self.edges[2][::-1]
            edges[2] = self.edges[0][::-1]
            edges[1] = self.edges[1][::-1]
            edges[3] = self.edges[3][::-1]
        return Tile(img, edges)

class Cell():
    def __init__(self, options):
        self.collapsed = False
        self.options = options

def getTiles(images: list[pygame.Surface]) -> list[Tile]:
    """
    Returns tile objects (not rotated) from given list of images, calculating edge rulesets\n
    DOES NOT WORK WITH TILES NOT EXACTLY MATCHED
    """
    tileList = []

    colourkey = {} # Maps colour to string, e.g {(255, 255, 255): "A"}
    curLetter = 33 # Start from "!"" ascii
    imgSize = images[0].get_width()
    for image in images:
        edges = []

        # Look at top edge
        edgeStr = ""
        for x in range(0, imgSize):
            pixelColour = image.get_at((x, 0)) # Get colour of pixels in top edge
            pixelColour = (pixelColour.r, pixelColour.g, pixelColour.b) # Convert colour object to (r, g, b)
            if pixelColour not in colourkey.keys(): # If colour is not assigned a character
                colourkey[pixelColour] = chr(curLetter) # Add character
                curLetter += 1                          # And increment next character to assign
            edgeStr += colourkey[pixelColour] # Add the corresponding letter character to string
        edges.append(edgeStr)

        # Look at right edge
        edgeStr = ""
        for y in range(0, imgSize):
            pixelColour = image.get_at((imgSize - 1, y))
            pixelColour = (pixelColour.r, pixelColour.g, pixelColour.b)
            if pixelColour not in colourkey.keys():
                colourkey[pixelColour] = chr(curLetter)
                curLetter += 1
            edgeStr += colourkey[pixelColour]
        edges.append(edgeStr)

        # Look at bottom edge
        edgeStr = ""
        for x in range(imgSize - 1, -1, -1):
            pixelColour = image.get_at((x, imgSize - 1))
            pixelColour = (pixelColour.r, pixelColour.g, pixelColour.b)
            if pixelColour not in colourkey.keys():
                colourkey[pixelColour] = chr(curLetter)
                curLetter += 1
            edgeStr += colourkey[pixelColour]
        edges.append(edgeStr)

        # Look at left edge
        edgeStr = ""
        for y in range(imgSize - 1, -1, -1):
            pixelColour = image.get_at((0, y))
            pixelColour = (pixelColour.r, pixelColour.g, pixelColour.b)
            if pixelColour not in colourkey.keys():
                colourkey[pixelColour] = chr(curLetter)
                curLetter += 1
            edgeStr += colourkey[pixelColour]
        edges.append(edgeStr)

        tileList.append(Tile(image, edges))

    return tileList

def getImagesFromFolder(filepath: str, size: int, numbered = False):
    imglist = []
    if not numbered:
        for path in os.listdir(filepath):
            imglist.append(
                pygame.transform.scale(pygame.image.load(os.path.join(filepath, path)), (size, size)).convert()
            )
    else:
        imglist = [pygame.transform.scale(pygame.image.load(f"{filepath}{os.sep}{i}.png"), (size, size)).convert() for i in range(len(os.listdir(filepath)))]
    
    return imglist

def getImagesFromTileMap(filepath, imgSize):
    tilemap = pygame.image.load(filepath).convert()
    tilemapSize = tilemap.get_width(), tilemap.get_height()

    imgList = []
    for x in range(0, tilemapSize[0], imgSize):
        for y in range(0, tilemapSize[1], imgSize):
            imgList.append(
                tilemap.subsurface((x, y, imgSize, imgSize))
            )
    return imgList

def getRotated(tiles: list[Tile]) -> list[Tile]:
    "Returns modified list of rotated tiles - removes duplicates"
    newTiles = tiles.copy()
    for tile in tiles:
        for i in range(1, 4): # Rotate 90, 180 and 270 degrees
            newTiles.append(tile.getRotated(i))
    
    return newTiles

def getFlipped(tiles: list[Tile]) -> list[Tile]:
    newTiles = tiles.copy()
    for tile in tiles:
        newTiles.append(tile.getFlipped("x"))
        newTiles.append(tile.getFlipped("y"))
    return newTiles

def removeRepeated(tiles: list[Tile]) -> list[Tile]:
    uniqueTiles = {}
    for tile in tiles:
        concString = "".join(tile.edges)
        uniqueTiles[concString] = tile
    return list(uniqueTiles.values())

def getEmptyCellGrid(numTiles, tileDim):
    return [[Cell([i for i in range(numTiles)]) for _ in range(tileDim)] for _ in range(tileDim)]

def drawGrid(dis, colour, size, tileDim):
    step = size // tileDim
    for x in range(step, size, step):
        pygame.draw.line(dis, colour, (x, 0), (x, size))
        pygame.draw.line(dis, colour, (0, x), (size, x))

def drawCells(dis, grid: list[list[Cell]], tiles, tileSize):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell.collapsed:
                dis.blit(tiles[cell.options[0]].image, (x * tileSize, y  * tileSize))

def checkValid(lst, options):
    returnList = []
    for i in lst:
        if i in options:
            returnList.append(i)
    return returnList

def debugDrawCellEntr(dis, font, grid, tileSize):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            length = len(cell.options)
            if length == 1: continue
            surf = font.render(str(length), True, (100, 100, 100))
            rect = surf.get_rect(center=(x * tileSize + tileSize//2, y  * tileSize + tileSize//2))
            dis.blit(surf, rect)

def pauseDisplay():
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
            clock.tick(10)

def evalGrid(grid: list[list[Cell]], tiles: list[Tile]):
    gridCopy = grid.copy()
    gridCopy = [item for sublist in gridCopy for item in sublist] # Flatten 2d to 1d array

    # Remove all instances of collapsed cells
    gridCopy = list(filter(lambda x: not x.collapsed, gridCopy))
    if len(gridCopy) == 0:
        pauseDisplay() # Pause if all cells are collapsed
        return getEmptyCellGrid(len(tiles), len(grid))

    # Find values with least entropy
    smallest = min([len(x.options) for x in gridCopy])
    leastEntropyCells = list(filter(lambda cell: len(cell.options) <= smallest, gridCopy))

    # Choose cell
    chosenCell = random.choice(leastEntropyCells)
    # Restart if no choices left
    if len(chosenCell.options) == 0:
        print("No available cell choices. Restarting...")
        time.sleep(2)
        return getEmptyCellGrid(len(tiles), len(grid))

    # Choose from options
    choice = random.choice(chosenCell.options)
    chosenCell.collapsed = True
    chosenCell.options = [choice]

    changedCellIndex = [None, None] # x, y
    # Get coords of changed cell
    for y, row in enumerate(grid):
        if chosenCell in row:
            changedCellIndex[1] = y
            changedCellIndex[0] = row.index(chosenCell)
            break

    # Calculate next grid, removing entropy from surrounding cells
    gridSize = len(grid)
    nextGrid = [[None for _ in range(gridSize)] for _ in range(gridSize)]
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell.collapsed:
                nextGrid[y][x] = grid[y][x]
            # Only loop through cells adjacent or diagonal to changed cell - much faster
            elif x > changedCellIndex[0] + 1 or x < changedCellIndex[0] - 1 or y > changedCellIndex[1] + 1 or y < changedCellIndex[1] - 1:
                nextGrid[y][x] = grid[y][x]
            else:
                options = [i for i in range(len(tiles))] # Start with all options availiable

                # Up
                if y > 0:
                    neighbourCell = grid[y - 1][x] # Get cell thats above
                    validOptions = []
                    for option in neighbourCell.options: # Go through available options that neighbour could be
                        validOptions += tiles[option].validDown # Add all the valid options
                    options = checkValid(options, validOptions) # Remove options that aren't valid

                # Right
                if x < gridSize - 1:
                    neighbourCell = grid[y][x + 1]
                    validOptions = []
                    for option in neighbourCell.options:
                        validOptions += tiles[option].validLeft
                    options = checkValid(options, validOptions)
                
                # Down
                if y < gridSize - 1:
                    neighbourCell = grid[y + 1][x]
                    validOptions = []
                    for option in neighbourCell.options:
                        validOptions += tiles[option].validUp
                    options = checkValid(options, validOptions)

                # Left
                if x > 0:
                    neighbourCell = grid[y][x - 1]
                    validOptions = []
                    for option in neighbourCell.options:
                        validOptions += tiles[option].validRight
                    options = checkValid(options, validOptions)

                nextGrid[y][x] = Cell(options)
    return nextGrid

def main():
    # Pygame init stuff
    pygame.display.set_caption("Wave Function Collapse")
    clock = pygame.time.Clock()

    # Configs
    tileDim = 25 # Tiles per row / col
    path = "tilesets\\circuit"
    tileSize = 28

    size = tileDim * tileSize # Size of window

    dis = pygame.display.set_mode((size, size))

    # Load images

    images = getImagesFromFolder(path, tileSize)

    tiles = getTiles(images)
    tiles.append(tiles[-1])

    tiles = getFlipped(tiles)
    tiles = getRotated(tiles)
    tiles = removeRepeated(tiles)

    for tile in tiles:
        tile.getValid(tiles)

    # Stuff
    grid = getEmptyCellGrid(len(tiles), tileDim)

    # Main Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = getEmptyCellGrid(len(tiles), tileDim)

        grid = evalGrid(grid, tiles)

        # Rendering
        dis.fill((0, 0, 0))
        drawGrid(dis, (100, 100, 100), size, tileDim)
        drawCells(dis, grid, tiles, tileSize)
        debugDrawCellEntr(dis, pygame.font.Font(None, 20), grid, tileSize)

        pygame.display.update()

        clock.tick(60)
    pygame.quit()

main()