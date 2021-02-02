from copy import deepcopy
from fnmatch import fnmatch
import time
import pygame
import random
import math
from pygame import transform
from pygame.constants import SRCALPHA
from config import textureConf
from config.playerConf import *
from config.ennemyConf import *
from os import *
from os.path import *


class Ennemy:

    """Meta class representing an ennemy"""

    def __init__(
        self,
        parentSurface,
        Hero,
        gameController,
        envGenerator,
        name,
        type_enemy,
        Level,
        place="openWorld",
    ) -> None:

        self.Game = gameController
        self.Hero = Hero
        self.envGenerator = envGenerator
        self.state = "Idle"
        self.prevState = "Idle"
        self.name = name
        self.place = place
        self.stats = {
            statName: stat * math.sqrt(self.Hero._Level)
            for statName, stat in ENNEMIES_STAT[self.name].items()
        }
        self._fightId = None
        self.goldValue = textureConf.WORLD_ELEMENTS["Ennemy"][self.name][
            "defaultGoldValue"
        ] + random.randint(1, 5)
        self.loot = deepcopy(
            random.choice(textureConf.WORLD_ELEMENTS["Ennemy"][self.name]["loots"])
        )
        self.loot.loadSurfDesc()
        self.loot.loadIcon()
        self.XP = random.randint(
            self.Hero._XP["Expmax"] // (4 * self.Hero._Level),
            self.Hero._XP["Expmax"] // (4 * self.Hero._Level) + 10,
        )
        self.isBoss = False

        # STATE BUBBLE
        self.bubbleAnim = []
        self.lastRenderedNPCBubble = time.time()
        self.BubbleDeltaTime = None
        self.bubbleIndex = 0
        self.bubbleRect = None
        self.bubbleSurf = None

        # Ennemy TEXTURE
        self.parentSurface = parentSurface
        self.animationFrames = {}
        self.surf = None
        self.animationPath = []
        self.AnimDeltaTime = None
        self.lastAnimRendering = time.time()
        self.AnimIndex = {state: 0 for state in ENNEMY_STATES}
        self.rect = None

        self.direction = "down"
        self.prevDir = self.direction
        self.keys = {
            "up": {"value": [0, -1]},
            "right": {"value": [1, 0]},
            "left": {"value": [-1, 0]},
            "down": {"value": [0, 1]},
        }

        # PHYSICS
        self.pos = None  # topleft !
        self.chunkPos = None
        self.initPos = None

        self.lastRenderedTime = time.time()
        self.velocity = {"Walk": 100, "Chase": 300}  # Pixels/s
        self.currentVel = self.velocity["Walk"]

        self.delta_T = 1 / self.Game.refresh_rate
        self.normalizedDistance = self.currentVel * self.delta_T
        self.lastClicked = time.time()

        self.XDistanceToTarget = 0
        self.YDistanceToTarget = 0
        self.targetPos = None
        self.playerDetected = False

        self._Level = Level
        self._TypeEnemy = type_enemy  # 0-normal 1-miniboss 2-boss

    def getTypeEnemy(self):
        if self._TypeEnemy == 0:
            return "Normal"
        elif self._TypeEnemy == 1:
            return "Mini Boss"
        elif self._TypeEnemy == 2:
            return "Boss"

    def setId(self, id):
        self._fightId = id
        self._fightName = (
            f"{self.name} {id}" if not self.isBoss else f"[BOSS] { self.name}"
        )

    def modifyHP(self, x):
        self.stats["HP"] += x
        if self.stats["HP"] <= 0:
            self.stats["HP"] = 0
            self.Game.combatLog.addText(f"The {self.name} has been slayed !")
        elif self.stats["HP"] > self.stats["HP_max"]:
            self.stats["HP"] = self.stats["HP_max"]

    def modifyMana(self, x):
        if self.stats["Mana"] + x < 0:
            return False
        self.stats["Mana"] += x
        if self.stats["Mana"] > self.stats["Mana_max"]:
            self.stats["Mana"] = self.stats["Mana_max"]

    # ------------------------- GRAPHICAL METHODS --------------------- #

    def initDungeon(self, pos, cameraPos, boss=False):

        self.init(pos, boss)
        self.pos = [coor - cameraCoor for coor, cameraCoor in zip(pos, cameraPos)]

    def init(self, pos, boss=False):

        # Translating the coor normally blitted in the mainChunk to the game Screen and relatively to the player
        self.pos = [
            coor - self.Game.resolution
            for coor, playerOffset in zip(pos, self.Hero.blitOffset)
        ]

        # As the self.rect is the rect to blit according to the Game screen, we need to project one on the mainChunk to compare it to other elements
        self.chunkPos = list(pos)
        self.initPos = list(pos)

        # Loading ENNEMY textures
        for state in ENNEMY_STATES:
            self.animationFrames[state] = [
                pygame.transform.scale(
                    pygame.image.load(
                        f"./assets/world_textures/ennemy/{self.name}/{state}/{f}"
                    ).convert_alpha(),
                    (
                        self.Hero.Map.stepGeneration
                        if not boss
                        else self.Hero.Map.stepGeneration * 2,
                        self.Hero.Map.stepGeneration
                        if not boss
                        else self.Hero.Map.stepGeneration * 2,
                    ),
                )
                for f in listdir(f"./assets/world_textures/ennemy/{self.name}/{state}/")
                if isfile(
                    join(f"./assets/world_textures/ennemy/{self.name}/{state}", f)
                )
            ]

        self.rect = self.animationFrames[self.state][0].get_rect(topleft=self.pos)
        self.rectChunk = self.animationFrames[self.state][0].get_rect(
            topleft=self.chunkPos
        )
        self.surf = pygame.Surface(self.rect.size, SRCALPHA)

        # Loading bubble stuff
        self.bubbleAnim = [
            pygame.transform.scale(
                pygame.image.load(f"./assets/world_textures/ennemy/stateBubble/{f}"),
                (PLAYER_SIZE, PLAYER_SIZE),
            )
            for f in listdir(f"./assets/world_textures/ennemy/stateBubble/")
            if isfile(join(f"./assets/world_textures/ennemy/stateBubble/", f))
        ]
        self.BubbleDeltaTime = ENNEMY_BUBBLE_ANIM_TIME / len(self.bubbleAnim)
        self.bubbleRect = self.bubbleAnim[0].get_rect(
            topleft=[
                self.pos[0] + self.rect.width // 2,
                self.pos[1] - (self.bubbleAnim[1].get_height() + 5),
            ]
        )

        if boss:
            self.isBoss = True
            for stat in self.stats:
                if stat not in ["ATK", "DEF"]:
                    self.stats[stat] *= 3
                else:
                    self.stats[stat] *= 2

        self.idle_updating()

    def _updateBubble(self):

        # Updating info bubble
        self.bubbleRect = self.bubbleAnim[0].get_rect(
            topleft=[self.pos[0], self.pos[1] - (self.bubbleAnim[1].get_height() + 5)]
        )

        if (time.time() - self.lastRenderedNPCBubble) > self.BubbleDeltaTime:

            self.lastRenderedNPCBubble = time.time()
            self.bubbleIndex = (self.bubbleIndex + 1) % len(self.bubbleAnim)
        self.bubbleSurf.blit(self.bubbleAnim[self.bubbleIndex], (0, 0))

    def _updateAnim(self):

        self.AnimDeltaTime = ENNEMY_ANIM_TIME / len(self.animationFrames[self.state])
        # Updating Walkning animation
        if (time.time() - self.lastAnimRendering) > self.AnimDeltaTime:

            self.lastAnimRendering = time.time()
            self.AnimIndex[self.state] = (self.AnimIndex[self.state] + 1) % len(
                self.animationFrames[self.state]
            )

    def setVel(self, velState: str):

        self.currentVel = self.velocity[velState]
        self.normalizedDistance = self.currentVel * self.delta_T

    def targetPlayer(self):
        self.targetPos = (
            [coor - 32 for coor in self.Hero.playerPosMainChunkCenter]
            if self.place == "openWorld"
            else [self.Hero.buildingPosX - 32, self.Hero.buildingPosY - 32]
        )
        self.XDistanceToTarget = self.targetPos[0] - self.chunkPos[0]
        self.YDistanceToTarget = self.targetPos[1] - self.chunkPos[1]

        #  To prevent position reset while changing chunkss
        self.initPos = self.chunkPos.copy()

    def detectPlayer(self, playerPos):

        if math.sqrt(
            (playerPos[0] - self.chunkPos[0]) ** 2
            + (playerPos[1] - self.chunkPos[1]) ** 2
        ) < (ENNEMY_DETECTION_RANGE * self.Hero.Map.stepGeneration):
            self.playerDetected = True
            self.setVel("Chase")
            self.targetPlayer()

        else:
            self.playerDetected = False
            self.setVel("Walk")

    def show(self):
        """
        Blit the updated animations on the parent surface
        """

        self.surf = pygame.Surface(self.rect.size, SRCALPHA)
        self.bubbleSurf = pygame.Surface(self.bubbleRect.size, SRCALPHA)

        self.detectPlayer(
            self.Hero.playerPosMainChunkCenter
        ) if self.place == "openWorld" else self.detectPlayer(
            [self.Hero.buildingPosX, self.Hero.buildingPosY]
        )

        if (time.time() - self.lastRenderedTime) > self.delta_T:
            self.moveByClick()

        # Updating the rect according to the possible movements
        self.rect.topleft = self.pos
        self.rectChunk.topleft = self.chunkPos

        self._updateAnim()
        if self.playerDetected:
            self._updateBubble()

        self.surf.blit(
            self.animationFrames[self.state][self.AnimIndex[self.state]], (0, 0)
        )
        self.parentSurface.blit(self.surf, self.rect)
        self.parentSurface.blit(self.bubbleSurf, self.bubbleRect)

    def setPos(self, pos):

        self.pos = list(pos)  # Need to be a topleft

    def moveByClick(self):

        # Computing the direction to get
        if not (
            abs(self.XDistanceToTarget) <= self.normalizedDistance
            and abs(self.YDistanceToTarget) <= self.normalizedDistance
        ):
            self.prevDir = self.direction

            if abs(self.XDistanceToTarget) >= abs(self.YDistanceToTarget):

                self.direction = "right" if self.XDistanceToTarget > 0 else "left"

            else:
                self.direction = "down" if self.YDistanceToTarget > 0 else "up"

            # First checking collision with the open world then computing and updating character pos
            if not self.envGenerator.isColliding(
                self.rectChunk, self.direction, "Ennemy"
            ):

                # Modifying bliting point of the background (make it "scroll" on the character)
                DELTA_X = (
                    self.keys[self.direction]["value"][0] * self.normalizedDistance
                )
                DELTA_Y = (
                    self.keys[self.direction]["value"][1] * self.normalizedDistance
                )

                # Updating the distance between the target and the character
                self.XDistanceToTarget -= DELTA_X
                self.YDistanceToTarget -= DELTA_Y

                self.pos[0] += DELTA_X
                self.pos[1] += DELTA_Y
                self.chunkPos[0] += DELTA_X
                self.chunkPos[1] += DELTA_Y

            else:
                if not self.playerDetected:
                    self.idle_updating()
                else:
                    self.targetPlayer()

        else:
            self.state = "Idle"
            self.prevState = "Walk"
            if not self.playerDetected and self.state == "Idle":
                self.idle_updating()
            elif self.playerDetected:
                self.Hero.createFight()

    def idle_updating(self):
        """Click randomly around the initial pos to simulate a moving ennemy.
        Chasing state from idle to Walk."""

        if (time.time() - self.lastClicked) > random.uniform(*CLICK_TIME_RANGE):
            self.lastClicked = time.time()

            self.targetPos = [
                coor
                + random.uniform(
                    -self.Hero.Map.stepGeneration, self.Hero.Map.stepGeneration
                )
                for coor in self.initPos
            ]
            self.XDistanceToTarget = self.targetPos[0] - self.chunkPos[0]
            self.YDistanceToTarget = self.targetPos[1] - self.chunkPos[1]

            self.prevState = "Idle"
            self.state = "Walk"
