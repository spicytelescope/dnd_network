from gameObjects.Dungeon import Dungeon
from math import *
from random import *
from typing import List, Tuple

import pygame

import config.textureConf as textureConf
from config.mapConf import *
from config.openWorldConf import *
from config.playerConf import PLAYER_SIZE
from config.textureConf import *
from gameController import GameController
from gameObjects.Building import Building
from gameObjects.Chest import Chest
from gameObjects.Ennemy import Ennemy
from gameObjects.NPC import NPC, Seller
from Player.Character import Character
from UI.UI_utils_text import InfoTip


class EnvGenerator:
    def __init__(self, gameController, Map):

        self.Game = gameController
        self.Map = Map
        self.Hero = None

        assert self.Map.id == 1, f"<ERROR> : can't generate env stuff on the WORLD_Map"

        # -------------- GENERATION DATA STRUCTURE ------- #

        self.mainChunkElementsTab = []
        self.mainChunkTextureTab = []
        self.alreadyGeneratedCoor = []
        self.scaleFactor = 1
        self.obstaclesList = []
        self.structObstacleList = []
        self.npc = []
        self.ennemies = []
        self.items = []
        self.chunkCoorGenerated = []
        self.lastCheckEntity = None

        # ------------------ GENERATION SETTINGS ---- #

        self.scopeSquareTreeDefaults = [
            eltValue["spawnRange"]
            for eltName, eltValue in textureConf.WORLD_ELEMENTS["Landscape"].items()
            if "tree" in eltName
        ]
        self.scopeSquareRockDefaults = [
            eltValue["spawnRange"]
            for eltName, eltValue in textureConf.WORLD_ELEMENTS["Landscape"].items()
            if "rock" in eltName
        ]
        self.TreeGenTresholdDefaults = [
            eltValue["spawnTreshold"]
            for eltName, eltValue in textureConf.WORLD_ELEMENTS["Landscape"].items()
            if "tree" in eltName
        ]
        self.RockGenTresholdDefaults = [
            eltValue["spawnTreshold"]
            for eltName, eltValue in textureConf.WORLD_ELEMENTS["Landscape"].items()
            if "rock" in eltName
        ]

        self.envStates = ["Low", "Default", "High"]
        self.envGenerationIndicator = 1

        # ---------------- GENERATION INFO ----------- #

        self.envInfoTip = InfoTip("", self.Game)

    def updateGenerationSettings(self, mode):

        self.envGenerationIndicator += (
            1
            if mode == "up" and self.envGenerationIndicator != len(self.envStates) - 1
            else 0
        )
        self.envGenerationIndicator -= (
            1 if mode == "down" and self.envGenerationIndicator != 0 else 0
        )

        if self.envStates[self.envGenerationIndicator] == "Default":
            parseCountTree = 0
            parseCountRock = 0
            for eltName, eltValue in textureConf.WORLD_ELEMENTS["Landscape"].items():
                if "tree" in eltName:
                    eltValue["spawnRange"] = self.scopeSquareTreeDefaults[
                        parseCountTree
                    ]
                    eltValue["spawnTreshold"] = self.TreeGenTresholdDefaults[
                        parseCountTree
                    ]
                    parseCountTree += 1
                elif "rock" in eltName:
                    eltValue["spawnRange"] = self.scopeSquareRockDefaults[
                        parseCountRock
                    ]
                    eltValue["spawnTreshold"] = self.RockGenTresholdDefaults[
                        parseCountRock
                    ]
                    parseCountRock += 1

        elif self.envStates[self.envGenerationIndicator] == "High":
            for eltName, eltValue in textureConf.WORLD_ELEMENTS["Landscape"].items():
                if "tree" in eltName or "rock" in eltName:
                    eltValue["spawnRange"] //= 2
                    eltValue["spawnTreshold"] //= 2
        elif self.envStates[self.envGenerationIndicator] == "Low":
            for eltName, eltValue in textureConf.WORLD_ELEMENTS["Landscape"].items():
                if "tree" in eltName or "rock" in eltName:
                    eltValue["spawnRange"] *= 2
                    eltValue["spawnTreshold"] *= 2

    def loadMainChunkElementTab(self):
        """method loading all the elementTab and textureTab of the chunk to make 2 centralised representing the mainChunk frames property"""

        # a factor use to take a value from a XbyX array (elementTab) to scale it up to a X*scale by X*scale tab (colorTab)
        self.scaleFactor = self.Map.currentChunkSubdivision // MIN_CHUNK_SUBDIVISON

        self.mainChunkTextureTab = [
            []
            for _ in range(
                len(range(-self.Map.renderDistance, self.Map.renderDistance + 1))
                * self.Map.currentChunkSubdivision
            )
        ]
        self.mainChunkElementsTab = [
            []
            for _ in range(
                len(range(-self.Map.renderDistance, self.Map.renderDistance + 1))
                * MIN_CHUNK_SUBDIVISON
            )
        ]

        for j in range(-self.Map.renderDistance, self.Map.renderDistance + 1):
            for i in range(-self.Map.renderDistance, self.Map.renderDistance + 1):

                chunkCoor = (
                    str(i + self.Map.chunkData["currentChunkPos"][0])
                    + ";"
                    + str(j + self.Map.chunkData["currentChunkPos"][1])
                )

                if chunkCoor not in self.chunkCoorGenerated:
                    self.chunkCoorGenerated.append(chunkCoor)
                else:
                    self.alreadyGeneratedCoor += [
                        (x, y)
                        for x in range(
                            (i + self.Map.renderDistance) * MIN_CHUNK_SUBDIVISON,
                            (i + self.Map.renderDistance + 1) * (MIN_CHUNK_SUBDIVISON),
                        )
                        for y in range(
                            (j + self.Map.renderDistance) * MIN_CHUNK_SUBDIVISON,
                            (j + self.Map.renderDistance + 1) * MIN_CHUNK_SUBDIVISON,
                        )
                    ]

                chunkElementTab = self.Map.chunkData[chunkCoor]["elementTab"]
                chunkTextureTab = self.Map.chunkData[chunkCoor]["textureTab"]

                for k in range(self.Map.currentChunkSubdivision):

                    self.mainChunkTextureTab[
                        (j + self.Map.renderDistance) * self.Map.currentChunkSubdivision
                        + k
                    ] += chunkTextureTab[k]

                for k in range(MIN_CHUNK_SUBDIVISON):

                    self.mainChunkElementsTab[
                        (j + self.Map.renderDistance) * MIN_CHUNK_SUBDIVISON + k
                    ] += chunkElementTab[k]

    def unloadMainChunkElementTab(self):
        """method converting the general arrays of elements/textures representing mainChunk to severals elementsTab / textureTab to keep track of the elements/textures in each chunk"""

        for j in range(-self.Map.renderDistance, self.Map.renderDistance + 1):
            for i in range(-self.Map.renderDistance, self.Map.renderDistance + 1):
                chunkCoor = (
                    str(i + self.Map.chunkData["currentChunkPos"][0])
                    + ";"
                    + str(j + self.Map.chunkData["currentChunkPos"][1])
                )

                iProjected = i + self.Map.renderDistance
                jProjected = j + self.Map.renderDistance
                self.Map.chunkData[chunkCoor]["textureTab"] = [
                    [
                        self.mainChunkTextureTab[y][x]
                        for x in range(
                            iProjected * self.Map.currentChunkSubdivision,
                            (iProjected + 1) * self.Map.currentChunkSubdivision,
                        )
                    ]
                    for y in range(
                        jProjected * self.Map.currentChunkSubdivision,
                        (jProjected + 1) * self.Map.currentChunkSubdivision,
                    )
                ]

                self.Map.chunkData[chunkCoor]["elementTab"] = [
                    [
                        self.mainChunkElementsTab[y][x]
                        for x in range(
                            iProjected * MIN_CHUNK_SUBDIVISON,
                            (iProjected + 1) * MIN_CHUNK_SUBDIVISON,
                        )
                    ]
                    for y in range(
                        jProjected * MIN_CHUNK_SUBDIVISON,
                        (jProjected + 1) * MIN_CHUNK_SUBDIVISON,
                    )
                ]

        # self.mainChunkElementsTab = self.mainChunkElementsTab = []
        self.alreadyGeneratedCoor = []

    def saveToMatrix(self):

        """Save the mainChunkElementTab to a matrix of 0 for obstacle and 1 for floor to walk in, makes the path finding possible"""
        for j in range(len(self.mainChunkElementsTab)):
            for i in range(len(self.mainChunkElementsTab)):
                # print(self.mainChunkElementsTab[j][i])
                self.Map.matrix[j][i] = (
                    1
                    if (
                        type(self.mainChunkElementsTab[j][i]["name"]) == str
                        and "flower" in self.mainChunkElementsTab[j][i]["name"]
                    )
                    or (
                        self.mainChunkElementsTab[j][i]["type"] == None
                        and not self.mainChunkElementsTab[j][i]["structure"]["isBorder"]
                    )
                    else 0
                )
        # with open("matrix.txt", "w") as f:
        #     for j in range(len(self.Map.matrix)):
        #         f.write(("").join(str(self.Map.matrix[j])))
        #         f.write("\n")

    def generateElement(
        self,
        type: str,
        name: str,
        limit: int,
        structureName: str = None,
        specificChunksCoor: List[Tuple[int, int]] = [],
    ) -> int:
        """Generate <limit> times an element identified by his type and his name in the chunks newly discovered by the player (that have not been in the envGenerator yet).
        The element might be generated into a structure.

        An optional parameter <specificChunks> can be passed in, to generate the element on specific chunk in the mainChunk array.

        Return the portion of elements that couldn't be generated on that chunk, so it can the generation of elements can be tracked."""

        if limit == 0:
            return 0  # Case we don't generate nothing, can happen so to optimise memory and time complexity, directly return 0

        assert (
            self.mainChunkElementsTab != [] and self.mainChunkTextureTab != []
        ), f"<ERROR> : this method can't be called without loadMainChunkElementTab() called before"

        generationCount = 0
        pass_count = 0
        passIterations = False

        # Element static ressources
        elt = textureConf.WORLD_ELEMENTS[type][name].copy()
        elt.pop("surf")

        possiblePos = [
            (i, j)
            for i in range(0, len(self.mainChunkElementsTab) - 1, elt["spawnRange"])
            for j in range(0, len(self.mainChunkElementsTab) - 1, elt["spawnRange"])
        ]

        if specificChunksCoor != []:
            current = self.Map.chunkData["currentChunkPos"]
            translatedSpecifChnkCoor = [
                (
                    coorX - current[0] + self.Map.renderDistance,
                    coorY - current[1] + self.Map.renderDistance,
                )
                for coorX, coorY in specificChunksCoor
            ]
            specificValues = []

            for coorX, coorY in translatedSpecifChnkCoor:
                specificValues += [
                    (i, j)
                    for i in range(
                        coorX * self.Map.currentChunkSubdivision,
                        (coorX + 1) * self.Map.currentChunkSubdivision,
                    )
                    for j in range(
                        coorY * self.Map.currentChunkSubdivision,
                        (coorY + 1) * self.Map.currentChunkSubdivision,
                    )
                ]

            possiblePos = [coor for coor in possiblePos if coor in specificValues]

        while len(possiblePos) != 0:
            i, j = possiblePos.pop(random.randrange(len(possiblePos)))

            if (i, j) in self.alreadyGeneratedCoor:
                continue

            scopeGrid = [
                [
                    self.mainChunkElementsTab[j + y][i + x]
                    for x in range(elt["spawnRange"])
                    if 0
                    <= i + x
                    <= (len(self.mainChunkElementsTab) - elt["spawnRange"] - 1)
                ]
                for y in range(elt["spawnRange"])
                if 0
                <= j + y
                <= (len(self.mainChunkElementsTab) - elt["spawnRange"] - 1)
            ]

            scopeGridFiltered = [
                [
                    scopeGrid[y][x]
                    if scopeGrid[y][x]["type"] == None
                    and scopeGrid[y][x]["structure"]["name"] == structureName
                    and not scopeGrid[y][x]["structure"]["isBorder"]
                    and (j + y, i + x)
                    not in [
                        (
                            self.Hero.posMainChunkCenter[0] // self.Map.stepGeneration
                            + k,
                            self.Hero.posMainChunkCenter[1] // self.Map.stepGeneration
                            + l,
                        )
                        for l in range(-SAFE_PLAYER_RANGE, SAFE_PLAYER_RANGE + 2)
                        for k in range(-SAFE_PLAYER_RANGE, SAFE_PLAYER_RANGE + 2)
                    ]
                    else None
                    for x in range(len(scopeGrid[y]))
                ]
                for y in range(len(scopeGrid))
            ]

            # We add the color restriction if this is not generated into a structure
            if structureName == None:

                scopeGridFiltered = [
                    [
                        scopeGridFiltered[y][x]
                        if self.mainChunkTextureTab[(j + y) * self.scaleFactor][
                            (i + x) * self.scaleFactor
                        ]["color"]
                        == elt["spawnTileCode"]
                        else None
                        for x in range(len(scopeGridFiltered[y]))
                    ]
                    for y in range(len(scopeGridFiltered))
                ]

            spawnTileCount = sum(
                [
                    len([elt for elt in scopeGridFiltered[x] if elt != None])
                    for x in range(len(scopeGridFiltered))
                ]
            )

            if passIterations:
                if pass_count == elt["spawnRange"]:
                    pass_count = 0
                    passIterations = False

                else:
                    pass_count += 1
                    continue

            if spawnTileCount >= elt["spawnTreshold"]:

                if generationCount == limit:
                    return limit - generationCount

                # We generate the element on the spawnRange, and as it is one element per spawnRange, if one is spawn we go to the next spawnRange by continuing the loop as pass count does not equal spawnRange

                # We filter again the scopegrid but to keep only the elements needed
                # scopeGridFiltered = [
                #     [elt for elt in scopeGridFiltered[x] if elt != None]
                #     for x in range(len(scopeGridFiltered))
                # ]
                # print(scopeGridFiltered)

                pass_count = 0  # It does not equal one as we want one space more after the generation
                passIterations = True
                generationCount += 1

                if elt["placeholder"]["type"] == "alone":

                    # We need to randomly select on scopeGrid and not ScopeGridFiltered as the index need to remain the same e.g the grid need to be (spawnRange)x(spawnRange)

                    caseSelectedPosY = random.choice(list(enumerate(scopeGridFiltered)))
                    caseSelectedPosX = random.choice(
                        list(enumerate(caseSelectedPosY[1]))
                    )

                    # The while is here to prevent to choose empty array which lead to <ERROR>s
                    # We verify that the randomly selected case is on the elt["spawnTileCode"]

                    # Let's not forget that caseSelectedPosY[0] and caseSelectedPosX[0] are integers in range(len(scopeGrid)). Meed to scale them up in the tab with i and j and then rescale to get the pos in the textureTab

                    while not (
                        scopeGridFiltered[caseSelectedPosY[0]][caseSelectedPosX[0]]
                        != None
                    ):
                        caseSelectedPosY = random.choice(
                            list(enumerate(scopeGridFiltered))
                        )
                        caseSelectedPosX = random.choice(
                            list(enumerate(caseSelectedPosY[1]))
                        )

                    # Getting the Y and X  index
                    caseSelectedPosY = caseSelectedPosY[0]
                    caseSelectedPosX = caseSelectedPosX[0]

                    scopeGridFiltered[caseSelectedPosY][caseSelectedPosX][
                        "value"
                    ] = elt.copy()
                    scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["type"] = type
                    scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["name"] = name

                    if (
                        type == "Landscape"
                        and isinstance(
                            textureConf.WORLD_ELEMENTS[type][name]["surf"], list
                        )
                        and len(textureConf.WORLD_ELEMENTS[type][name]["surf"]) != 0
                    ):
                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX][
                            "surfIndex"
                        ] = random.randrange(
                            0, len(textureConf.WORLD_ELEMENTS[type][name]["surf"])
                        )

                    # ------------------ AFFECTING ENTITY ----------------- #

                    if name == "Chest":

                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["value"][
                            "entity"
                        ] = Chest(self.Game, self.Hero, None)

                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["value"][
                            "onContact"
                        ] = scopeGridFiltered[caseSelectedPosY][caseSelectedPosX][
                            "value"
                        ][
                            "entity"
                        ].show

                    elif name == "Seller":
                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["value"][
                            "entity"
                        ] = Seller(
                            self.Map.chunkData["mainChunk"],
                            random.randint(100, 300),
                            self.Game,
                            self.Hero,
                            random.choice(
                                listdir("./assets/world_textures/NPC/Seller/")
                            ),
                        )

                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["value"][
                            "onContact"
                        ] = scopeGridFiltered[caseSelectedPosY][caseSelectedPosX][
                            "value"
                        ][
                            "entity"
                        ].openInterface

                    elif name == "Villager":
                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["value"][
                            "entity"
                        ] = NPC(
                            self.Map.chunkData["mainChunk"],
                            random.choices(["Talk-only", "Quest"], weights=[1, 2], k=1)[
                                0
                            ],
                            self.Hero,
                            self.Game,
                            random.choice(
                                listdir("./assets/world_textures/NPC/Villager/")
                            ),
                            name,
                        )

                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["value"][
                            "onContact"
                        ] = scopeGridFiltered[caseSelectedPosY][caseSelectedPosX][
                            "value"
                        ][
                            "entity"
                        ].openDialog

                    elif type == "Ennemy":

                        scopeGridFiltered[caseSelectedPosY][caseSelectedPosX]["value"][
                            "entity"
                        ] = Ennemy(
                            self.Game.screen,
                            self.Hero,
                            self.Game,
                            self.Map.envGenerator,
                            name,
                            0,
                            1,
                        )

                elif elt["placeholder"]["type"] == "all":

                    # all type on the placeholder means the scopeGridFiltered = scopeGrid and we blit at the topleft
                    for k in range(elt["spawnRange"]):
                        for l in range(elt["spawnRange"]):
                            scopeGrid[k][l]["value"] = elt.copy()
                            scopeGrid[k][l]["value"]["placeholder"] = elt[
                                "placeholder"
                            ].copy()
                            scopeGrid[k][l]["type"] = type
                            scopeGrid[k][l]["name"] = name

                    if type == "Building":
                        scopeGrid[0][0]["value"]["entity"] = Building(
                            type,
                            name,
                            self.Game,
                            self.Map,
                            self.Hero,
                        )
                    elif type == "Dungeon":
                        scopeGrid[0][0]["value"]["entity"] = Dungeon(
                            name,
                            self.Game,
                            self.Hero,
                            [
                                32,
                                32,
                            ],
                            self.Map,
                            random.randrange(2, int(32 * 32 * 0.01)),
                        )

                    # We give to all the pack the same entity object to reference to
                    for k in range(elt["spawnRange"]):
                        for l in range(elt["spawnRange"]):
                            scopeGrid[k][l]["value"]["entity"] = scopeGrid[0][0][
                                "value"
                            ]["entity"]
                            scopeGrid[k][l]["value"]["onContact"] = scopeGrid[0][0][
                                "value"
                            ]["entity"].show

        # logger.info(f"Generated {type}-{name}")
        return limit - generationCount

    def generateStructure(self, name, number, specificChunksCoor=[]):
        """Generate a structure in the mainChunk map"""

        structTemplate = textureConf.WORLD_ELEMENTS_STRUCTURE[name].copy()
        count = 0
        for j in range(
            len(self.mainChunkElementsTab) - structTemplate["spawnRange"][1]
        ):
            for i in range(
                len(self.mainChunkElementsTab) - structTemplate["spawnRange"][0]
            ):

                scopeGrid = [
                    [
                        self.mainChunkElementsTab[j + y][i + x]
                        for x in range(structTemplate["spawnRange"][0])
                        if 0
                        <= i + x
                        <= (
                            len(self.mainChunkElementsTab)
                            - structTemplate["spawnRange"][0]
                            - 1
                        )
                    ]
                    for y in range(structTemplate["spawnRange"][1])
                    if 0
                    <= j + y
                    <= (
                        len(self.mainChunkElementsTab)
                        - structTemplate["spawnRange"][1]
                        - 1
                    )
                ]

                scopeGridFiltered = [
                    [
                        scopeGrid[y][x]
                        for x in range(len(scopeGrid[y]))
                        if self.mainChunkTextureTab[(j + y) * self.scaleFactor][
                            (i + x) * self.scaleFactor
                        ]["color"]
                        == structTemplate["spawnTileCode"]
                        and scopeGrid[y][x]["type"] == None
                        and scopeGrid[y][x]["structure"]["name"] == None
                    ]
                    for y in range(len(scopeGrid))
                ]

                spawnTileCount = sum(
                    [len(scopeGridFiltered[x]) for x in range(len(scopeGridFiltered))]
                )

                if spawnTileCount >= structTemplate["spawnTreshold"] and count < number:
                    logger.info(f"BLITED AT CHUNK : {specificChunksCoor}")
                    borderCoor = [
                        (x, y)
                        for y in range(len(scopeGrid))
                        for x in range(len(scopeGrid[y]))
                        if x == 0
                        or y == 0
                        or y == len(scopeGrid) - 1
                        or x == len(scopeGrid[y]) - 1
                    ]
                    for _ in range(structTemplate["numberOfEntry"]):
                        # Creating doors
                        borderCoor.pop(random.randrange(len(borderCoor)))

                    count += 1
                    for k in range(len(scopeGrid)):
                        for l in range(len(scopeGrid[k])):
                            scopeGrid[k][l]["structure"] = {
                                "name": name,
                                "borderSurf": structTemplate["borderSurf"],
                            }

                            scopeGrid[k][l]["structure"]["isBorder"] = (
                                True if (l, k) in borderCoor else False
                            )

                    # Generating element in it
                    for eltType in structTemplate["composition"].keys():
                        for eltName, leftToGenerate in structTemplate["composition"][
                            eltType
                        ].items():
                            self.generateElement(
                                eltType,
                                eltName,
                                leftToGenerate,
                                structureName=name,
                                specificChunksCoor=specificChunksCoor,
                            )

    def isColliding(self, baseRect, direction, entity="Player"):
        """return 1 if the Hero collide with an element of the landscape"""

        # We create a special hitbox to the hero to see if there is collision with a direction
        PADDING_CHECKER = (
            self.Hero.normalizedDistance
        )  # amount of pixels between the hero and an obstacle

        # logger.info(f"Pos of the player in the mainChunk : {playerMainChunkTopLeft}")
        # logger.info(f"{entity} : {baseRect}")

        tmpRect = None
        if direction == "right":
            tmpRect = pygame.Rect(
                baseRect.topleft[0],
                baseRect.topleft[1],
                baseRect.size[0] + PADDING_CHECKER,
                baseRect.size[1],
            )
        if direction == "left":
            tmpRect = pygame.Rect(
                baseRect.topleft[0] - PADDING_CHECKER,
                baseRect.topleft[1],
                baseRect.size[0] + PADDING_CHECKER,
                baseRect.size[1],
            )
        if direction == "up":
            tmpRect = pygame.Rect(
                baseRect.topleft[0],
                baseRect.topleft[1] - PADDING_CHECKER,
                baseRect.size[0],
                baseRect.size[1] + PADDING_CHECKER,
            )
        if direction == "down":
            tmpRect = pygame.Rect(
                baseRect.topleft[0],
                baseRect.topleft[1],
                baseRect.size[0],
                baseRect.size[1] + PADDING_CHECKER,
            )

        obstaclesListRects = [
            elt["value"]["rect"]
            for elt in self.obstaclesList
            if elt["type"] != "Ennemy"
        ]

        if tmpRect.collidelist(obstaclesListRects) != -1:

            # if self.Game.debug_mode:
            #     logger.debug(
            #         f"collision with : {self.obstaclesList[tmpRect.collidelist(obstaclesListRects)]['name']}"
            #     )

            if entity == "Player":
                if (
                    self.obstaclesList[tmpRect.collidelist(obstaclesListRects)][
                        "value"
                    ]["entity"]
                    != None
                ):
                    self.obstaclesList[tmpRect.collidelist(obstaclesListRects)][
                        "value"
                    ]["entity"].openable = True

                self.lastCheckEntity = self.obstaclesList[
                    tmpRect.collidelist(obstaclesListRects)
                ]

            return True

        else:
            if (
                entity == "Player"
                and self.lastCheckEntity != None
                and self.lastCheckEntity["value"]["entity"] != None
            ):
                self.lastCheckEntity["value"]["entity"].openable = False

        #  STRUCT HANDLING
        obstacleStructListRect = [
            elt["value"]["rect"] for elt in self.structObstacleList
        ]

        if tmpRect.collidelist(obstacleStructListRect) != -1:
            return True

    def displayWorldStructs(self):

        self.structObstacleList = []

        for j in range(len(self.mainChunkElementsTab)):
            for i in range(len(self.mainChunkElementsTab)):

                elt = self.mainChunkElementsTab[j][i]
                x = (j + i) * (self.Map.stepGeneration * sqrt(2)) // 2
                y = (
                    (j - i) * (self.Map.stepGeneration * sqrt(2)) // 4
                    + self.Map.chunkData["mainChunk"].get_height() // 2
                    - self.Map.stepGeneration * sqrt(2) // 2
                )
                # Case with a tile of a structure
                if (
                    elt["structure"]["name"] != None
                    and textureConf.WORLD_ELEMENTS_STRUCTURE[elt["structure"]["name"]][
                        "surf"
                    ]
                    != None
                ):

                    self.Map.chunkData["mainChunk"].blit(
                        elt["structure"]["borderSurf"], (x, y)
                    )
                    self.Map.chunkData["mainChunk"].blit(
                        textureConf.WORLD_ELEMENTS_STRUCTURE[elt["structure"]["name"]][
                            "surf"
                        ],
                        (x, y),
                    )
                if elt["structure"]["isBorder"]:

                    fenceRect = elt["structure"]["borderSurf"].get_rect(topleft=(x, y))
                    self.structObstacleList.append(
                        {
                            "name": "Struct Border",
                            "value": {"rect": fenceRect, "entity": None},
                        }
                    )

                    self.Map.chunkData["mainChunk"].blit(
                        elt["structure"]["borderSurf"],
                        (x, y),
                    )

    def displayWorldElements(self):
        """Method called when world elements are generated or when the mainChunk is changed to reblit them"""

        self.obstaclesList = []
        self.npc = []
        self.ennemies = []

        for j in range(len(self.mainChunkElementsTab)):
            for i in range(len(self.mainChunkElementsTab)):
                if self.mainChunkElementsTab[j][i]["type"] != None:
                    # Reseting the placeholder's flag to reblit the "all" placeholder flags
                    self.mainChunkElementsTab[j][i]["value"]["placeholder"][
                        "flag"
                    ] = False

        for j in range(len(self.mainChunkElementsTab)):
            for i in range(len(self.mainChunkElementsTab)):

                def standard_vec_into_iso(x, y):
                    x_iso = x + y
                    y_iso = -0.5 * x + 0.5 * y
                    return (x_iso, y_iso)

                x = (j + i) * (self.Map.stepGeneration * sqrt(2)) // 2
                y = (
                    (j - i) * (self.Map.stepGeneration * sqrt(2)) // 4
                    + self.Map.chunkData["mainChunk"].get_height() // 2
                    - self.Map.stepGeneration * sqrt(2) // 2
                )
                # x = (j - i) * self.Map.stepGeneration * sqrt(
                #     2
                # )
                # y = ((j + i) * self.Map.stepGeneration * sqrt(2)) // 4 - self.Map.chunkData["mainChunk"].get_height() // 2 - self.Map.stepGeneration * sqrt(2) / 2

                elt = self.mainChunkElementsTab[j][i]

                if elt["type"] != None:

                    if elt["value"]["placeholder"]["type"] == "alone":
                        # The NPC got a special treatment as they are world elements that needs to be animated
                        if elt["type"] == "NPC" or elt["type"] == "Ennemy":

                            elt["value"]["entity"].init((x, y))
                            if elt["type"] == "NPC":

                                elt["value"]["rect"] = elt["value"][
                                    "entity"
                                ].surf.get_rect(topleft=(x, y))
                                self.npc.append(elt)
                                self.obstaclesList.append(elt)
                            else:
                                self.ennemies.append(elt)
                            continue

                    elif elt["value"]["placeholder"]["type"] == "all":

                        if elt["value"]["placeholder"]["flag"]:
                            continue

                        if not elt["value"]["placeholder"]["flag"]:
                            # Initialise all the flag for unbliting the next one cases of the element's components

                            for l in range(elt["value"]["spawnRange"]):
                                for k in range(elt["value"]["spawnRange"]):
                                    if k == 0 and l == 0:
                                        continue
                                    elif 0 <= j + l < len(
                                        self.mainChunkElementsTab
                                    ) and 0 <= i + k < len(self.mainChunkElementsTab):

                                        if (
                                            self.mainChunkElementsTab[j + l][i + k][
                                                "value"
                                            ]
                                            != None
                                        ):
                                            self.mainChunkElementsTab[j + l][i + k][
                                                "value"
                                            ]["placeholder"]["flag"] = True

                    #         x = (j * tile_width / 2) + (i * tile_width / 2)
                    # y = (i * tile_height / 2) - (j * tile_height / 2)

                    if (
                        elt["type"] == "Landscape"
                        and type(
                            textureConf.WORLD_ELEMENTS[elt["type"]][elt["name"]]["surf"]
                        )
                        == list
                    ):
                        if (
                            len(
                                textureConf.WORLD_ELEMENTS[elt["type"]][elt["name"]][
                                    "surf"
                                ]
                            )
                            != 0
                        ):
                            surfToBlit = textureConf.WORLD_ELEMENTS[elt["type"]][
                                elt["name"]
                            ]["surf"][elt["surfIndex"]]

                            elt["value"]["rect"] = surfToBlit.get_rect(topleft=(x, y))
                            self.Map.chunkData["mainChunk"].blit(
                                surfToBlit,
                                elt["value"]["rect"],
                            )
                            if not "flower" in elt["name"]:
                                self.obstaclesList.append(elt)

                        continue

                    elt["value"]["rect"] = textureConf.WORLD_ELEMENTS[elt["type"]][
                        elt["name"]
                    ]["surf"].get_rect(topleft=(x, y))
                    self.Map.chunkData["mainChunk"].blit(
                        textureConf.WORLD_ELEMENTS[elt["type"]][elt["name"]]["surf"],
                        elt["value"]["rect"],
                    )

                    if not "flower" in elt["name"]:
                        self.obstaclesList.append(elt)

    def showInfoTipElt(self):

        mousePosTranslated = [
            coor + (self.Map.renderDistance * self.Map.CHUNK_SIZE) - offset
            for coor, offset in zip(pygame.mouse.get_pos(), self.Hero.blitOffset)
        ]

        mouseCollideElt = None
        for elt in self.obstaclesList:
            if elt["value"]["rect"].collidepoint(mousePosTranslated):
                mouseCollideElt = elt

        if mouseCollideElt != None:
            interactKey = self.Game.KeyBindings["Interact with an element"]["key"]
            self.envInfoTip.setText(
                f"{mouseCollideElt['name']} {f'- Press [{interactKey}]  to interact with it !' if mouseCollideElt['value']['entity'] != None else ''}"
            )
            self.envInfoTip.show()
            self.Game.cursor.set("interact")
        else:
            self.Game.cursor.set("main")

    def checkInteractableEntities(self, event):

        mousePosTranslated = [
            coor + (self.Map.renderDistance * self.Map.CHUNK_SIZE)
            for coor in pygame.mouse.get_pos()
        ]

        if (
            self.lastCheckEntity != None
            and self.lastCheckEntity["value"]["entity"] != None
            and self.lastCheckEntity["value"]["rect"].collidepoint(mousePosTranslated)
            != -1
            and event.key == self.Game.KeyBindings["Interact with an element"]["value"]
        ):
            self.lastCheckEntity["value"]["onContact"]()

    def showNpc(self):

        for npc in self.npc:
            npc["value"]["entity"].show()

    def showEnnemies(self):

        for ennemy in self.ennemies:
            ennemy["value"]["entity"].show()

    def showItems(self):
        for i, item in enumerate(self.items):
            item.show(self.Game.screen)


