from copy import deepcopy
from UI.UI_utils_text import SelectPopUp
import string
import time
from config import spellsConf, textureConf
from config.ennemyConf import ENNEMY_DETECTION_RANGE
from network.packet_types import TEMPLATE_CHARACTER_INFO
from utils.Network_helpers import write_to_pipe

import utils.RessourceHandler as RessourceHandler
from assets.animation import *
from config import playerConf
from config.HUDConf import *
from config.playerConf import *
from config.netConf import *
from config.textureConf import *
from gameController import *
from gameObjects import *
from HUD.CharBar import CharBar
from HUD.Inventory import Inventory
from HUD.spellBook import SpellBook
from HUD.QuestController import QuestController

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from queue import Queue


class Character:
    def __init__(self, gameController, Map, genOrder=-1) -> None:

        self.genOrder = genOrder

        # ---------- SAVE ------------ #
        self._stateSaved = False
        self.charImage_string = None
        # Assets that the player_map is already rendered on the self.screen !
        self.Game = gameController
        self.Map = Map
        self.currentPlace = "openWorld"
        self.currentBuilding = None
        self.Inventory = None
        self.SpellBook = None
        if self.genOrder == 0:
            self.Map.Hero = self
        self._fightId = None

        # Rest mechanics
        self.lastTimeoutHealed = time.time()
        self.lastedTurnRest = 1

        # ------------------- STATS ------------------- #

        self._Level = 0
        self.classId = random.randint(0, len(CLASSES_NAMES) - 1)
        self._XP = {"Exp": 0, "Expmax": 100}

        self.stats = playerConf.CLASSES_DEFAULT_STATS[
            playerConf.CLASSES_NAMES[self.classId]
        ]

        self.spellsID = []

        # name of length 10
        self.name = random.choice(list(string.ascii_uppercase)) + ("").join(
            [
                random.choice(list(string.ascii_lowercase))
                for _ in range(random.randint(1, 9))
            ]
        )

        self._fightName = self.name

        # ------------------ ANIMATIONS --------------- #

        self.imageState = {
            "image": playerConf.CLASSES[self.classId]["directions"]["down"][0],
            "imagePos": 0,
        }
        self.charRect = self.imageState["image"].get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.direction = "down"
        self.prevDir = self.direction
        self.animationMinTimeRendering = (
            PLAYER_ANIMATION_DURATION / PLAYER_ANIMATION_FRAME_LENGTH
        )
        self.lastTimePlayerAnimated = time.time()

        # ------------------- CHARACTERS MOVEMENTS --- #

        # Default is centered the view

        self.spawnPos = [0, 0]

        # Handling physics
        self.lastRenderedTime = time.time()
        self.velocity = 400  # Pixels/s
        self.delta_T = 1 / self.Game.refresh_rate
        self.normalizedDistance = self.velocity * self.delta_T

        self.pos = self.charRect.center

        # Handling player target point
        self.XDistanceToTarget = 0
        self.YDistanceToTarget = 0
        self.targetPos = self.pos

        # ------------------ CHUNKS HANDLING (OPEN WORLD) -------- #

        self.initChunkPosX = (
            -self.Map.chunkData["mainChunk"].get_width() / 2 + self.pos[0]
        )
        self.initChunkPosY = (
            -self.Map.chunkData["mainChunk"].get_height() / 2 + self.pos[1]
        )
        self.mainChunkPosX = self.initChunkPosX
        self.mainChunkPosY = self.initChunkPosY

        # Values tracking the movement of the player regarding of his position in the chunks, used mainly for the chunkController method
        self.blitOffset = [0, 0]
        self.keys = {
            "up": {"name": pygame.K_UP, "value": [0, 1]},
            "right": {"name": pygame.K_RIGHT, "value": [-1, 0]},
            "left": {"name": pygame.K_LEFT, "value": [1, 0]},
            "down": {"name": pygame.K_DOWN, "value": [0, -1]},
        }

        self.posMainChunkCenter = [
            int(self.Map.chunkData["mainChunk"].get_width() / 2 - self.blitOffset[0]),
            int(self.Map.chunkData["mainChunk"].get_height() / 2 - self.blitOffset[1]),
        ]

        if self.genOrder == 0:
            self.Map.envHandler.Hero = self
            self.Map.envHandler.envGenerator.Hero = self

        # ----------------------- BUILDING HANDLING ----------------- #

        # Keep tracks of the player pos in a closed map
        self.buildingPosX = 0
        self.buildingPosY = 0

        # ----------------------- PATHFINDING -------------- #
        self.pathfinding_q = Queue()

    def initSpells(self):

        self.spellsID = playerConf.CLASSES[self.classId]["spellsId"]

    def modifyHP(self, x):
        self.stats["HP"] += x
        if self.stats["HP"] < 0:
            self.stats["HP"] = 0
        elif self.stats["HP"] > self.stats["HP_max"]:
            self.stats["HP"] = self.stats["HP_max"]

    def modifyMana(self, x):
        if self.stats["Mana"] + x < 0:
            return False
        self.stats["Mana"] += x
        if self.stats["Mana"] > self.stats["Mana_max"]:
            self.stats["Mana"] = self.stats["Mana_max"]

    def addExp(self, x):
        self._XP["Exp"] += x
        if self._XP["Exp"] > self._XP["Expmax"]:
            self.lvlUp()

    def lvlUp(self):

        self._XP["Exp"] = 0
        self._XP["Expmax"] += 10 // 100
        self._Level += 1

        self.spellsID += [
            Id
            for Id in spellsConf.SPELL_DB.keys()
            if spellsConf.SPELL_DB[Id].className
            == playerConf.CLASSES_NAMES[self.classId]
            and spellsConf.SPELL_DB[Id].lvl == self._Level
        ]
        logger.info(f"Current player's spell's ID : {self.spellsID}")

        self.SpellBook.updateSpellBook()

        if not self._Level == 1:  # The inital level up does not require something else
            # Dialog(
            #     f,
            #     (self.Game.resolution // 2, self.Game.resolution // 2),
            #     self.Game.screen,
            #     (255, 0, 0),
            #     self.Game,
            #     charLimit=50,
            # ).mainShow()

            def addStat(stat, value):
                def int_func():
                    return self.modifyStat(stat, value)

                return int_func

            SelectPopUp(
                {
                    f"{stat}": addStat(stat, 1)
                    for stat in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
                },
                self.Game.screen,
                self.Game,
                (self.Game.resolution // 2, self.Game.resolution // 2),
                f"{self.name} gain a level ! What characteristic do you want to up ?",
            ).show()

        # if self.Game.isOnline:
        #     self.transmitCharacInfos()

    def modifyStat(self, stat, value):
        self.stats[stat] += value

    def setId(self, id):
        self._fightId = id
        self._fightName = self.name

    def createFight(self, preConfig=[]):

        if preConfig != []:
            self.Game.fightMode.initFight(preConfig)

        else:
            entitieOnContact = [
                Hero for Hero in self.Game.heroesGroup if Hero.stats["HP"] > 0
            ]
            if len(entitieOnContact) == 0:
                logger.error("All heroes are dead, can't start fight")
            else:
                if self.currentPlace == "openWorld":
                    for i, ennemy in enumerate(self.Map.envGenerator.ennemies):
                        if (
                            math.sqrt(
                                (
                                    ennemy["value"]["entity"].chunkPos[0]
                                    - self.posMainChunkCenter[0]
                                )
                                ** 2
                                + (
                                    ennemy["value"]["entity"].chunkPos[1]
                                    - self.posMainChunkCenter[1]
                                )
                                ** 2
                            )
                            // self.Map.stepGeneration
                            <= ENNEMY_DETECTION_RANGE
                        ):
                            entitieOnContact.append(
                                self.Map.envGenerator.ennemies.pop(i)["value"]["entity"]
                            )

                elif self.currentPlace == "building":
                    for i, ennemy in enumerate(self.currentBuilding.ennemies):
                        if (
                            math.sqrt(
                                (ennemy.pos[0] - self.pos[0]) ** 2
                                + (ennemy.pos[1] - self.pos[1]) ** 2
                            )
                            // self.Map.stepGeneration
                            <= ENNEMY_DETECTION_RANGE
                        ):
                            entitieOnContact.append(
                                self.currentBuilding.ennemies.pop(i)
                            )

                self.Game.fightMode.initFight(entitieOnContact)

    def __str__(self) -> str:

        return f"Character {self.name} : \n\t-> {self.targetPos} \n\t-> {CLASSES_NAMES[self.classId]}"

    # ---------------------- GRPAPHIC METHOD ------------------ #

    def initHUD(self, LoadingMenu=None) -> None:
        """
        Initialise the Hero HUD except the minimap which is instancied by the Map object and update the flag on the Loading Menu passed in.

        The HUD consists of these elements :
        + Inventory
        + Spell Book
        + Character Bar (displaying character states)

        Parameters :
        ---
        + LoadingMenu : loading menu instance

        """
        if self.genOrder == 0:

            LoadingMenu.updateProgressBar("HUDLoading")
            RessourceHandler.loadHUDRessources()
            LoadingMenu.confirmLoading("HUDLoading")

            LoadingMenu.updateProgressBar("ItemDBLoading", "gameObjectLoading")
            RessourceHandler.loadItemRessources()
            LoadingMenu.confirmLoading("ItemDBLoading", "gameObjectLoading")

            LoadingMenu.updateProgressBar("spellDBLoading", "gameObjectLoading")
            RessourceHandler.loadSpellRessources()
            LoadingMenu.confirmLoading("spellDBLoading", "gameObjectLoading")

        self.Inventory = Inventory(self.Game, self)
        self.CharBar = CharBar(self.Game, self)
        self.SpellBook = SpellBook(self.Game, self)
        if self.genOrder == 0:
            self.QuestJournal = QuestController(self.Game, self)
        else:
            self.QuestJournal = self.Game.heroesGroup[0].QuestJournal

        # Loading the intial spells by raising the level from 0 to 1
        self.lvlUp()

    def spawnHeroRandomPos(self, Map):

        assert (
            Map.id == 0
        ), f"<ERROR> : this method can only be invoked within the WORLD_MAP config"
        """Spawns a character somewhere on the world map, but not with water"""
        self.spawnPos = [
            int(random.randint(1, self.resolution) - PLAYER_SIZE / 2),
            int(random.randint(1, self.resolution) - PLAYER_SIZE / 2),
        ]

        while Map.worldMapTab[self.pos[1]][self.pos[0]] == textureConf.WATER:
            # We add the constant PLAYER_SIZE/2 for the sprite
            self.pos = [
                int(random.randint(1, self.resolution) - PLAYER_SIZE / 2),
                int(random.randint(1, self.resolution) - PLAYER_SIZE / 2),
            ]

    def moveControllerCentered(self, event):

        # if the direction is not the same as the previous one
        # we do not update the animation frame index
        if event.type == pygame.KEYDOWN:
            # Animation handling
            if pygame.key.name(event.key) == self.direction:
                self.imageState["imagePos"] = (
                    0
                    if self.imageState["imagePos"] == PLAYER_ANIMATION_FRAME_LENGTH - 1
                    else self.imageState["imagePos"] + 1
                )

            # Change of direction and change of the animation position
            else:
                self.direction = pygame.key.name(event.key)

            # Computing and updating character pos
            for key in self.keys:
                if pygame.key.get_pressed()[self.keys[key]["name"]]:

                    # Checking collision with the open world
                    if not self.Map.envGenerator.isColliding(
                        self.imageState["image"].get_rect(
                            center=self.posMainChunkCenter
                        ),
                        self.direction,
                    ):

                        self.imageState["image"] = CLASSES[self.classId]["directions"][
                            self.direction
                        ][self.imageState["imagePos"]]

                        self.mainChunkPosX += (
                            self.keys[key]["value"][0] * self.normalizedDistance
                        )
                        self.mainChunkPosY += (
                            self.keys[key]["value"][1] * self.normalizedDistance
                        )

                        # These values are here to track the movement of the player regarding of the limits of the chunks
                        # It might be nested in the mainChunkPos computing, but it has been separated for code lisibility
                        self.blitOffset[0] += (
                            self.keys[key]["value"][0] * self.normalizedDistance
                        )
                        self.blitOffset[1] += (
                            self.keys[key]["value"][1] * self.normalizedDistance
                        )

                        if self.Game.debug_mode:
                            logger.debug(f"{self.direction} -> {self.blitOffset}")

    def moveByClick(self, envGenerator, mapName):

        # if self.genOrder >0:

        #     if not (
        #     abs(self.Game.heroesGroup[0].XDistanceToTarget) < self.normalizedDistance
        #     and abs(self.Game.heroesGroup[0].YDistanceToTarget) < self.normalizedDistance
        # ):
        #         self.prevDir = self.direction

        #         if abs(self.Game.heroesGroup[0].XDistanceToTarget) >= abs(self.Game.heroesGroup[0].YDistanceToTarget):

        #             self.direction = "right" if self.Game.heroesGroup[0].XDistanceToTarget > 0 else "left"

        #         else:
        #             self.direction = "down" if self.Game.heroesGroup[0].YDistanceToTarget > 0 else "up"

        #         # Updating running animation
        #         if (
        #             self.prevDir == self.direction
        #             and (time.time() - self.lastTimePlayerAnimated)
        #             > self.animationMinTimeRendering
        #         ):
        #             self.lastTimePlayerAnimated = time.time()
        #             self.imageState["imagePos"] = (
        #                 0
        #                 if self.imageState["imagePos"]
        #                 == PLAYER_ANIMATION_FRAME_LENGTH - 1
        #                 else self.imageState["imagePos"] + 1
        #             )
        # else:
        # Computing the direction to get
        if not (
            abs(self.XDistanceToTarget) < self.normalizedDistance
            and abs(self.YDistanceToTarget) < self.normalizedDistance
        ):

            self.prevDir = self.direction

            if abs(self.XDistanceToTarget) >= abs(self.YDistanceToTarget):

                self.direction = "right" if self.XDistanceToTarget > 0 else "left"

            else:
                self.direction = "down" if self.YDistanceToTarget > 0 else "up"

            # First checking collision with the open world then computing and updating character pos
            if not envGenerator.isColliding(
                self.imageState["image"].get_rect(center=self.posMainChunkCenter),
                self.direction,
            ):

                # Updating running animation
                if (
                    self.prevDir == self.direction
                    and (time.time() - self.lastTimePlayerAnimated)
                    > self.animationMinTimeRendering
                ):
                    self.lastTimePlayerAnimated = time.time()
                    self.imageState["imagePos"] = (
                        0
                        if self.imageState["imagePos"]
                        == PLAYER_ANIMATION_FRAME_LENGTH - 1
                        else self.imageState["imagePos"] + 1
                    )

                # Modifying bliting point of the background (make it "scroll" on the character)
                DELTA_X = (
                    self.keys[self.direction]["value"][0] * self.normalizedDistance
                )
                DELTA_Y = (
                    self.keys[self.direction]["value"][1] * self.normalizedDistance
                )

                # Updating the distance between the target and the character
                self.XDistanceToTarget += DELTA_X
                self.YDistanceToTarget += DELTA_Y

                if mapName == "openWorld":
                    self.mainChunkPosX += DELTA_X
                    self.mainChunkPosY += DELTA_Y

                    # These values are here to track the movement of the player regarding of the limits of the chunks
                    # It might be nested in the mainChunkPos computing, but it has been separated for code lisibility
                    self.blitOffset[0] += DELTA_X
                    self.blitOffset[1] += DELTA_Y

                    self.posMainChunkCenter = [
                        int(
                            self.Map.chunkData["mainChunk"].get_width() / 2
                            - self.blitOffset[0]
                        ),
                        int(
                            self.Map.chunkData["mainChunk"].get_height() / 2
                            - self.blitOffset[1]
                        ),
                    ]

                    for ennemy in envGenerator.ennemies:
                        ennemy["value"]["entity"].setPos((DELTA_X, DELTA_Y))

                    # if self.Game.debug_mode:
                    #     logger.debug(
                    #         f"{self.Map.chunkData['currentChunkPos']} - {self.direction} -> {self.blitOffset}"
                    #     )

                    if self.Game.isOnline:
                        self.Map.transmitPosInfos()

                elif mapName == "building":
                    self.buildingPosX -= DELTA_X
                    self.buildingPosY -= DELTA_Y
                    self.currentBuilding.update(-DELTA_X, -DELTA_Y)

                    for ennemy in envGenerator.ennemies:
                        ennemy.setPos(
                            [
                                coor + offset
                                for coor, offset in zip(ennemy.pos, (DELTA_X, DELTA_Y))
                            ]
                        )

                for item in envGenerator.items:
                    item.setPos(
                        [
                            coor + offset
                            for coor, offset in zip(item.pos, (DELTA_X, DELTA_Y))
                        ],
                    )
        else:
            if not self.pathfinding_q.empty():
                self.updateClickPoint(subclick=self.pathfinding_q.get())

    def updateClickPoint(self, subclick=[]):

        if subclick != []:
            self.XDistanceToTarget, self.YDistanceToTarget = subclick

        else:
            self.pathfinding_q.queue.clear()
            # Updated at each click, so the tuple is converted to be exploited

            # pathfinding
            grid = Grid(matrix=self.Map.matrix)

            # Case - Movement within the tilee
            if [pos // self.Map.stepGeneration for pos in self.posMainChunkCenter] == [
                int(
                    (coor + self.Map.CHUNK_SIZE * self.Map.renderDistance - offset)
                    // self.Map.stepGeneration
                )
                for coor, offset in zip(list(pygame.mouse.get_pos()), self.blitOffset)
            ]:
                self.updateClickPoint(
                    subclick=[
                        coor
                        + self.Map.CHUNK_SIZE * self.Map.renderDistance
                        - offset
                        - mainChunkPos
                        for coor, offset, mainChunkPos in zip(
                            list(pygame.mouse.get_pos()),
                            self.blitOffset,
                            self.posMainChunkCenter,
                        )
                    ]
                )
            else:

                start = grid.node(
                    *[pos // self.Map.stepGeneration for pos in self.posMainChunkCenter]
                )
                end = grid.node(
                    *[
                        int(
                            (
                                coor
                                + self.Map.CHUNK_SIZE * self.Map.renderDistance
                                - offset
                            )
                            // self.Map.stepGeneration
                        )
                        for coor, offset in zip(pygame.mouse.get_pos(), self.blitOffset)
                    ]
                )

                finder = AStarFinder()
                paths, runs = finder.find_path(start, end, grid)

                self.pathfinding_q.queue.clear()

                if len(paths) > 0:
                    for i in range(len(paths)):
                        if i == 0:
                            self.pathfinding_q.put(
                                [
                                    p_coor * self.Map.stepGeneration
                                    + PLAYER_SIZE // 2
                                    - mainChunkPos
                                    for p_coor, mainChunkPos in zip(
                                        paths[i], self.posMainChunkCenter
                                    )
                                ]
                            )
                        # elif i == (len(paths)-1):
                        #     self.pathfinding_q.put(
                        #         [
                        #             coor
                        #             + self.Map.CHUNK_SIZE * self.Map.renderDistance
                        #             - offset
                        #             - prev_p * self.Map.stepGeneration
                        #             for coor, offset, prev_p in zip(
                        #                 pygame.mouse.get_pos(),
                        #                 self.blitOffset,
                        #                 paths[i - 1],
                        #             )
                        #         ]
                        #     )
                        else:
                            self.pathfinding_q.put(
                                [
                                    (p_coor - prev_p_coor) * self.Map.stepGeneration
                                    for p_coor, prev_p_coor in zip(
                                        paths[i], paths[i - 1]
                                    )
                                ]
                            )

    def handleMovements(self, mapName):
        """Function updating pos and bliting it to the game screen every delta_t period of time"""

        if (time.time() - self.lastRenderedTime) > self.delta_T:

            if mapName == "openWorld":
                # Checking chunks
                self.Map.chunkController()

                # Updating pos
                self.moveByClick(self.Map.envGenerator, mapName)
                # self.moveControllerCentered(event)

            elif mapName == "building":

                self.moveByClick(self.currentBuilding, mapName)

            # Reseting the chrono to move the character
            self.lastRenderedTime = time.time()

    def show(self):
        if self.genOrder > 0:
            self.direction = self.Game.heroesGroup[0].direction
            self.imageState["imagePos"] = self.Game.heroesGroup[0].imageState[
                "imagePos"
            ]
        # Changing animation
        self.imageState["image"] = playerConf.CLASSES[self.classId]["directions"][
            self.direction
        ][self.imageState["imagePos"]]

        if not self.Game.screen.get_locked():
            self.Game.screen.blit(self.imageState["image"], self.charRect)

    def zoomedShow(self):

        # Changing animation
        self.imageState["image"] = playerConf.CLASSES[self.classId]["directions"][
            self.direction
        ][self.imageState["imagePos"]]

        self.zoomedSurf = pygame.transform.scale(self.imageState["image"], (64, 64))
        self.zoomedRect = self.zoomedSurf.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.Game.screen.blit(
            self.zoomedSurf,
            self.zoomedRect,
        )

    # -------------------- NETWORK --------------- #

    def transmitCharacInfos(self):
        charac_packet = deepcopy(TEMPLATE_CHARACTER_INFO)
        charac_packet["sender_id"] = self.networkId
        charac_packet["spellsID"] = self.spellsID
        charac_packet["stats"] = self.stats
        write_to_pipe(
            IPC_FIFO_OUTPUT_CREA
            if self.Game.NetworkController.isSessionCreator
            else IPC_FIFO_OUTPUT_JOINER,
            charac_packet,
        )

    # def __getstate__(self):

    #     state = self.__dict__.copy()
    #     state.pop("Game")

    #     if not self._stateSaved:

    #         charImage = state["imageState"].pop("image")
    #         self.charImage_string = (
    #             pygame.image.tostring(charImage, "RGB"),
    #             charImage.get_size(),
    #         )
    #         self._stateSaved = True
    #         state = self.__dict__.copy()
    #         state.pop("Game")

    #     return state

    # def __setstate__(self, state):

    #     charImage_string, size = state["charImage_string"]
    #     state["imageState"]["image"] = pygame.image.fromstring(
    #         charImage_string, size, "RGB"
    #     )

    #     self.__dict__.update(state)
