from config.playerConf import INVENTORY_STORAGE_INIT_POS_CHEST
from pygame.constants import MOUSEBUTTONDOWN
from config.itemConf import *
from config.HUDConf import *
import config.textureConf as textureConf
import config.itemConf as itemConf
import pygame, random, time
from .Item import Item
import copy

class Chest:

    """
    Class representing a chest, which is a storage UI opened and closed with an animation.
    The chest is initialised with a default content which can be empty.
    """

    def __init__(self, gameController, Hero, defaultContent: list = None):

        self.Game = gameController
        self.openable = False
        self.open = False
        self.firstOpen = True
        self.Hero = Hero

        # ------------ CHEST TEXTURE ----------------- #

        self.HUD_blank = pygame.transform.scale(
            textureConf.WORLD_ELEMENTS["GameObject"]["Chest"]["CHEST_SURF"],
            (
                int(
                    INVENTORY_SURF_RATIO
                    * self.Game.resolution
                    // 2
                    * self.Game.resolutionFactor
                ),
                int(self.Game.resolution // 2 * self.Game.resolutionFactor),
            ),
        )
        self.HUD = self.HUD_blank.copy()
        self.rect = self.HUD.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )

        # -------------------- ITEMS ---------------- #

        self.defaultContent = defaultContent

        self.storage = {
            "tab": [
                [None for _ in range(CHEST_STORAGE_WIDTH)]
                for _ in range(CHEST_STORAGE_HEIGHT)
            ],
            # [coor*self.Game.resolutionFactor for coor in INVENTORY_STORAGE_INIT_POS],
            "initPoint": INVENTORY_STORAGE_INIT_POS_CHEST,
            # [coor*self.Game.resolutionFactor for coor in INVENTORY_STORAGE_OFFSET]}
            "offset": INVENTORY_STORAGE_OFFSET,
        }

        self.storageLength = [CHEST_STORAGE_WIDTH, CHEST_STORAGE_HEIGHT]
        self.numRestriction = [DEFAULT_NUM_CHEST_MIN, DEFAULT_NUM_CHEST_MAX]

        # ------------------ ITEM HANDLING -------------------- #

        # If none is dragged, set "coor" to empty array
        self.draggedItem = {
            "coor": [],
            "origin": "",  # Can be either chestStorage or inventoryStorage
        }

    def initChest(self) -> None:
        """
        Take the item of the defaultContent of the chest and place them at random position in the storage.
        """
        if self.defaultContent != None:
            for item in self.defaultContent:
                i, j = 0, 0
                while self.storage["tab"][j][i] != None:
                    i = random.randint(0, self.storageLength[0] - 1)
                    j = random.randint(0, self.storageLength[1] - 1)

                self.storage["tab"][j][i] = copy.deepcopy(item)
                item.loadSurfDesc()
                item.loadIcon()
                item.setCoor(
                    (
                        self.storage["initPoint"][0] + i * self.storage["offset"][0],
                        self.storage["initPoint"][1] + j * self.storage["offset"][1],
                    )
                )
        else:
            for aleat_id in [
                random.choice(list(itemConf.ITEM_DB.keys()))
                for _ in range(random.choice(self.numRestriction))
            ]:
                i, j = 0, 0
                while self.storage["tab"][j][i] != None:
                    i = random.randint(0, self.storageLength[0] - 1)
                    j = random.randint(0, self.storageLength[1] - 1)

                self.storage["tab"][j][i] = copy.deepcopy(itemConf.ITEM_DB[aleat_id])
                self.storage["tab"][j][i].loadSurfDesc()
                self.storage["tab"][j][i].loadIcon()
                self.storage["tab"][j][i].setCoor(
                    (
                        self.storage["initPoint"][0] + i * self.storage["offset"][0],
                        self.storage["initPoint"][1] + j * self.storage["offset"][1],
                    )
                )

    def transition(self, name, frames, animationTime):

        if name == "open":
            if self.openable:
                self.bg = self.Game.screen.copy()
                self.open = True

                if self.firstOpen:
                    self.initChest()
                    self.firstOpen = False
            else:
                return

        elif name == "close":
            self.open = False

        for frame in frames:
            rect = frame.get_rect(
                center=(self.Game.resolution // 2, self.Game.resolution // 2)
            )
            self.Game.screen.blit(self.bg, (0, 0))
            self.Game.screen.blit(frame, rect)
            self.Game.show()
            time.sleep(animationTime / len(frames))

        self.Game.screen.blit(self.bg, (0, 0))

    def checkActions(self, event):

        # ------------ ITEMS ACTION CHECKING --------- #

        self._checkItemSelection(event)
        self._handleDragSpot(event)

        # ---------- EXIT HANDLING ----------- #

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def __handleDragging(self, i, j, storageName):
        """Method handling the dragging considering that there is an item dragged at the case on coordonates (i,j) on the storage identified by <storageName>"""

        if (
            self.draggedItem["origin"] == "chestStorage"
        ):  # Means dragged item is from chest storage
            # If the item is dragged with himself, cancel

            # chest(dragged) -> chest
            if storageName == "chestStorage":

                if [i, j] == self.draggedItem["coor"]:
                    self.draggedItem["coor"] = []
                else:

                    (
                        self.storage["tab"][self.draggedItem["coor"][1]][
                            self.draggedItem["coor"][0]
                        ],
                        self.storage["tab"][j][i],
                    ) = (
                        self.storage["tab"][j][i],
                        self.storage["tab"][self.draggedItem["coor"][1]][
                            self.draggedItem["coor"][0]
                        ],
                    )

                    # Switching rect by updating coors
                    draggedCoor = self.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ].centerCoor

                    self.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ].setCoor(self.storage["tab"][j][i].centerCoor)
                    self.storage["tab"][j][i].setCoor(draggedCoor)

                    self.draggedItem["coor"] = []

            # chest(dragged)->inventory
            else:

                (
                    self.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ],
                    self.Hero.Inventory.storage["tab"][j][i],
                ) = (
                    self.Hero.Inventory.storage["tab"][j][i],
                    self.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ],
                )

                # Switching rect by updating coors
                draggedCoor = self.storage["tab"][self.draggedItem["coor"][1]][
                    self.draggedItem["coor"][0]
                ].centerCoor

                self.storage["tab"][self.draggedItem["coor"][1]][
                    self.draggedItem["coor"][0]
                ].setCoor(self.Hero.Inventory.storage["tab"][j][i].centerCoor)
                self.Hero.Inventory.storage["tab"][j][i].setCoor(draggedCoor)

            self.draggedItem["coor"] = []

        elif (
            self.draggedItem["origin"] == "inventoryStorage"
        ):  # dragged item is from the inventory storage

            # If the item is dragged with himself, cancel

            # inventory(dragged) -> inventory
            if storageName == "inventoryStorage":

                if [i, j] == self.draggedItem["coor"]:
                    self.draggedItem["coor"] = []
                else:

                    (
                        self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                            self.draggedItem["coor"][0]
                        ],
                        self.Hero.Inventory.storage["tab"][j][i],
                    ) = (
                        self.Hero.Inventory.storage["tab"][j][i],
                        self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                            self.draggedItem["coor"][0]
                        ],
                    )

                    # Switching rect by updating coors
                    draggedCoor = self.Hero.Inventory.storage["tab"][
                        self.draggedItem["coor"][1]
                    ][self.draggedItem["coor"][0]].centerCoor

                    self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ].setCoor(self.Hero.Inventory.storage["tab"][j][i].centerCoor)
                    self.Hero.Inventory.storage["tab"][j][i].setCoor(draggedCoor)

                    self.draggedItem["coor"] = []

            # inventory(dragged)->chest
            else:

                (
                    self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ],
                    self.storage["tab"][j][i],
                ) = (
                    self.storage["tab"][j][i],
                    self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ],
                )

                # Switching rect by updating coors
                draggedCoor = self.Hero.Inventory.storage["tab"][
                    self.draggedItem["coor"][1]
                ][self.draggedItem["coor"][0]].centerCoor

                self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                    self.draggedItem["coor"][0]
                ].setCoor(self.storage["tab"][j][i].centerCoor)

                self.storage["tab"][j][i].setCoor(draggedCoor)
                self.draggedItem["coor"] = []

    def __handleDraggingToEmptyCase(self, i, j, storageName):

        if self.draggedItem["coor"] != []:
            if storageName == "chestStorage":
                # chest -> chest_emptyCase

                if self.draggedItem["origin"] == "chestStorage":
                    self.storage["tab"][j][i] = self.storage["tab"][
                        self.draggedItem["coor"][1]
                    ][self.draggedItem["coor"][0]]

                    self.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ] = None

                    self.storage["tab"][j][i].setCoor(
                        [
                            self.storage["initPoint"][0]
                            + i * self.storage["offset"][0],
                            self.storage["initPoint"][1]
                            + j * self.storage["offset"][1],
                        ]
                    )

                    self.draggedItem["coor"] = []

                # inventory -> chest_emptyCase
                else:

                    self.storage["tab"][j][i] = self.Hero.Inventory.storage["tab"][
                        self.draggedItem["coor"][1]
                    ][self.draggedItem["coor"][0]]

                    self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ] = None

                    self.storage["tab"][j][i].setCoor(
                        [
                            self.storage["initPoint"][0]
                            + i * self.storage["offset"][0],
                            self.storage["initPoint"][1]
                            + j * self.storage["offset"][1],
                        ]
                    )
                    self.draggedItem["coor"] = []

            elif storageName == "inventoryStorage":

                # inventory -> inventory_emptyCase

                if self.draggedItem["origin"] == "inventoryStorage":
                    self.Hero.Inventory.storage["tab"][j][
                        i
                    ] = self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ]
                    self.Hero.Inventory.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ] = None

                    self.Hero.Inventory.storage["tab"][j][i].setCoor(
                        [
                            self.Hero.Inventory.storage["initPoint"][0]
                            + i * self.Hero.Inventory.storage["offset"][0],
                            self.Hero.Inventory.storage["initPoint"][1]
                            + j * self.Hero.Inventory.storage["offset"][1],
                        ]
                    )

                    self.draggedItem["coor"] = []

                # chest -> inventory_emptyCase
                else:

                    self.Hero.Inventory.storage["tab"][j][i] = self.storage["tab"][
                        self.draggedItem["coor"][1]
                    ][self.draggedItem["coor"][0]]
                    self.storage["tab"][self.draggedItem["coor"][1]][
                        self.draggedItem["coor"][0]
                    ] = None

                    self.Hero.Inventory.storage["tab"][j][i].setCoor(
                        [
                            self.Hero.Inventory.storage["initPoint"][0]
                            + i * self.Hero.Inventory.storage["offset"][0],
                            self.Hero.Inventory.storage["initPoint"][1]
                            + j * self.Hero.Inventory.storage["offset"][1],
                        ]
                    )
                    self.draggedItem["coor"] = []

    def _checkItemSelection(self, event):
        """method handling the dragging of an item, the displaying of information if one item's icon is hovered"""

        mousePosTranslated = [
            coor - self.rect.topleft[i]
            for coor, i in zip(pygame.mouse.get_pos(), [0, 1])
        ]

        # ------------------ CHEST STORAGE HANDLING -------------- #

        for j in range(CHEST_STORAGE_HEIGHT):
            for i in range(CHEST_STORAGE_WIDTH):

                if self.storage["tab"][j][i] != None:

                    # Checking item selection
                    if self.storage["tab"][j][i].rect.collidepoint(mousePosTranslated):
                        # The case is an item, we handle swaping and dragging

                        # Check if the item is clicked or not
                        if event.type == MOUSEBUTTONDOWN and event.button == 1:
                            if self.draggedItem["coor"] == []:
                                self.draggedItem = {
                                    "coor": [i, j],
                                    "origin": "chestStorage",
                                }
                            else:
                                self.__handleDragging(i, j, "chestStorage")

                else:  # The case is empty and clicked, if there is a dragging running in, place the object on the case

                    # Creating a rect for the empty case
                    emptyCaseRect = pygame.Surface(
                        (ITEM_ICON_DIM[0], ITEM_ICON_DIM[1])
                    ).get_rect(
                        center=(
                            self.storage["initPoint"][0]
                            + i * self.storage["offset"][0],
                            self.storage["initPoint"][1]
                            + j * self.storage["offset"][1],
                        )
                    )

                    if (
                        event.type == MOUSEBUTTONDOWN
                        and event.button == 1
                        and emptyCaseRect.collidepoint(mousePosTranslated)
                    ):
                        self.__handleDraggingToEmptyCase(i, j, "chestStorage")

        # ------------------ INVENTORY STORAGE HANDLING -------------- #

        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):

                if self.Hero.Inventory.storage["tab"][j][i] != None:

                    # Checking item selection
                    if self.Hero.Inventory.storage["tab"][j][i].rect.collidepoint(
                        mousePosTranslated
                    ):
                        # The case is an item, we handle swaping and dragging

                        # Check if the item is clicked or not
                        if event.type == MOUSEBUTTONDOWN and event.button == 1:
                            if self.draggedItem["coor"] == []:
                                self.draggedItem = {
                                    "coor": [i, j],
                                    "origin": "inventoryStorage",
                                }
                            else:
                                self.__handleDragging(i, j, "inventoryStorage")

                else:  # The case is empty and clicked, if there is a dragging running in, place the object on the case

                    # Creating a rect for the empty case
                    emptyCaseRect = pygame.Surface(
                        (ITEM_ICON_DIM[0], ITEM_ICON_DIM[1])
                    ).get_rect(
                        center=(
                            self.Hero.Inventory.storage["initPoint"][0]
                            + i * self.Hero.Inventory.storage["offset"][0],
                            self.Hero.Inventory.storage["initPoint"][1]
                            + j * self.Hero.Inventory.storage["offset"][1],
                        )
                    )

                    if (
                        event.type == MOUSEBUTTONDOWN
                        and event.button == 1
                        and emptyCaseRect.collidepoint(mousePosTranslated)
                    ):
                        self.__handleDraggingToEmptyCase(i, j, "inventoryStorage")

    def _showItems(self):

        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):
                if self.Hero.Inventory.storage["tab"][j][i] != None:
                    self.HUD.blit(
                        self.Hero.Inventory.storage["tab"][j][i].icon,
                        self.Hero.Inventory.storage["tab"][j][i].rect,
                    )

        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):
                if self.storage["tab"][j][i] != None:
                    self.HUD.blit(
                        self.storage["tab"][j][i].icon,
                        self.storage["tab"][j][i].rect,
                    )

    def _handleDragSpot(self, event):
        """Method showing the dragged item onto the mouse and
        putting it somewhere given actions describes as follows.

        If the player left click while dragging an item on :
        - an other item icon in the storage : swap with it (handle by _checkItemSelection method)
        - an other item icon in the equipment : swap if it's the same object type
        - somewhere outside of the surf : cancel the dragging and put the item icon at his place"""

        if self.draggedItem["coor"] != []:

            # Showing the dragged item on the left of the mouse
            # We don't translate the mouse pos as the item can be dragged onto the entier screen

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if not self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.draggedItem["coor"] = []

    def _showDraggedItem(self):

        if self.draggedItem["coor"] != []:

            if self.draggedItem["origin"] == "chestStorage":

                draggedItem = self.storage["tab"][self.draggedItem["coor"][1]][
                    self.draggedItem["coor"][0]
                ]

            else:
                draggedItem = self.Hero.Inventory.storage["tab"][
                    self.draggedItem["coor"][1]
                ][self.draggedItem["coor"][0]]

            # Make the effect of "selected item"
            dragSurf = pygame.transform.scale(
                draggedItem.icon,
                (
                    int(draggedItem.rect.width * 1.25),
                    int(draggedItem.rect.height * 1.25),
                ),
            )

            dragRect = dragSurf.get_rect(center=pygame.mouse.get_pos())
            self.Game.screen.blit(dragSurf, dragRect)

    def show(self):

        if not self.open:
            self.transition(
                "open",
                textureConf.WORLD_ELEMENTS["GameObject"]["Chest"]["CHEST_ANIM_OPEN"],
                textureConf.WORLD_ELEMENTS["GameObject"]["Chest"]["transitionTime"],
            )

        while self.open:

            self.HUD = self.HUD_blank.copy()

            for event in pygame.event.get():

                self.checkActions(event)

                if (
                    event.type == pygame.KEYDOWN
                    and event.key
                    == self.Game.KeyBindings["Interact with an element"]["value"]
                ):
                    self.transition(
                        "close",
                        textureConf.WORLD_ELEMENTS["GameObject"]["Chest"][
                            "CHEST_ANIM_CLOSE"
                        ],
                        textureConf.WORLD_ELEMENTS["GameObject"]["Chest"][
                            "transitionTime"
                        ],
                    )

            if self.open:

                self.Game.screen.blit(self.bg, (0, 0))
                self._showItems()
                self.Game.screen.blit(self.HUD, self.rect)
                self._showDraggedItem()

                # -------------- BLITING CHEST CONTENT --------------- #

                self.Game.show()