class EnvHandler:

    """Class handling the generation of the elements, accordingly to several factors.

    Handle the flag mechanism needed to keep track of what is left to generate in zones.
    """

    def __init__(self, gameController, Map) -> None:

        self.Game = gameController
        self.Map = Map
        self.envGenerator = EnvGenerator(self.Game, self.Map)

        # dict containing : the name of the zone, the flags of the elements/structure to generate in the chunks, a list of chunkCoors
        # template:
        # "ZONE_NAME" : {
        #     "elements": {
        #         "NPC": {
        #             "Seller": 1
        #         }
        #     },
        #     "structures": {
        #         "Village" : 1
        #     },
        #     "chunkCoorList": createChunkCoorListFromRadius((0,0), 4),
        # }
        # The number are the number of times left the elements need to be generated
        self.zones = {}

        self.loadZones()

    def loadZones(self):
        """Load the deterministic generated elements."""
        self.addZone("Init_Zone", DEPART_ZONE)
        self.addZone("Danger Zone", DANGER_ZONE)
        # self.addZone("Init_Zone", ZONE_1)
        # self.addZone("Init_Zone", ZONE_2)

    def addZone(self, zoneName, zoneProperties) -> None:

        name = zoneName
        elements, structures, chunkCoorList = zoneProperties.values()
        self.zones[name] = {
            "elements": elements,
            "structures": structures,
            "chunkCoorList": chunkCoorList,
        }
        logger.info(
            f"Addded zone {name} on chunks : {chunkCoorList} with elements : {elements} and structures {structures}"
        )

    def saveToDebug(self):

        with open("playerMap.txt", "w") as f:
            typeText = ""
            for j in range(len(self.envGenerator.mainChunkElementsTab)):
                line = []
                for elt in self.envGenerator.mainChunkElementsTab[j]:

                    if elt["structure"]["name"] == "Village":
                        for eltVillage in textureConf.WORLD_ELEMENTS_STRUCTURE[
                            elt["structure"]["name"]
                        ]["composition"].keys():
                            if elt["type"] == eltVillage:
                                typeText = f"V, {eltVillage[0]}"
                                break
                            else:
                                typeText = "V, O"

                        line.append(typeText)
                        continue  # Not going through the types as we already gave one

                    # going here means no structure e.g structure = None
                    for eltWorld in textureConf.WORLD_ELEMENTS.keys():
                        if elt["type"] == eltWorld:
                            typeText = elt["type"][0]
                            break
                        else:
                            typeText = "O"
                    line.append(typeText)
                f.write(f"{line}\n")

        with open("playerMapcolor.txt", "w") as f:
            for j in range(len(self.envGenerator.mainChunkElementsTab)):
                line = []
                for elt in self.envGenerator.mainChunkTextureTab[j]:
                    if elt["color"] == GREEN:
                        line.append("G")
                    elif elt["color"] == BEACH:
                        line.append("S")
                    elif elt["color"] == WATER:
                        line.append("W")
                f.write(f"{line}\n")

    def genLandscapesElements(self):
        """Generate elements that can appears at each chunk rendering"""

        for biomeName in BIOME_NAMES:
            for biomeElt in BIOME_LANDSCAPE_NAME:
                elementEntry = f"{biomeName[0].upper() + biomeName[1:]}_{biomeElt}"
                self.envGenerator.generateElement("Landscape", elementEntry, -1)
                self.envGenerator.generateElement("Landscape", elementEntry, -1)

        # elt = textureConf.WORLD_ELEMENTS["Landscape"]["Sand_tree"].copy()
        # self.envGenerator.mainChunkElementsTab[0][0]["value"] = elt.copy()
        # self.envGenerator.mainChunkElementsTab[0][0]["type"] = "Landscape"
        # self.envGenerator.mainChunkElementsTab[0][0]["name"] = "Sand_tree"

    def genRareElements(self):

        for eltType in BUILDING_NAMES_RANDOM_GEN:
            for eltName, genTreshhold in BUILDING_NAMES_RANDOM_GEN[eltType].items():
                if random.uniform(0.0, 1.0) <= genTreshhold:
                    self.envGenerator.generateElement(eltType, eltName, 1)

        for structName, genTreshhold in STRUCTS_NAMES_RANDOM_GEN.items():
            if random.uniform(0.0, 1.0) <= genTreshhold:
                self.envGenerator.generateStructure(structName, 1)

    def zoneChecker(self):
        """Keeps track of what has been generated and on which chunks, generate then the elements or structure."""

        mainChunkCoors = [
            (
                self.Map.chunkData["currentChunkPos"][0] + i,
                self.Map.chunkData["currentChunkPos"][1] + j,
            )
            for j in range(-self.Map.renderDistance, self.Map.renderDistance + 1)
            for i in range(-self.Map.renderDistance, self.Map.renderDistance + 1)
        ]

        for zoneName, zone in self.zones.items():

            chunkCoorsGen = [
                coor for coor in mainChunkCoors if coor in zone["chunkCoorList"]
            ]
            if chunkCoorsGen == []:
                # The player haven't reached the zone yet
                continue
            else:

                logger.info(f"Generating {zoneName}")
                #  Updating the remaining chunk Coors
                zone["chunkCoorList"] = [
                    chunkCoor
                    for chunkCoor in zone["chunkCoorList"]
                    if chunkCoor not in chunkCoorsGen
                ]

                # -------------- ELEMENT GENERATION ---------------- #

                for eltType in zone["elements"]:
                    for eltName, leftToGenerate in zone["elements"][eltType].items():

                        # Generating element and updating it on the self.zones dict to keep track of what is left to generate
                        zone["elements"][eltType][
                            eltName
                        ] = self.envGenerator.generateElement(
                            eltType,
                            eltName,
                            leftToGenerate,
                            specificChunksCoor=chunkCoorsGen,
                        )

                # ----------------- STRUCTURE GENERATION ----------------- #

                for structName, leftToGenerate in zone["structures"].items():
                    zone["structures"][
                        structName
                    ] = self.envGenerator.generateStructure(
                        structName, leftToGenerate, specificChunksCoor=chunkCoorsGen
                    )

    def generateWorldElements(self, fastGen=False):

        self.envGenerator.loadMainChunkElementTab()
        if not fastGen:
            self.zoneChecker()
            # self.genRareElements()
            self.genLandscapesElements()
            # self.saveToDebug()

        self.envGenerator.displayWorldStructs()
        self.envGenerator.displayWorldElements()

        self.envGenerator.saveToMatrix()
        self.envGenerator.unloadMainChunkElementTab()
