import time
from os import listdir
from os.path import isfile, join

import config.textureConf as textureConf
import pygame
from config.NPCConf import *
from config.playerConf import *
from pygame.constants import SRCALPHA
from UI.UI_utils_text import SelectPopUp
from UI.SellerInterface import *
from UI.UI_utils_text import Dialog


class NPC:

    """
    Meta class representing an NPC entity.
    """

    def __init__(
        self, parentSurface, defaultState, Hero, gameController, name="", profession=""
    ) -> None:

        self.states = NPC_STATES
        self.state = defaultState  # Talkable
        self.openable = False  # for envGenerator
        self.npcName = name
        self.profession = profession
        self.Hero = Hero
        self.Game = gameController
        self.questGiven = False

        # -------- NPC TEXTURE --------- #

        self.parentSurface = parentSurface
        self.pos = [0, 0]  # topleft !

        # STATE BUBBLE
        self.bubbleAnim = []
        self.lastRenderedNPCBubble = time.time()
        self.NPCBubbleDeltaTime = None
        self.bubbleIndex = 0
        self.bubbleRect = None
        self.bubbleSurf = None

        # PNJ TEXTURE
        self.animationFramesPath = None
        self.animationFrames = []
        self.lastRenderedNPC = time.time()
        self.NPCAnimDeltaTime = None
        self.NPCAnimIndex = 0
        self.NPCRect = None
        self.surf = None

    def init(self, pos, zoomed=False):

        self.pos = pos  # Need to be a topleft
        self.changeState(self.state)  #  Loading bubble textures

        self.animationFrames = [
            pygame.transform.scale(
                pygame.image.load(
                    f"./assets/world_textures/NPC/{self.profession}/{self.npcName}/frames/{f}"
                ).convert_alpha(),
                (PLAYER_SIZE, PLAYER_SIZE),
            )
            for f in listdir(
                f"./assets/world_textures/NPC/{self.profession}/{self.npcName}/frames"
            )
            if isfile(
                join(
                    f"./assets/world_textures/NPC/{self.profession}/{self.npcName}/frames",
                    f,
                )
            )
        ]

        self.speakerFrame = pygame.image.load(
            f"./assets/world_textures/NPC/{self.profession}/{self.npcName}/default.png"
        )

        if zoomed:
            self.animationFrames = [
                pygame.transform.scale2x(frame) for frame in self.animationFrames
            ]

        self.NPCAnimDeltaTime = NPC_ANIM_TIME / len(self.animationFrames)
        self.NPCRect = self.animationFrames[0].get_rect(topleft=self.pos)
        self.surf = pygame.Surface(self.NPCRect.size, SRCALPHA)

        # ------------ QUEST HANDLING -------------- #

        self.quest = random.choice(NPC_QUESTS)

        for taskName, taskValue in self.quest["tasks"].items():

            if taskName in self.Hero.stats:
                taskValue += self.Hero.stats[taskName]

    def changeState(self, stateName):

        self.state = stateName
        assert stateName in NPC_STATES, logger.error("NEW NPC STATE UNKNOWN")

        self.bubbleAnim = [
            pygame.transform.scale(
                pygame.image.load(
                    f"./assets/world_textures/NPC/stateBubble/{stateName}/{f}"
                ),
                (PLAYER_SIZE, PLAYER_SIZE),
            )
            for f in listdir(f"./assets/world_textures/NPC/stateBubble/{stateName}/")
            if isfile(join(f"./assets/world_textures/NPC/stateBubble/{stateName}/", f))
        ]
        self.NPCBubbleDeltaTime = NPC_BUBBLE_ANIM_TIME / len(self.bubbleAnim)
        self.bubbleRect = self.bubbleAnim[0].get_rect(
            topleft=[self.pos[0], self.pos[1] - (self.bubbleAnim[1].get_height() + 5)]
        )
        self.bubbleSurf = pygame.Surface(self.bubbleRect.size, SRCALPHA)

    def _updateAnimation(self):

        # Updating NPC
        if (time.time() - self.lastRenderedNPC) > self.NPCAnimDeltaTime:

            self.lastRenderedNPC = time.time()
            self.NPCAnimIndex = (self.NPCAnimIndex + 1) % len(self.animationFrames)

        # Updating info bubble
        if (time.time() - self.lastRenderedNPCBubble) > self.NPCBubbleDeltaTime:

            self.lastRenderedNPCBubble = time.time()
            self.bubbleIndex = (self.bubbleIndex + 1) % len(self.bubbleAnim)

    def show(self):

        """
        Blit the updated animations on the parent surface
        """

        self._updateAnimation()
        self.surf.fill((255, 255, 255, 0))

        self.surf.blit(self.animationFrames[self.NPCAnimIndex], (0, 0))
        self.bubbleSurf.blit(self.bubbleAnim[self.bubbleIndex], (0, 0))
        self.parentSurface.blit(self.surf, self.NPCRect)
        self.parentSurface.blit(self.bubbleSurf, self.bubbleRect)

    def openDialog(self):

        if self.state in ["Talk-only", "Interactable"]:
            Dialog(
                random.choice(NPC_DIALOGS[self.profession]),
                (self.Game.resolution // 2, int(self.Game.resolution * 0.7)),
                self.Game.screen,
                (0, 0, 0),
                self.Game,
                speakerFrame=self.speakerFrame,
            ).mainShow()

        elif self.state == "Quest":
            if not self.questGiven:
                Dialog(
                    self.quest["desc"],
                    (self.Game.resolution // 2, int(self.Game.resolution * 0.7)),
                    self.Game.screen,
                    (0, 0, 0),
                    self.Game,
                    speakerFrame=self.speakerFrame,
                ).mainShow()
                SelectPopUp(
                    {
                        "Accept": self.giveQuest,
                        "Decline": lambda: None,
                    },
                    self.Game.screen,
                    self.Game,
                    (self.Game.resolution // 2, self.Game.resolution // 2),
                ).show()

            elif self.questGiven and self.quest["id"] in [
                quest["id"] for quest in self.Hero.QuestJournal.questsEnded
            ]:
                Dialog(
                    self.quest["textReward"],
                    (self.Game.resolution // 2, int(self.Game.resolution * 0.7)),
                    self.Game.screen,
                    (0, 0, 0),
                    self.Game,
                    speakerFrame=self.speakerFrame,
                ).mainShow()

                self.Hero.QuestJournal.getReward(self.quest["id"])
            else:
                Dialog(
                    random.choice(NPC_DIALOGS[self.profession]),
                    (self.Game.resolution // 2, int(self.Game.resolution * 0.7)),
                    self.Game.screen,
                    (0, 0, 0),
                    self.Game,
                    speakerFrame=self.speakerFrame,
                ).mainShow()

    def giveQuest(self):

        self.questGiven = True
        self.Hero.QuestJournal.addQuest(self.quest)
        self.quest["id"] = self.Hero.QuestJournal.quests[-1]["id"]


class Seller(NPC):
    def __init__(
        self, parentSurface, defaultGoldAmount, gameController, Hero, Name
    ) -> None:

        super().__init__(
            parentSurface,
            "Interactable",
            Hero,
            gameController,
            name=Name,
            profession="Seller",
        )

        self.goldAmount = defaultGoldAmount
        self.Game = gameController
        self.Hero = Hero

        # UI Interface
        self.sellerInterface = SellerInterface(self.Game, self.Hero, self)
        self.SellerChoice = {
            "Talk to the Seller": lambda: self.openDialog(),
            "Buy items from the Seller": lambda: self.sellerInterface.show(),
        }

    def openInterface(self):

        SelectPopUp(
            self.SellerChoice,
            self.Game.screen,
            self.Game,
            (self.Game.resolution // 2, self.Game.resolution // 2),
        ).show()