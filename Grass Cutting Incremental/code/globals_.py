import pygame

class globalVariable():
    def __init__(self):
        self.amount = 0
        self.value = ""

cash = globalVariable()
currentScreen = globalVariable()

# ------------------------------------------------------------------ |

def generateNumberDictionary():
    bigDict = {
        0: "",
        1: "K",
        2: "M",
        3: "B",
        4: "T",
        5: "Qd",
        6: "Qn",
        7: "Sx",
        8: "Sp",
        9: "Oc",
        10: "No",
        11: "Dc"
    }

    index = 11
    for x in range(65, 91):
        for y in range(65, 91):
            index += 1
            bigDict[index] = f"{chr(x)}{chr(y)}"

    return bigDict

bigDict = generateNumberDictionary()

dis = pygame.Surface((685, 500))

grassFieldSize = (500, 500)
upgradePanelSize = (185, 500)
upgradePanelMidX = upgradePanelSize[0] // 2