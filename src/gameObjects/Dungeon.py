import math
import os
import random
import time

import config.HUDConf as HUDConf
import config.mapConf as mapConf
import config.textureConf as textureConf
import pygame
import urizen as uz
from config import ennemyConf, playerConf
from config.openWorldConf import CORRIOR_PADDING, DUNGEON_FOG
from config.playerConf import BASE_HITBOX_ZOOMED, MAX_TEAM_LENGH
from pygame.constants import *
from saves.savesController import SaveController
from UI.menuClass import PauseMenu
from utils.utils import logger

from gameObjects.Chest import Chest
from gameObjects.Ennemy import Ennemy


class Dungeon:
    def __init__(
        self, name, gameController, Hero, mapTileSize, Map, nChest=0, nLevels=1
    ) -> None:

        self.Game = gameController
        self.Hero = Hero
        self.Map = Map
        self.Game = gameController
        self.PauseMenu = PauseMenu(self.Game, self.Map, self.Hero, SaveController(), self.Game.heroesGroup)
        self.openable = False
        self.open = False
        self.firstOpen = True

        self.type = "Dungeon"
        self.name = name
        self.safeRange = 4  # Range around the dungeon entry without ennemies
        self.nChest = nChest
        self.bossGenerated = False
        self.nLevels = nLevels
        self.actualLevelsGenerated = 0
        self.portalsTiles = []

        # -------------- FOG ---------------- #
        # Map tiles discovering state to alpha key

        self.FOG_PADDING = 0
        if (self.Game.WINDOW_SIZE[0] // 64) % 2 == 0:
            self.FOG_PADDING = 64 // 2
        self.fogSurf = pygame.Surface(
            (
                self.Game.WINDOW_SIZE[0] + self.FOG_PADDING,
                self.Game.WINDOW_SIZE[1] + self.FOG_PADDING,
            ),
            SRCALPHA,
        )

        # ---------- MAP SETTINGS ----------- #

        self.MAP_TILE_SIZE = mapTileSize
        self.MAP_SIZE = [12 * mapTileDim for mapTileDim in self.MAP_TILE_SIZE]

        self.dungeonSurf = None
        self.tab = [
            ["|" for _ in range(self.MAP_SIZE[0] // 12)]
            for __ in range(self.MAP_SIZE[1] // 12)
        ]
        self.elementTab = [
            [
                {
                    "entity": None,
                    "onContact": lambda: None,
                }
                for _ in range(self.MAP_SIZE[0] // 12)
            ]
            for __ in range(self.MAP_SIZE[1] // 12)
        ]
        self.visitedTiles = []
        self.ennemies = []
        self.items = []
        self.obstaclesList = []
        self.lastCheckEntity = {"entity": None, "rect": None, "onContact": None}

        # --------------- MiniMap ---------------- #

        self.layout = pygame.transform.scale(
            HUDConf.PLAYER_ICON_SLOT,
            (self.Game.resolution // 4, self.Game.resolution // 4),
        )
        self.miniMapBlitPoint = [self.Game.resolution - self.layout.get_width(), 0]
        self.layoutRect = self.layout.get_rect(topleft=self.miniMapBlitPoint)
        self.miniMapSurf = None

        #  Extended map

        # Player Icon
        self.playerIcon = playerConf.CLASSES[self.Hero.classId]["icon"]
        # self.playerIconRect = self.playerIcon.get_rect(center=self.rect.center)

        self.extendedSurf = pygame.transform.scale(
            mapConf.EXTENDED_MINIMAP_BG,
            (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
        )
        self.zoomValue = self.extendedSurf.get_size()
        self.offsetZoom = self.extendedSurf.get_size()

        self.extendedRect = self.extendedSurf.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.TOPLEFT_CHUNK_BLIT = self.extendedRect.topleft

        self.playerIconExtendedRect = self.playerIcon.get_rect(
            center=self.extendedRect.center
        )

        self.extendedMapLayout = pygame.transform.scale(
            mapConf.EXTENDED_MAP_LAYOUT,
            (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
        )
        self.ZOOM_SAMPLE = [int(elt * 0.3) for elt in self.extendedSurf.get_size()]

        # ------------------ Camera ----------------- #

        self.playerCurrentTile = []

        self.camera = {}
        self.cameraRect = None

        # ---------------- Torchs --------------- #
        self.torchRects = []
        self.lastAnimatedTorch = time.time()
        self.deltaTorch = 1 / len(
            textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"]["torchs"]
        )
        self.torchIndex = 0

        # ------------ Portal ---------------- #

        self.portalRect = None
        self.lastAnimatedPortal = time.time()
        self.deltaPortal = 1 / len(textureConf.DUNGEON_PORTAL_IDLE)
        self.portalIndex = 0

    def transition(self, name, frames, animationTime):

        if name == "open":
            if self.openable:
                self.bg = self.Game.screen.copy()
                self.open = True
                self.Game.enterBuilding()

                self.Hero.currentBuilding = self

                if self.firstOpen:
                    for _ in range(self.nLevels):
                        self.loadMap()

                    self.firstOpen = False
            else:
                return

        elif name == "close":
            self.open = False
            self.Game.goToOpenWorld()

        for frame in frames:
            rect = frame.get_rect(
                center=(self.Game.resolution // 2, self.Game.resolution // 2)
            )
            self.Game.screen.blit(self.bg, (0, 0))
            self.Game.screen.blit(frame, rect)
            self.Game.show()
            time.sleep(animationTime / len(frames))

        self.Game.screen.blit(self.bg, (0, 0))

        # Resetting Hero movement
        self.Hero.XDistanceToTarget = 0
        self.Hero.YDistanceToTarget = 0
        self.Hero.targetPos = self.Hero.pos

        self.Game.musicController.setMusic("dungeon")

    def update(self, dx=0, dy=0):
        """
        Handle the bliting of the surf, according to its limits.
        """

        # Updating camera center
        self.camera["pos"][0] += dx
        self.camera["pos"][1] += dy
        self.cameraRect = pygame.Surface(self.camera["size"]).get_rect(
            center=self.camera["pos"]
        )

        self.playerCurrentTile = [
            coor // 64 for coor in [self.Hero.buildingPosX, self.Hero.buildingPosY]
        ]

    def showTab(self):
        for j in range(len(self.tab)):
            for i in range(len(self.tab[j])):
                print(self.tab[j][i], end="")
            print("")

    def loadMap(self):

        self.actualLevelsGenerated += 1
        # tile size 12 on the generator

        WALL_COLOR = (136, 102, 68, 255)
        FLOOR_COLOR = (0, 0, 0, 255)

        Map_IMG = uz.dungeon_bsp_tree(self.MAP_TILE_SIZE[0], self.MAP_TILE_SIZE[1], 10)
        uz.vg_tiled(Map_IMG, filepath="tmpDungeon.png", show=False)
        tileMap = pygame.image.load("tmpDungeon.png")

        # ---------------- FLOOR AND WALL/OTHER ----------------- #

        for j in range(0, self.MAP_SIZE[1], 12):
            for i in range(0, self.MAP_SIZE[0], 12):

                surf = tileMap.subsurface(pygame.Rect(i, j, 12, 12))
                surf_color_tab = [
                    surf.get_at((x, y))
                    for x in range(surf.get_width())
                    for y in range(surf.get_height())
                ]
                color = WALL_COLOR if WALL_COLOR in surf_color_tab else FLOOR_COLOR
                if color == WALL_COLOR:
                    self.tab[j // 12][i // 12] = "|"
                elif color == FLOOR_COLOR:
                    self.tab[j // 12][i // 12] = "."

        # ---------------- ENTRY ------------------ #

        self.showTab()

        self.entryTile = [
            random.randrange(len(self.tab[0])),
            random.randrange(len(self.tab)),
        ]
        scopeGridEntry = [
            self.tab[self.entryTile[1] + l][self.entryTile[0] + k]
            if 0 <= self.entryTile[1] + l < len(self.tab)
            and 0 <= self.entryTile[0] + k < len(self.tab[0])
            else "|"
            for l in range(-1, 2)
            for k in range(-1, 2)
        ]

        while (
            self.tab[self.entryTile[1]][self.entryTile[0]] != "."
            or "|" not in scopeGridEntry
        ):
            self.entryTile = [
                random.randrange(len(self.tab[0])),
                random.randrange(len(self.tab)),
            ]
            scopeGridEntry = [
                self.tab[self.entryTile[1] + l][self.entryTile[0] + k]
                if 0 <= self.entryTile[1] + l < len(self.tab)
                and 0 <= self.entryTile[0] + k < len(self.tab[0])
                else "|"
                for l in range(-1, 2)
                for k in range(-1, 2)
            ]

        self.tab[self.entryTile[1]][self.entryTile[0]] = "E"
        for signx, signy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            if (
                0 <= self.entryTile[1] + signy < len(self.tab)
                and 0 <= self.entryTile[0] + signx < len(self.tab[0])
                and self.tab[self.entryTile[1] + signy][self.entryTile[0] + signx]
                == "|"
            ):
                self.tab[self.entryTile[1] + signy][self.entryTile[0] + signx] = "D"
                break

        self.enterPoint = [coor * 64 for coor in self.entryTile]

        # CAMERA
        self.camera = {
            "pos": [coor + 32 for coor in self.enterPoint],  # center
            "size": self.Game.WINDOW_SIZE,
        }
        self.cameraRect = pygame.Surface(self.camera["size"]).get_rect(
            center=self.camera["pos"]
        )

        # PLAYER POS
        self.Hero.buildingPosX, self.Hero.buildingPosY = self.camera["pos"]
        self.playerCurrentTile = self.entryTile

        # Spawning ennemies
        already_gen_Coor = []
        total = 0
        current = 0
        BOSS_RANGE = (
            max(self.MAP_TILE_SIZE) // 3
        )  # min number of tile to spawn the boss

        # ------------------ ENNEMY ------------- #

        for j in range(0, len(self.tab)):
            for i in range(0, len(self.tab[j])):

                if (i, j) not in already_gen_Coor:
                    scopeGrid = [
                        self.tab[j + l][i + k]
                        if 0 <= j + l < len(self.tab) and 0 <= i + k < len(self.tab[0])
                        else "|"
                        for l in range(
                            -ennemyConf.ENNEMY_SPAWN_RANGE[self.Game.difficultyId],
                            ennemyConf.ENNEMY_SPAWN_RANGE[self.Game.difficultyId] + 1,
                        )
                        for k in range(
                            -ennemyConf.ENNEMY_SPAWN_RANGE[self.Game.difficultyId],
                            ennemyConf.ENNEMY_SPAWN_RANGE[self.Game.difficultyId] + 1,
                        )
                    ]
                    if (
                        all([elt == "." for elt in scopeGrid])
                        and math.sqrt(
                            (i - self.entryTile[0]) ** 2 + (j - self.entryTile[1]) ** 2
                        )
                        >= self.safeRange
                    ):
                        total += 1
                        if random.uniform(0, 1) <= (
                            ennemyConf.ENNEMY_DUNGEON_PROB
                            + (1 - ennemyConf.ENNEMY_DUNGEON_PROB)
                            * (self.Game.difficultyId + 1)
                            / len(self.Game.difficultyModes) # if the maximum level of difficulty is set, all the mobs spawn
                        ):
                            current += 1
                            self.tab[j][i] = "X"
                            already_gen_Coor.append((i, j))
                            if (
                                not self.bossGenerated
                                and math.sqrt(
                                    (j - self.entryTile[1]) ** 2
                                    + (i - self.entryTile[0]) ** 2
                                )
                                >= BOSS_RANGE
                            ):
                                if self.nLevels == self.actualLevelsGenerated:
                                    self.tab[j][i] = "B"
                                    self.bossGenerated = True
                                else:
                                    self.tab[j][i] = "MB"
                                self.tab[j + random.choice([-1, 1])][
                                    i + random.choice([-1, 1])
                                ] = "P"
                                self.bossGenerated = True

                            else:
                                self.tab[j][i] = "X"

        logger.debug(
            f"[PROBA : {ennemyConf.ENNEMY_DUNGEON_PROB*100}%] - ENNEMY GENERATION ACTUAL RATE : {round((current/total)*100,2)}% ({current}/{total})"
        )

        # ------------ WALLS --------------- #
        for j in range(0, len(self.tab)):
            for i in range(0, len(self.tab[0])):
                if j == 0 and self.tab[j + 1][i] != "|":
                    self.tab[j][i] = "#"
                if j < len(self.tab) - 2:
                    if all([self.tab[j + k][i] == "|" for k in range(3)]):
                        self.tab[j][i] = "#"
                    if (
                        0 < j
                        and self.tab[j][i] == "|"
                        and self.tab[j + 1][i] not in [" ", "|", "#"]
                        and self.tab[j - 1][i] not in [" ", "|", "#"]
                    ):
                        self.tab[j][i] = "#"

                elif self.tab[j][i] == "|":
                    self.tab[j][i] = "#"

        # --------- VOID AND CORRIDORS --------- #
        for j in range(0, len(self.tab)):
            for i in range(0, len(self.tab[0])):
                if all(
                    [
                        self.tab[j + k][i + l] == "#" or self.tab[j + k][i + l] == " "
                        for k in range(-1, 2)
                        for l in range(-1, 2)
                        if 0 <= j + k < len(self.tab) and 0 <= i + l < len(self.tab[0])
                    ]
                ):
                    self.tab[j][i] = " "

                horizontal_scope = [
                    self.tab[j][i + k]
                    for k in range(-1, 2)
                    if 0 <= i + k < len(self.tab[0])
                ]
                vertical_scope = [
                    self.tab[j + l][i]
                    for l in range(-1, 2)
                    if 0 <= j + l < len(self.tab)
                ]
                if (
                    len(horizontal_scope) == 3
                    and horizontal_scope[1] in [".", "E"]
                    and horizontal_scope[0] in ["#", "|", "D"]
                    and horizontal_scope[2] in ["#", "|", "D"]
                ):
                    self.tab[j][i + 1] = "RC|" if self.tab[j][i + 1] == "|" else "RC#"
                    self.tab[j][i - 1] = "LC|" if self.tab[j][i - 1] == "|" else "LC#"
                if (
                    len(vertical_scope) == 3
                    and vertical_scope[1] in [".", "E"]
                    and vertical_scope[0] in ["#", "|", "D"]
                    and vertical_scope[2] in ["#", "|", "D"]
                ):
                    self.tab[j + 1][i] = "BC|" if self.tab[j + 1][i] == "|" else "BC#"
                    self.tab[j - 1][i] = "TC|" if self.tab[j - 1][i] == "|" else "TC#"
            # ----------- SPAWNING TORCHS -------------- #

            for j in range(0, len(self.tab) - 2):
                for i in range(0, len(self.tab[0]) - 2):
                    if all([self.tab[j + k][i] == "|" for k in range(2)]) and all(
                        [self.tab[j][i + k] == "|" for k in range(-2, 3)]
                    ):
                        self.tab[j][i] = "T"

        # -------------- SPAWNING CHESTS ------------- #
        for _ in range(self.nChest):

            chestCoor = [
                random.randrange(len(self.tab[0])),
                random.randrange(len(self.tab)),
            ]
            chestScopeGrid = scopeGrid = [
                self.tab[chestCoor[1] + l][chestCoor[0] + k]
                if 0 <= chestCoor[1] + l < len(self.tab)
                and 0 <= chestCoor[0] + k < len(self.tab[0])
                else "|"
                for l in range(
                    -2,
                    3,
                )
                for k in range(
                    -2,
                    3,
                )
            ]
            tryCount = 0
            while not all([elt == "." for elt in chestScopeGrid]):
                tryCount += 1
                if tryCount == 25:
                    break
                chestCoor = [
                    random.randrange(len(self.tab[0])),
                    random.randrange(len(self.tab)),
                ]
                chestScopeGrid = scopeGrid = [
                    self.tab[chestCoor[1] + l][chestCoor[0] + k]
                    if 0 <= chestCoor[1] + l < len(self.tab)
                    and 0 <= chestCoor[0] + k < len(self.tab[0])
                    else "|"
                    for l in range(
                        -2,
                        3,
                    )
                    for k in range(
                        -2,
                        3,
                    )
                ]

            self.tab[chestCoor[1]][chestCoor[0]] = "C"

        self.showTab()

        self.blitMap()

        # ------------- FOG --------------- #

        self.fogSurf.fill((0, 0, 0, 50))
        center = [
            self.Game.WINDOW_SIZE[0] // 64 / 2,
            self.Game.WINDOW_SIZE[1] // 64 / 2,
        ]

        for j in range(1024 + self.FOG_PADDING):
            for i in range(1024 + self.FOG_PADDING):
                if (
                    DUNGEON_FOG
                    <= math.sqrt(
                        (j // 64 - center[1]) ** 2 + (i // 64 - center[0]) ** 2
                    )
                    < DUNGEON_FOG + 1
                ):
                    self.fogSurf.set_at((i, j), (0, 0, 0, 127))
                elif (
                    math.sqrt((j // 64 - center[1]) ** 2 + (i // 64 - center[0]) ** 2)
                    >= DUNGEON_FOG + 1
                ):
                    self.fogSurf.set_at((i, j), (0, 0, 0, 255))

    def applyFog(self):

        # ------------------- Tiles for minimap ------------- #
        if self.playerCurrentTile not in self.visitedTiles:
            self.visitedTiles.append(self.playerCurrentTile)

        self.Game.screen.blit(self.fogSurf, (-self.FOG_PADDING, -self.FOG_PADDING))

    def isColliding(self, baseRect, direction, entity="Player"):

        # We create a special hitbox to the hero to see if there is collision with a direction
        PADDING_CHECKER = (
            self.Hero.normalizedDistance
        )  # amount of pixels between the hero and an obstacle

        # if entity == "Ennemy":
        #     logger.info(f"{baseRect} Pos of the ennemy in the map : {[self.ennemies[0].chunkPos]}")

        if entity == "Player":
            baseRect = pygame.Rect(0, 0, 0, 0)
            baseRect.topleft = [
                coor - 32 for coor in [self.Hero.buildingPosX, self.Hero.buildingPosY]
            ]

        hitbox = None
        if direction == "right":
            hitbox = pygame.Rect(
                baseRect.topleft[0],
                baseRect.topleft[1],
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
                BASE_HITBOX_ZOOMED,
            )
        if direction == "left":
            hitbox = pygame.Rect(
                baseRect.topleft[0] - PADDING_CHECKER,
                baseRect.topleft[1],
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
                BASE_HITBOX_ZOOMED,
            )
        if direction == "up":
            hitbox = pygame.Rect(
                baseRect.topleft[0],
                baseRect.topleft[1] - PADDING_CHECKER,
                BASE_HITBOX_ZOOMED,
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
            )
        if direction == "down":
            hitbox = pygame.Rect(
                baseRect.topleft[0],
                baseRect.topleft[1],
                BASE_HITBOX_ZOOMED,
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
            )

        if entity == "Player":
            if hitbox.collidelist(self.obstaclesList) != -1:

                rectCollided = self.obstaclesList[hitbox.collidelist(self.obstaclesList)]
                eltCaseFromObstacle = self.elementTab[rectCollided.topleft[1] // 64][
                    rectCollided.topleft[0] // 64
                ]

                if eltCaseFromObstacle["entity"] != None:
                    eltCaseFromObstacle["entity"].openable = True

                self.lastCheckEntity["entity"] = eltCaseFromObstacle["entity"]
                self.lastCheckEntity["onContact"] = eltCaseFromObstacle["onContact"]
                self.lastCheckEntity["rect"] = rectCollided

                return True

            else:
                if self.lastCheckEntity["entity"] != None:
                    self.lastCheckEntity["entity"].openable = False

    def checkOpenableEntity(self, event):

        mousePosTranslated = [
            buildingPos + posCoor - (self.Game.resolution // 2)
            for posCoor, buildingPos in zip(
                pygame.mouse.get_pos(),
                [self.Hero.buildingPosX, self.Hero.buildingPosY],
            )
        ]

        if (
            self.lastCheckEntity["entity"] != None
            and self.lastCheckEntity["onContact"] != None
            # and self.lastCheckEntity["rect"].collidepoint(mousePosTranslated)
            and event.key == self.Game.KeyBindings["Interact with an element"]["value"]
        ):
            self.lastCheckEntity["onContact"]()

    def showMinimap(self):

        self.layout = pygame.transform.scale(
            HUDConf.PLAYER_ICON_SLOT,
            (self.Game.resolution // 4, self.Game.resolution // 4),
        )

        self.miniMapSurf = pygame.transform.scale(
            self.dungeonSurf.copy(), [int(0.90 * coor) for coor in self.layoutRect.size]
        )

        ratio = self.miniMapSurf.get_width() / self.dungeonSurf.get_width()
        playerPoint = [
            coor * ratio for coor in [self.Hero.buildingPosX, self.Hero.buildingPosY]
        ]

        miniMapSurfRect = self.miniMapSurf.get_rect(
            center=(self.layoutRect.width // 2, self.layoutRect.height // 2)
        )
        #  Updating fog of war
        fogLayout = pygame.Surface(
            (miniMapSurfRect.width, miniMapSurfRect.height), SRCALPHA
        )
        fogLayout.fill((0, 0, 0, 255))

        for pos in self.visitedTiles:
            pygame.draw.circle(
                fogLayout,
                (255, 255, 255, 0),
                [coor * 64 * ratio for coor in pos],
                DUNGEON_FOG * 64 * ratio,
            )
        self.miniMapSurf.blit(fogLayout, (0, 0))
        cameraWidth = self.camera["size"][0] * ratio
        cameraPoints = [
            [
                playerPoint[0] + (cameraWidth // 2) * sign_x,
                playerPoint[1] + (cameraWidth // 2) * sign_y,
            ]
            for sign_x, sign_y in [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        ]

        pygame.draw.lines(self.miniMapSurf, (255, 0, 0), True, cameraPoints)
        self.layout.blit(
            self.miniMapSurf,
            miniMapSurfRect,
        )
        self.Game.screen.blit(self.layout, self.layoutRect)

    def blitMap(self):

        self.dungeonSurf = pygame.Surface(
            [64 * mapTileDim for mapTileDim in self.MAP_TILE_SIZE]
        )

        for j in range(len(self.tab)):
            for i in range(len(self.tab[j])):

                # Wall bliting
                if "#" in self.tab[j][i] or "|" in self.tab[j][i]:
                    if "RC" in self.tab[j][i]:
                        self.obstaclesList.append(
                            pygame.Rect(
                                i * 64 + CORRIOR_PADDING,
                                j * 64,
                                64 - CORRIOR_PADDING,
                                64,
                            )
                        )
                    elif "LC" in self.tab[j][i]:
                        self.obstaclesList.append(
                            pygame.Rect(i * 64, j * 64, 64 - CORRIOR_PADDING, 64)
                        )
                    elif "TC" in self.tab[j][i]:
                        self.obstaclesList.append(
                            pygame.Rect(i * 64, j * 64, 64, 64 - CORRIOR_PADDING)
                        )
                    elif "BC" in self.tab[j][i]:
                        self.obstaclesList.append(
                            pygame.Rect(
                                i * 64,
                                j * 64 + CORRIOR_PADDING,
                                64,
                                64 - CORRIOR_PADDING,
                            )
                        )
                    else:
                        self.obstaclesList.append(pygame.Rect(i * 64, j * 64, 64, 64))

                if self.tab[j][i] in ["|", "T", "D"] or "C|" in self.tab[j][i]:

                    if j < len(self.tab) - 2:
                        if "|" in self.tab[j + 1][i]:
                            self.dungeonSurf.blit(
                                textureConf.WORLD_ELEMENTS["Dungeon"][self.name][
                                    "tileset"
                                ]["upper_wall"],
                                (i * 64, j * 64),
                            )
                        else:
                            self.dungeonSurf.blit(
                                textureConf.WORLD_ELEMENTS["Dungeon"][self.name][
                                    "tileset"
                                ]["lower_wall"],
                                (i * 64, j * 64),
                            )
                    else:
                        self.dungeonSurf.blit(
                            textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                                "lower_wall"
                            ],
                            (i * 64, j * 64),
                        ) if j == len(self.tab) else self.dungeonSurf.blit(
                            textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                                "upper_wall"
                            ],
                            (i * 64, j * 64),
                        )
                # Floor bliting
                elif self.tab[j][i] == "#" or "C#" in self.tab[j][i]:
                    self.dungeonSurf.blit(
                        textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                            "ceil"
                        ],
                        (i * 64, j * 64),
                    )

                elif self.tab[j][i] in [
                    ".",
                    "P",
                    "X",
                    "E",
                    "B",
                ]:  # e.g self.tab[j][i] == "."
                    self.dungeonSurf.blit(
                        random.choice(
                            textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                                "floors"
                            ]
                        ),
                        (i * 64, j * 64),
                    )

                if self.tab[j][i] == "T":
                    self.dungeonSurf.blit(
                        textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                            "torchs"
                        ][self.torchIndex],
                        (i * 64, j * 64),
                    )
                    self.torchRects.append((i * 64, j * 64))

                if 0 < j < len(self.tab) - 1 and self.tab[j][i] == "D":
                    if self.tab[j + 1][i] == "E":  # We show the door
                        self.dungeonSurf.blit(
                            textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                                "door"
                            ],
                            (i * 64, (j - 1) * 64),
                        )
                    self.obstaclesList.append(pygame.Rect(i * 64, j * 64, 60, 60))

                if self.tab[j][i] == "E":
                    self.dungeonSurf.blit(
                        pygame.transform.scale(
                            textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                                "entrance"
                            ],
                            (64, 64),
                        ),
                        (i * 64, j * 64),
                    )

                if self.tab[j][i] == "P":
                    self.dungeonSurf.blit(
                        textureConf.DUNGEON_PORTAL_IDLE[self.portalIndex],
                        (i * 64, j * 64),
                    )
                    self.portalsTiles.append((i, j))
                    self.portalRect = pygame.Rect(i * 64, j * 64, 64, 64)

                if self.tab[j][i] == "C":
                    self.obstaclesList.append(pygame.Rect(i * 64, j * 64, 64, 64))
                    self.dungeonSurf.blit(
                        pygame.transform.scale(
                            textureConf.WORLD_ELEMENTS["GameObject"]["Chest"]["surf"],
                            (64, 64),
                        ),
                        (i * 64, j * 64),
                    )
                    self.elementTab[j][i]["entity"] = Chest(self.Game, self.Hero, None)
                    self.elementTab[j][i]["onContact"] = self.elementTab[j][i][
                        "entity"
                    ].show

                if self.tab[j][i] in ["X", "B"]:
                    self.elementTab[j][i]["entity"] = Ennemy(
                        self.Game.screen,
                        self.Hero,
                        self.Game,
                        self,
                        random.choice(
                            textureConf.WORLD_ELEMENTS["Dungeon"][self.name][
                                "composition"
                            ]["ennemy"]
                        ),
                        0,
                        1,
                        place="building",
                    )
                    self.elementTab[j][i]["entity"].initDungeon(
                        (i * 64, j * 64),
                        self.cameraRect.topleft,
                        boss=(self.tab[j][i] == "B"),
                    )
                    self.ennemies.append(self.elementTab[j][i]["entity"])

    def showExtendedMap(self):

        showMap = True
        while showMap:

            self.extendedSurf = pygame.transform.scale(
                mapConf.EXTENDED_MINIMAP_BG,
                (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
            )

            for event in pygame.event.get():
                if (
                    event.type == KEYDOWN
                    and event.key == self.Game.KeyBindings["Toggle Minimap"]["value"]
                ):
                    showMap = False

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == MOUSEBUTTONDOWN:

                    # ------------- ZOOM HANDLING ----------- #

                    # zoom in
                    if event.button == 4 and self.extendedRect.collidepoint(
                        pygame.mouse.get_pos()
                    ):
                        self.zoomValue = [
                            dim + self.ZOOM_SAMPLE[i]
                            for i, dim in enumerate(self.zoomValue)
                        ]

                    elif (
                        event.button == 5
                    ):  # zoom out, if it doesn't mean to zoom out more than the original size
                        if (
                            self.zoomValue[0] > self.offsetZoom[0]
                            and self.zoomValue[1] > self.offsetZoom[1]
                        ):
                            self.zoomValue = [
                                dim - self.ZOOM_SAMPLE[i]
                                for i, dim in enumerate(self.zoomValue)
                            ]

                    else:
                        continue

            self.extendedChunkMap = self.miniMapSurf
            # self.extendedChunkMap.blit(
            #     pygame.transform.scale2x(self.playerIcon),
            #     (
            #         self.Hero.buildingPosX, self.Hero.buildingPosY
            #     ),
            # )
            self.extendedChunkMap = pygame.transform.scale(
                self.extendedChunkMap, self.zoomValue
            )
            self.chunkRect = self.extendedChunkMap.get_rect(
                center=(
                    self.extendedChunkMap.get_width() // 2,
                    self.extendedChunkMap.get_height() // 2,
                )
            )

            self.extendedSurf.blit(self.extendedChunkMap, self.chunkRect)
            self.extendedMapLayout = pygame.transform.scale(
                mapConf.EXTENDED_MAP_LAYOUT,
                (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
            )

            self.extendedSurf.blit(self.extendedMapLayout, (0, 0))
            self.Game.screen.blit(self.extendedSurf, self.extendedRect)
            self.Game.show()

    def show(self):

        if not self.open:

            self.transition(
                "open",
                textureConf.DUNGEON_ANIM_OPEN,
                mapConf.BUILDING_TRANSITION_TIME,
            )

        while self.open:
            self.Game.screen.fill((0, 0, 0, 0))
            for torchRect in self.torchRects:
                self.dungeonSurf.blit(
                    textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                        "torchs"
                    ][self.torchIndex],
                    torchRect,
                )
            self.dungeonSurf.blit(
                textureConf.DUNGEON_PORTAL_IDLE[self.portalIndex], self.portalRect
            )

            if (time.time() - self.lastAnimatedTorch) > self.deltaTorch:
                self.lastAnimatedTorch = time.time()
                self.torchIndex = (self.torchIndex + 1) % len(
                    textureConf.WORLD_ELEMENTS["Dungeon"][self.name]["tileset"][
                        "torchs"
                    ]
                )
            if (time.time() - self.lastAnimatedPortal) > self.deltaPortal:
                self.lastAnimatedPortal = time.time()
                self.portalIndex = (self.portalIndex + 1) % len(
                    textureConf.DUNGEON_PORTAL_IDLE
                )

            self.Game.screen.blit(self.dungeonSurf, (0, 0), self.cameraRect)

            for i, item in enumerate(self.items):
                item.show(self.Game.screen)

            for ennemy in self.ennemies:
                ennemy.show()

            self.applyFog()

            for event in pygame.event.get():

                if event.type == pygame.KEYDOWN:

                    if len(self.Game.heroesGroup) > 1 and event.key == self.Game.KeyBindings["Switch heroes"]["value"]:
                        self.Game.heroIndex = (self.Game.heroIndex + 1) % MAX_TEAM_LENGH

                    self.checkOpenableEntity(event)

                    if event.key == self.Game.KeyBindings["Pick up items"]["value"]:
                        for i, item in enumerate(self.items):
                            item.lootHandler(self.Hero, self, i)
                    if event.key == self.Game.KeyBindings["Interact with an element"][
                        "value"
                    ] and (
                        self.playerCurrentTile == self.entryTile
                        or tuple(self.playerCurrentTile) in self.portalsTiles
                    ):
                        self.transition(
                            "close",
                            textureConf.DUNGEON_ANIM_CLOSE,
                            mapConf.BUILDING_TRANSITION_TIME,
                        )
                        break

                    elif event.key == self.Game.KeyBindings["Pause the game"]["value"]:
                        self.PauseMenu.captureBackground()
                        self.PauseMenu.initPauseMenu()
                        self.PauseMenu.mainLoop()

                    elif (
                        event.key == self.Game.KeyBindings["Toggle Inventory"]["value"]
                        and self.Hero.Inventory.open == False
                    ):
                        self.Hero.Inventory.show()
                        break

                    elif (
                        event.key == self.Game.KeyBindings["Toggle Spell Book"]["value"]
                    ):
                        self.Hero.SpellBook.show()
                        break

                    elif event.key == self.Game.KeyBindings["Toggle Minimap"]["value"]:
                        self.showExtendedMap()

                    elif event.key == self.Game.KeyBindings["Pause the game"]["value"]:
                        self.PauseMenu.captureBackground()
                        self.PauseMenu.initPauseMenu()
                        self.PauseMenu.mainLoop()
                        break
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.Hero.updateClickPoint()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            if self.open:
                self.Hero.handleMovements("building")

                self.Game.heroesGroup[self.Game.heroIndex].CharBar.show()
                self.Game.heroesGroup[self.Game.heroIndex].zoomedShow()
                self.showMinimap()

                self.Game.show()
                self.Game.spaceTransition(self.name)
