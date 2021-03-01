import random
from saves.savesController import SaveController
from gameObjects.NPC import Seller
import time

import pygame
from numpy import genfromtxt
from numpy.core.records import record
from config import mapConf

import config.textureConf as textureConf
from config.mapConf import *
import config.HUDConf as HUDConf
from config.playerConf import *
from gameObjects.Chest import Chest
from UI.menuClass import PauseMenu
from os import *

class Building:

    """Class representing a building.

    A building is a closed map, with elements in it generated differently according to the map and a collision different as it's on a total square.
    """

    def __init__(self, type, name, gameController, Map, Hero, genNPC=0) -> None:

        self.name = name
        self.type = type
        self.Hero = Hero
        self.Game = gameController
        self.Map = Map
        self.PauseMenu = PauseMenu(self.Game, self.Map, self.Hero, SaveController(), self.Game.heroesGroup)
        self.genNPC = genNPC

        self.openable = False
        self.open = False
        self.firstOpen = True

        # --------------- Map ----------------------- #

        self.mapSurfPath = textureConf.WORLD_ELEMENTS[self.type][self.name][
            "mapSurfPath"
        ]
        self.elementTab = [
            [
                {"entity": None, "onContact": None}
                for _ in range(BUILDING_MAP_SIZE)
            ]
            for __ in range(BUILDING_MAP_SIZE)
        ]
        self.obstaclesList = []
        self.lastCheckEntity = {"entity": None, "rect": None, "onContact": None}

        # --------------- MiniMap ---------------- #

        self.layout = pygame.transform.scale(
            HUDConf.PLAYER_ICON_SLOT,
            (self.Game.resolution // 4, self.Game.resolution // 4),
        )
        self.miniMapBlitPoint = [self.Game.resolution - self.layout.get_width(), 0]
        self.layoutRect = self.layout.get_rect(topleft=self.miniMapBlitPoint)

        # ------------------ Camera ----------------- #

        self.enterPoint = [
            coor * 64
            for coor in textureConf.WORLD_ELEMENTS[self.type][self.name]["enterPoints"][
                0
            ]
        ]

        self.enterTiles = [
            [coor for coor in coors]
            for coors in textureConf.WORLD_ELEMENTS[self.type][self.name]["enterPoints"]
        ]
        self.playerCurrentTile = self.enterTiles[0]

        self.camera = {
            "pos": [coor + 32 for coor in self.enterPoint],  # center
            "size": self.Game.WINDOW_SIZE,
        }
        self.cameraRect = pygame.Surface(self.camera["size"]).get_rect(
            center=self.camera["pos"]
        )

        # ------------------- NPC ------------------- #

        self.npcs = textureConf.WORLD_ELEMENTS[self.type][self.name]["NPC"]
        self.npcElements = []

        # ------------------- Ennemies -------------- #
        self.ennemies = []
        self.items = []

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

    def loadMap(self):
        """Load the map surf from self.mapSurfPath,
        create elementTab ffrom self.mapEltPath
        """
        self.mapSurf = pygame.transform.scale2x(pygame.image.load(self.mapSurfPath))

        self.MAP_LAYERS_PATHS = textureConf.WORLD_ELEMENTS[self.type][self.name][
            "mapLayerPath"
        ]
        self.MAP_LAYERS = [
            genfromtxt(path, delimiter=",") for path in self.MAP_LAYERS_PATHS
        ]

        for j in range(BUILDING_MAP_SIZE):
            for i in range(BUILDING_MAP_SIZE):

                caseValues = [layer[j][i] for layer in self.MAP_LAYERS]

                # Spawning NPC
                if f"{i};{j}" in self.npcs.keys():
                    if self.npcs[f"{i};{j}"] == "Seller":
                        self.obstaclesList.append(pygame.Rect(i * 64, j * 64, 64, 64))
                        self.elementTab[j][i]["entity"] = Seller(
                            self.mapSurf,
                            random.randint(100, 300),
                            self.Game,
                            self.Hero,
                            random.choice(
                                listdir("./assets/world_textures/NPC/Seller/")
                            ),
                        )
                        self.elementTab[j][i]["onContact"] = self.elementTab[j][i][
                            "entity"
                        ].openInterface
                        self.npcElements.append(self.elementTab[j][i]["entity"])

                    self.elementTab[j][i]["entity"].init(
                        (
                            i * 64,
                            j * 64,
                        ),
                        zoomed=True,
                    )

                #  Obstalce generation
                if not (
                    caseValues[0] in TILED_GROUND_ID
                    and caseValues[1] == -1
                    and caseValues[2] == -1
                ):
                    self.obstaclesList.append(pygame.Rect(i * 64, j * 64, 64, 64))
                    if (
                        caseValues[1] in TILED_FRAMEWORK_CONVERT["Chest"]
                        or caseValues[2] in TILED_FRAMEWORK_CONVERT["Chest"]
                    ):
                        chestAlreadygen = False
                        for k, l in [
                            (x, y) for x in range(-1, 2) for y in range(-1, 2)
                        ]:
                            if isinstance(
                                self.elementTab[j + l][i + k]["entity"], Chest
                            ):
                                self.elementTab[j][i]["entity"] = self.elementTab[
                                    j + l
                                ][i + k]["entity"]
                                self.elementTab[j][i]["onContact"] = self.elementTab[
                                    j + l
                                ][i + k]["entity"].show
                                chestAlreadygen = True
                                break

                        if not chestAlreadygen:
                            self.elementTab[j][i]["entity"] = Chest(
                                self.Game, self.Hero, None
                            )
                            self.elementTab[j][i]["onContact"] = self.elementTab[j][i][
                                "entity"
                            ].show

                        logger.debug(f"BLITTED CHEST AT {[i,j]}")

    def isColliding(self, baseRect, direction):

        # We create a special hitbox to the hero to see if there is collision with a direction
        PADDING_CHECKER = (
            self.Hero.normalizedDistance
        )  # amount of pixels between the hero and an obstacle

        playerMapTopLeft = [
            coor - 32 for coor in [self.Hero.buildingPosX, self.Hero.buildingPosY]
        ]
        # logger.info(
        #     f"Pos of the player in the map : {[self.Hero.buildingPosX, self.Hero.buildingPosY]}, topleft : {playerMapTopLeft}"
        # )

        tmpRect = None
        if self.Hero.direction == "right":
            tmpRect = pygame.Rect(
                playerMapTopLeft[0],
                playerMapTopLeft[1],
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
                BASE_HITBOX_ZOOMED,
            )
        if self.Hero.direction == "left":
            tmpRect = pygame.Rect(
                playerMapTopLeft[0] - PADDING_CHECKER,
                playerMapTopLeft[1],
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
                BASE_HITBOX_ZOOMED,
            )
        if self.Hero.direction == "up":
            tmpRect = pygame.Rect(
                playerMapTopLeft[0],
                playerMapTopLeft[1] - PADDING_CHECKER,
                BASE_HITBOX_ZOOMED,
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
            )
        if self.Hero.direction == "down":
            tmpRect = pygame.Rect(
                playerMapTopLeft[0],
                playerMapTopLeft[1],
                BASE_HITBOX_ZOOMED,
                BASE_HITBOX_ZOOMED + PADDING_CHECKER,
            )

        if tmpRect.collidelist(self.obstaclesList) != -1:

            rectCollided = self.obstaclesList[tmpRect.collidelist(self.obstaclesList)]
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
            and self.lastCheckEntity["rect"].collidepoint(mousePosTranslated)
            and event.key == self.Game.KeyBindings["Interact with an element"]["value"]
        ):
            self.lastCheckEntity["onContact"]()

    def showMinimap(self):

        self.layout = pygame.transform.scale(
            HUDConf.PLAYER_ICON_SLOT,
            (self.Game.resolution // 4, self.Game.resolution // 4),
        )

        miniMapSurf = pygame.transform.scale(
            self.mapSurf.copy(), [int(0.90 * coor) for coor in self.layoutRect.size]
        )
        ratio = miniMapSurf.get_width() / self.mapSurf.get_width()
        playerPoint = [
            coor * ratio for coor in [self.Hero.buildingPosX, self.Hero.buildingPosY]
        ]

        miniMapSurfRect = miniMapSurf.get_rect(
            center=(self.layoutRect.width // 2, self.layoutRect.height // 2)
        )

        cameraWidth = self.camera["size"][0] * ratio
        cameraPoints = [
            [
                playerPoint[0] + (cameraWidth // 2) * sign_x,
                playerPoint[1] + (cameraWidth // 2) * sign_y,
            ]
            for sign_x, sign_y in [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        ]

        pygame.draw.lines(miniMapSurf, (255, 0, 0), True, cameraPoints)
        self.layout.blit(
            miniMapSurf,
            miniMapSurfRect,
        )
        self.Game.screen.blit(self.layout, self.layoutRect)

    def transition(self, name, frames, animationTime):

        if name == "open":
            if self.openable:
                self.bg = self.Game.screen.copy()
                self.open = True
                self.Game.enterBuilding()

                self.Hero.currentBuilding = self
                self.Hero.buildingPosX, self.Hero.buildingPosY = self.camera["pos"]

                if self.firstOpen:
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
        self.Game.musicController.setMusic("building")

        # Resetting Hero movement
        self.Hero.XDistanceToTarget = 0
        self.Hero.YDistanceToTarget = 0
        self.Hero.targetPos = self.Hero.pos

    def show(self):

        if not self.open:

            self.transition(
                "open",
                textureConf.BUILDING_ANIM_OPEN,
                mapConf.BUILDING_TRANSITION_TIME,
            )


        while self.open:
            self.Game.screen.fill((0, 0, 0))
            self.Game.screen.blit(self.mapSurf, (0, 0), self.cameraRect)

            mousePosTranslated = [
                buildingPos + posCoor - (self.Game.resolution // 2)
                for posCoor, buildingPos in zip(
                    pygame.mouse.get_pos(),
                    [self.Hero.buildingPosX, self.Hero.buildingPosY],
                )
            ]

            for npc in self.npcElements:
                npc.show()

            for event in pygame.event.get():

                if event.type == pygame.KEYDOWN:
                    self.checkOpenableEntity(event)

                    if event.key == self.Game.KeyBindings["Pick up items"]["value"]:
                        for i, item in enumerate(self.items):
                            item.lootHandler(self.Hero, self, i)

                    if (
                        event.key
                        == self.Game.KeyBindings["Interact with an element"]["value"]
                        and self.playerCurrentTile in self.enterTiles
                    ):
                        self.transition(
                            "close",
                            textureConf.BUILDING_ANIM_CLOSE,
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

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.Hero.updateClickPoint()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            if self.open:
                self.Hero.handleMovements("building")

                for i, item in enumerate(self.items):
                    item.show(self.Game.screen)

                self.Hero.CharBar.show()
                self.Game.heroesGroup[self.Game.heroIndex].zoomedShow()
                self.showMinimap()

                self.Game.show()
                self.Game.spaceTransition(self.name)