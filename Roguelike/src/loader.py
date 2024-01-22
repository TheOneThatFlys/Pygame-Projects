import os
import pygame
import csv

class ImageLoader():
    def __init__(self):
        self.assets = {}
        self.loaded = False

    def __getitem__(self, key: str) -> pygame.Surface:
        if not self.loaded: raise Exception("Assets have not been loaded. Run assets.load() first to access images!")
        return self.assets[key]

    def load(self, path, scale: int = 1):
        """
        Loads all images in folder into a dictionary accessed with \"folder.file\".\n
        Scales the images by given scale (default = 1).
        """
        _IGNOREPATHS = ["assets\\fonts"]
        for dirpath, dirnames, filenames in os.walk(path):
            if dirpath in _IGNOREPATHS: continue
            for filename in filenames:
                if filename.endswith(".png"):
                    image = pygame.image.load(os.path.join(dirpath, filename))
                    image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale)).convert_alpha()
                    self.assets[
                        os.path.join(dirpath, filename)
                               .removeprefix(path)
                               .replace(os.path.sep, ".")
                               .removesuffix(".png")[1:]
                    ] = image

        self.loaded = True

    def loadAnimation(self, image: pygame.Surface, frames: int) -> list[pygame.Surface]:
        animations = []
        scale = image.get_width() / frames
        height = image.get_height()
        for i in range(frames):
            animations.append(image.subsurface((i * scale, 0, scale, height)))
        return animations

    def loadAnimationFolder(self, foldername, idleFrames, runFrames, deathFrames) -> dict[str, list[pygame.Surface]]:
        animations = {
            "idle-right": assets.loadAnimation(assets[f"{foldername}.idle-anim"], idleFrames),
            "idle-left": assets.loadAnimation(pygame.transform.flip(assets[f"{foldername}.idle-anim"], True, False), idleFrames),
            "run-right": assets.loadAnimation(assets[f"{foldername}.run-anim"], runFrames),
            "run-left": assets.loadAnimation(pygame.transform.flip(assets[f"{foldername}.run-anim"], True, False), runFrames),
            "death": assets.loadAnimation(assets[f"{foldername}.death-anim"], deathFrames),
        }
        return animations

    def loadTileSet(self, reference: str, tileSize: int) -> list[pygame.Surface]:
        id = 0
        ts = []
        image = self[reference]
        for y in range(0, image.get_height(), tileSize):
            for x in range(0, image.get_width(), tileSize):
                img = image.subsurface((x, y, tileSize, tileSize))
                ts.append(img)
        self.assets[f"{reference}.tileAt"] = ts
        return ts

class MapLoader():
    def __init__(self):
        self.maps = {}

    def __getitem__(self, key: str) -> pygame.Surface:
        return self.maps[key]

    def load(self, path):
        for dirpath, dirnames, filenames in os.walk(path):
            path_key = os.path.join(dirpath).removeprefix(path+os.path.sep)
            self.maps[path_key] = {}
            for filename in filenames:
                if filename.endswith(".csv"):
                    with open(os.path.join(dirpath, filename)) as f:
                        r = csv.reader(f, delimiter=",")
                        map = []
                        for row in r:
                            temp = []
                            for val in row:
                                temp.append(int(val))
                            map.append(temp)
                        self.maps[path_key][filename.removesuffix(".csv")] = map

class FontLoader():
    def __init__(self):
        self.fonts = {}

    def __getitem__(self, key: str) -> pygame.font.Font:
        return self.fonts[key]

    def load(self, path, sizes):
        ttf = ".ttf"
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                if not filename.endswith(ttf): continue
                for size in sizes:
                    key = f"{filename.removesuffix(ttf)}-{size}"
                    self.fonts[key] = pygame.font.Font(os.path.join(dirpath, filename), size)

assets = ImageLoader()
maps = MapLoader()
fonts = FontLoader()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1, 1))
    il = ImageLoader()
    path = os.path.join(os.path.dirname(__file__)[:-4], "assets")
    il.load(path, scale = 5)
    print(path)
    print(il.assets)
    il.loadAnimation(il["player.death-anim"], 6)
