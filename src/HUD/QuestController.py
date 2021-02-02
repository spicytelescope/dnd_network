from UI.UI_utils_text import Dialog
from copy import deepcopy
from config.UIConf import BUTTON_FONT_SIZE, DUNGEON_FONT
from config.openWorldConf import DUNGEON_FOG
import math
from time import *
from collections import Counter

import pygame
from config import HUDConf, itemConf, spellsConf
from pygame.constants import KEYDOWN
from utils.utils import logger
from UI.UI_utils_fonc import formatDialogContent


class QuestController:
    """Quest controller, currently supports 2 types of tasks :
    + getting an amount of <player stat> (e.g DEX, STR, Money, ATK ....)
    + getting some items in the player's inventory
    """

    def __init__(self, gameController, Hero) -> None:

        self.quests = []
        self.questsEnded = []
        self.questContainer = [self.quests, self.questsEnded]
        self.Hero = Hero
        self.Game = gameController
        self.open = False

        self.MAX_PAGE = math.ceil(len(self.Hero.spellsID) / 3)
        self.MAX_PAGE_INDEX = self.MAX_PAGE - 1
        self.pageIndex = 0
        self.buttonIndex = 0

        # ----------- TEXTURES ----------------- #

        self.openAnimFrames = [
            pygame.transform.scale(img, (self.Game.resolution, self.Game.resolution))
            for img in HUDConf.QUEST_OPEN_ANIM_FRAMES
        ]
        self.closeAnimFrames = [
            pygame.transform.scale(img, (self.Game.resolution, self.Game.resolution))
            for img in HUDConf.QUEST_CLOSE_ANIM_FRAMES
        ]

        self.mainSurf = pygame.transform.scale(
            HUDConf.QUEST_JOURNAL_MAIN_SURF,
            (int(self.Game.resolution * 0.9), int(self.Game.resolution * 0.9)),
        )

        self.rect = self.mainSurf.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.bg = None

        self.buttons = HUDConf.QUESTS_BUTTONS
        for button in self.buttons:
            self.buttons[button]["rect"] = self.buttons[button]["surf"].get_rect(
                center=tuple(self.buttons[button]["blitPoint"])
            )

        self.buttons["back"]["effect"] = lambda: self.transition(
            "back", 1, None
        )
        self.buttons["next"]["effect"] = lambda: self.transition(
            "next", 1, None
        )

        self.toolBarLayout = [
            HUDConf.QUEST_PROGRESS_BAR,
            HUDConf.QUEST_COMPLETED_BAR,
        ]

        self.toolButtonsRects = [
            pygame.Rect(265, 161, 230, 50),
            pygame.Rect(506, 166, 240, 48),
        ]

        self.toolBarLayoutRect = self.toolBarLayout[0].get_rect(
            center=(
                self.rect.width // 2,
                int(self.rect.height * 0.15),
            )
        )

    def addQuest(self, quest):
        # template = {
        #     "id" : time.time(),
        #     "name": "some_name",
        #     "tasks": {
        #         "Money": self.Hero.stats["Money"] + 50,
        #         "Items": {"Mushroom's skin": 5},
        #     },
        #     "reward": {"Money": 50, "Items": [5, 7]},  # ids of the items
        #     "desc": "Here is a sample description",
        #     "textReward": "Thanks for saving me !",
        # }
        self.quests.append({"id": int(time()), **quest})

    def removeQuest(self, questId):

        for i, quest in enumerate(self.questsEnded):

            if quest["id"] == questId:
                self.questsEnded.pop(i)

    def transition(self, name, time=1, frames=None):

        self.MAX_PAGE = math.ceil(len(self.quests) / 3)
        self.MAX_PAGE_INDEX = self.MAX_PAGE - 1
        self.pageIndex = 0

        if name == "open":
            self.bg = self.Game.screen.copy()
            self.open = True
        elif name == "close":
            self.open = False
        elif name == "next":
            self.pageIndex += 1 if self.pageIndex != self.MAX_PAGE_INDEX else 0
        elif name == "back":
            self.pageIndex -= 1 if self.pageIndex != 0 else 0

        if frames != None:
            for frame in frames:
                self.Game.screen.blit(self.bg, (0, 0))
                self.Game.screen.blit(
                    pygame.transform.scale(
                        frame,
                        (
                            int(self.Game.resolution * 0.9),
                            int(self.Game.resolution * 0.9),
                        ),
                    ),
                    self.rect,
                )
                self.Game.show(combatMode=False)
                sleep(time / len(frames))

    def getReward(self, questId):

        if self.questsEnded != []:
            quest = [quest for quest in self.questsEnded if quest["id"] == questId][0]
            for taskName, taskValue in quest["reward"].items():
                if taskName in self.Hero.stats:
                    self.Hero.stats[taskName] += taskValue

                elif "Item" in taskName:  # Id
                    itemPlaced = False
                    for j in range(HUDConf.INVENTORY_STORAGE_HEIGHT):
                        for i in range(HUDConf.INVENTORY_STORAGE_WIDTH):
                            if (
                                self.Hero.Inventory.storage["tab"][j][i] == None
                                and not itemPlaced
                            ):
                                self.Hero.Inventory.storage["tab"][j][i] = deepcopy(
                                    itemConf.ITEM_DB[taskValue]
                                )
                                self.Hero.Inventory.storage["tab"][j][i].loadIcon()
                                self.Hero.Inventory.storage["tab"][j][i].loadSurfDesc()
                                self.Hero.Inventory.storage["tab"][j][i].setCoor(
                                    (
                                        self.Hero.Inventory.storage["initPoint"][0]
                                        + i * self.Hero.Inventory.storage["offset"][0],
                                        self.Hero.Inventory.storage["initPoint"][1]
                                        + j * self.Hero.Inventory.storage["offset"][1],
                                    )
                                )
                                itemPlaced = True

                    if not itemPlaced:

                        Dialog(
                            "You've got not enough space to store this item.",
                            (self.Game.resolution // 2, self.Game.resolution // 2),
                            self.Game.screen,
                            (255, 0, 0),
                            self.Game,
                            error=True,
                            charLimit=100,
                        ).mainShow()

    def show(self):

        if not self.open:
            self.transition("open", HUDConf.QUEST_OPEN_ANIM_TIME, self.openAnimFrames)

        while self.open:

            self.mainSurf = pygame.transform.scale(
                HUDConf.QUEST_JOURNAL_MAIN_SURF,
                (int(self.Game.resolution * 0.9), int(self.Game.resolution * 0.9)),
            )

            # ------------ QUEST CHECKING  ---------------- #

            inventoryItemNames = Counter(
                [
                    self.Hero.Inventory.storage["tab"][j][i].property["name"]
                    for j in range(HUDConf.INVENTORY_STORAGE_HEIGHT)
                    for i in range(HUDConf.INVENTORY_STORAGE_WIDTH)
                    if self.Hero.Inventory.storage["tab"][j][i] != None
                ]
            )

            for questIndex, quest in enumerate(self.quests):
                for taskName, taskGoal in quest["tasks"].items():
                    tasksDone = 0
                    for statName in self.Hero.stats:
                        if (
                            taskName == statName
                            and self.Hero.stats[statName] >= taskGoal
                        ):
                            tasksDone += 1

                    if taskName == "Items" and all(
                        [
                            itemOccurence == inventoryItemNames[itemName]
                            for itemName, itemOccurence in taskGoal.items()
                        ]
                    ):
                        tasksDone += 1

                    if tasksDone == len(quest["tasks"]):
                        logger.info(f"QUEST {quest['name']} COMPLETED")
                        self.questsEnded.append(self.quests.pop(questIndex))

            # ------------------- GRAPHICAL UPDATE ----------------- #

            for event in pygame.event.get():

                if (
                    event.type == pygame.KEYDOWN
                    and event.key
                    == self.Game.KeyBindings["Open quest's Journal"]["value"]
                ):
                    self.transition(
                        "close", HUDConf.QUEST_CLOSE_ANIM_TIME, self.closeAnimFrames
                    )

                #  ------------ QUEST SELECTION ----------- #
                if event.type == pygame.MOUSEBUTTONDOWN:

                    for i, rect in enumerate(self.toolButtonsRects):
                        if rect.collidepoint(pygame.mouse.get_pos()):
                            self.buttonIndex = i
                            continue

                # --------- PAGE SELECTION ------------ #

                for button in self.buttons:

                    if button == "next" and self.pageIndex == self.MAX_PAGE_INDEX:
                        continue
                    elif button == "back" and self.pageIndex == 0:
                        continue

                    if self.buttons[button]["rect"].collidepoint(
                        pygame.mouse.get_pos()
                    ):

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.buttons[button]["effect"]()

            if self.open:
                self.Game.screen = self.bg.copy()

                #  ----------------------- QUEST TYPE BLITING ------------------- #

                if self.questContainer[self.buttonIndex] != [] and self.pageIndex < len(
                    self.questContainer[self.buttonIndex]
                ):

                    # ------------------------- NAME --------------------- #

                    fontName = pygame.font.Font(DUNGEON_FONT, 100).render(
                        self.questContainer[self.buttonIndex][self.pageIndex]["name"],
                        True,
                        (0, 0, 0),
                    )
                    self.mainSurf.blit(
                        fontName,
                        fontName.get_rect(
                            center=(self.rect.width // 2, int(self.rect.height * 0.25))
                        ),
                    )

                    # -------------------- DESC --------------------- #

                    for i, text in enumerate(
                        formatDialogContent(
                            self.questContainer[self.buttonIndex][self.pageIndex][
                                "desc"
                            ],
                            40,
                        )
                    ):
                        fontName = pygame.font.Font(DUNGEON_FONT, 50)
                        fontName.italic = True
                        fontName = fontName.render(text, True, (0, 0, 0))
                        self.mainSurf.blit(
                            fontName,
                            fontName.get_rect(
                                center=(
                                    int(self.rect.width * 0.55),
                                    int(
                                        i * fontName.get_height() * 0.75
                                        + self.rect.height * 0.32
                                    ),
                                )
                            ),
                        )

                    # ------------------- TASKS ----------------- #

                    fontName = pygame.font.Font(DUNGEON_FONT, 80).render(
                        "Tasks : ", True, (0, 0, 0)
                    )
                    self.mainSurf.blit(
                        fontName,
                        fontName.get_rect(
                            center=(
                                int(self.rect.width * 0.30),
                                int(self.rect.height * 0.5),
                            )
                        ),
                    )

                    for i, (taskName, taskValue) in enumerate(
                        self.questContainer[self.buttonIndex][self.pageIndex][
                            "tasks"
                        ].items()
                    ):

                        if "Item" in taskName:
                            for itemName, itemOccurence in taskValue.items():
                                fontName = pygame.font.Font(DUNGEON_FONT, 50)
                                fontName.bold = all(
                                    [itemOccurence == inventoryItemNames[itemName]]
                                )
                                fontName = fontName.render(
                                    f"- Get {itemName} : {inventoryItemNames[itemName] if inventoryItemNames[itemName] < itemOccurence else itemOccurence}/{itemOccurence}",
                                    True,
                                    (0, 0, 0),
                                )

                        elif taskName in self.Hero.stats:
                            fontName = pygame.font.Font(DUNGEON_FONT, 50)
                            fontName.bold = self.Hero.stats[taskName] >= taskValue
                            fontName = fontName.render(
                                f"- Get {taskName} : {self.Hero.stats[taskName] if self.Hero.stats[taskName] < taskValue else taskValue}/{taskValue}",
                                True,
                                (0, 0, 0),
                            )

                        self.mainSurf.blit(
                            fontName,
                            fontName.get_rect(
                                center=(
                                    int(self.rect.width * 0.30),
                                    int(
                                        self.rect.height * 0.55
                                        + i * fontName.get_height() * 0.75
                                    ),
                                )
                            ),
                        )

                    # ----------------- REWARD --------------------- #

                    fontName = pygame.font.Font(DUNGEON_FONT, 80).render(
                        "Reward : ", True, (0, 0, 0)
                    )
                    self.mainSurf.blit(
                        fontName,
                        fontName.get_rect(
                            center=(
                                int(self.rect.width * 0.70),
                                self.rect.height // 2,
                            )
                        ),
                    )

                    for i, (taskName, taskValue) in enumerate(
                        self.questContainer[self.buttonIndex][self.pageIndex][
                            "reward"
                        ].items()
                    ):

                        if "Item" in taskName:

                            item = itemConf.ITEM_DB[taskValue]
                            fontName = pygame.font.Font(DUNGEON_FONT, 50).render(
                                item.property["name"],
                                True,
                                itemConf.RARETY_TYPES[item.property["rarety"]]["color"],
                            )

                        elif taskName in self.Hero.stats:
                            fontName = pygame.font.Font(DUNGEON_FONT, 50).render(
                                f"{taskName} : {taskValue} "
                                if taskName == "Money"
                                else f"{taskName} : {taskValue} points",
                                True,
                                (0, 0, 0),
                            )

                        self.mainSurf.blit(
                            fontName,
                            fontName.get_rect(
                                center=(
                                    int(self.rect.width * 0.70),
                                    int(
                                        self.rect.height * 0.55
                                        + i * fontName.get_height() * 0.75
                                    ),
                                )
                            ),
                        )

                    pygame.draw.line(
                        self.mainSurf,
                        (0, 0, 0),
                        (self.rect.width // 2, self.rect.height // 2),
                        (self.rect.width // 2, int(self.rect.height * 0.8)),
                        10,
                    )
                else:
                    noQuestSurf = pygame.font.Font(
                        DUNGEON_FONT, int(BUTTON_FONT_SIZE * 1.75)
                    ).render(
                        "No quests taken for the moment !"
                        if self.buttonIndex == 0
                        else "No quests completed !",
                        True,
                        (0, 0, 0),
                    )
                    self.mainSurf.blit(
                        noQuestSurf,
                        noQuestSurf.get_rect(
                            center=(self.rect.width // 2, self.rect.height // 2)
                        ),
                    )

                self.mainSurf.blit(
                    self.toolBarLayout[self.buttonIndex], self.toolBarLayoutRect
                )
                self.Game.screen.blit(self.mainSurf, self.rect)

                for button in self.buttons:
                    if self.buttons[button]["rect"].collidepoint(
                        pygame.mouse.get_pos()
                    ):

                        self.Game.screen.blit(
                            self.buttons[button]["surfClicked"],
                            self.buttons[button]["rect"],
                        )
                    else:
                        self.Game.screen.blit(
                            self.buttons[button]["surf"], self.buttons[button]["rect"]
                        )

                self.Game.show()