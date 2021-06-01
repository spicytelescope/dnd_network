from UI.UI_utils_text import Dialog
from config import playerConf
from gameObjects.Item import Item
from network.packet_types import TEMPLATE_INVENTORY

from pygame.constants import MOUSEBUTTONDOWN

from assets.animation import *
from gameController import *
from gameObjects.Item import Item
from config.eventConf import *
from config.menuConf import *
from config.UIConf import *
from config.playerConf import *
from config.textureConf import *
import config.HUDConf as HUDConf
from config.HUDConf import *
from config.itemConf import *
import config.itemConf as itemConf
from config.netConf import *
from copy import *
import json

from utils.Network_helpers import write_to_pipe


class Inventory:
    """An inventory is defined by 5 zones:
    - the storage zone : showing the unequiped items
    - the equipment zone : showing the equiped items
    - the item information zone : showing one item's information
    - the button zone : showing EQUIP and REMOVE button
    - the stat zone : showing the character stat's

    For the interaction with the player, the input comming from the mouse will be translated to the plan of the inventory surface, which means that the origin of the plan will be at the topLeft of the inventory's rect.
    """

    def __init__(self, gameController, Hero):

        self.Id = 4
        self.Game = gameController
        self.Hero = Hero

        # ------------- TEXTURES AND UI ---------- #

        self.inventorySurf = pygame.transform.scale(
            HUDConf.INVENTORY_SURF,
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
        self.surf = self.inventorySurf.copy()

        self.rect = self.surf.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.rect.topleft = (self.rect.topleft[0], -self.surf.get_height())

        # ----------------- ANIMATIONS -------------- #

        self.open = False
        self._show = False
        self.animations = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.time_delta = self.clock.tick(self.Game.refresh_rate)

        # ---------------- ITEMS ------------------- #

        self.storageLength = [INVENTORY_STORAGE_WIDTH, INVENTORY_STORAGE_HEIGHT]
        self.storage = {
            "tab": [
                [None for _ in range(INVENTORY_STORAGE_WIDTH)]
                for _ in range(INVENTORY_STORAGE_HEIGHT)
            ],
            # [coor*self.Game.resolutionFactor for coor in INVENTORY_STORAGE_INIT_POS],
            "initPoint": INVENTORY_STORAGE_INIT_POS,
            # [coor*self.Game.resolutionFactor for coor in INVENTORY_STORAGE_OFFSET]}
            "offset": INVENTORY_STORAGE_OFFSET,
        }
        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):
                if j * INVENTORY_STORAGE_WIDTH + i < playerConf.DEFAULT_NUM_ITEM:
                    itemId = playerConf.CLASSES[self.Hero.classId]["defaultItemKitId"][
                        j * INVENTORY_STORAGE_WIDTH + i
                    ]
                    self.storage["tab"][j][i] = deepcopy(itemConf.ITEM_DB[itemId])
                    self.storage["tab"][j][i].loadIcon()
                    self.storage["tab"][j][i].loadSurfDesc()
                    self.storage["tab"][j][i].setCoor(
                        (
                            self.storage["initPoint"][0]
                            + i * self.storage["offset"][0],
                            self.storage["initPoint"][1]
                            + j * self.storage["offset"][1],
                        )
                    )

        self.equipment = deepcopy(EQUIPMENT_TEMPLATE)
        self.twoHandedWeaponEquiped = False

        self.draggedItemCoor = None  # List
        self.equipmentDraggedCoor = None  # Int

        self.informationSpot = {
            "item": None,
            "blitPoint": [
                coor * self.Game.resolutionFactor for coor in ITEM_INFO_RAW_POS_ICON
            ],
            "coor": [],
        }

        self.itemHovered = False

    def setRectPos(self, centerCoor):
        """Method used to re center the bliting of the inventory when he's nested in another UI

        Args:
        ---
            centerCoor (tuple): coordonates meant to center the inventory UI
        """

        self.rect = self.surf.get_rect(center=centerCoor)
        self.rect.topleft = (self.rect.topleft[0], -self.surf.get_height())

    def openInventory(self):

        # self.background = self.Game.screen.copy()
        self.inventoryAni = Animation(y=0, duration=INVENTORY_ANIMATION_TIME)

        self.animations.add(self.inventoryAni)
        self.inventoryAni.start(self.rect)
        self.open = False
        self._show = True

    def close(self):

        self.closeInventoryAni = Animation(
            y=-self.surf.get_height(), duration=INVENTORY_ANIMATION_TIME
        )
        self.animations.add(self.closeInventoryAni)

        self.closeInventoryAni.start(self.rect)

        self.closeInventoryAni.schedule(self._close, "on finish")

    def _close(self):

        self.rect = self.surf.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.rect.topleft = (self.rect.topleft[0], -self.surf.get_height())

        self._show = False
        self.resetInventoryActions()
        # self.Game.backToGame()

        remove_animations_of(self.rect, self.animations)

    def checkActions(self, event, protected=False):
        """The protected arg is here to make sure that the inventory cannot be modified by other player in online games"""

        # ------------ ITEMS ACTION CHECKING --------- #
        self._checkItemSelection(event, protected)
        self._handleDragSpot(event)

        # ---------- EXIT HANDLING ----------- #

        if (
            event.type == pygame.KEYDOWN
            and event.key == self.Game.KeyBindings["Toggle Inventory"]["value"]
        ):
            self.close()

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # if self.Game.isOnline:
        #     self.Hero.transmitCharacInfos()
        #     self.transmitInvInfos()

    def checkSellItem(self, event, Seller):

        mousePosTranslated = [
            coor - self.rect.topleft[i]
            for coor, i in zip(pygame.mouse.get_pos(), [0, 1])
        ]
        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):

                if (
                    self.storage["tab"][j][i] != None
                    and self.storage["tab"][j][i].rect.collidepoint(mousePosTranslated)
                    and event.type == MOUSEBUTTONDOWN
                    and event.button == 3
                ):
                    Seller.sellItem()

    def checkTradeItem(self, event, TradeUI):

        mousePosTranslated = [
            coor - self.rect.topleft[i]
            for coor, i in zip(pygame.mouse.get_pos(), [0, 1])
        ]
        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):

                if (
                    self.storage["tab"][j][i] != None
                    and self.storage["tab"][j][i].rect.collidepoint(mousePosTranslated)
                    and event.type == MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    TradeUI.inventory_to_trade((i, j))

    def draw(self):

        if self.open:  # Act as a first time opening
            self.time_delta = self.clock.tick(self.Game.refresh_rate)
            self.animations.update(self.time_delta)
            self.openInventory()

        if self._show:

            self.time_delta = self.clock.tick(self.Game.refresh_rate)
            self.animations.update(self.time_delta)

            # ------------ RESOLUTION CHECKING ------------- #

            for indicator in self.Game.changesMadeChecker.items():
                # indicator[0] is the id and indicator[1] is the flag to mark that changes has been made
                if indicator[0] == self.Id and indicator[1]:
                    self.__init__(self.Game, self.Hero)
                    self.resetChanges()

            # ------------ BLITING TEXTURES AND UI STUFF ------ #

            self.surf = self.inventorySurf.copy()
            # self.Game.screen.blit(self.background, (0, 0))

            # -------------- BLITING ITEMS AND PLAYER'S STATS --- #

            self._showItems()
            self._showItemInfoSpot()
            self._showPlayerStats()
            # self._handleDoubleHandItems()

            self.Game.screen.blit(self.surf, self.rect)
            self._showDraggedItem()

    def nestedShow(self, pos):
        """
        Method used when the inventory is nested into another UI,
        using a non-blocking way
        """
        clock = pygame.time.Clock()
        time_delta = clock.tick(self.Game.refresh_rate)
        self.animations.update(time_delta)

        if not self.open:

            self.setRectPos(pos)
            self.rect.topleft = [self.rect.topleft[0], 0]
            self.open = True

        if self.open:

            time_delta = clock.tick(self.Game.refresh_rate)
            self.animations.update(time_delta)

            # ------------ RESOLUTION CHECKING ------------- #

            for indicator in self.Game.changesMadeChecker.items():
                # indicator[0] is the id and indicator[1] is the flag to mark that changes has been made
                if indicator[0] == self.Id and indicator[1]:
                    self.__init__(self.Game, self.Hero)
                    self.resetChanges()

            # ------------ BLITING TEXTURES AND UI STUFF ------ #
            self.surf = self.inventorySurf.copy()
            self.Game.screen.blit(self.surf, self.rect)

            # -------------- BLITING ITEMS AND PLAYER'S STATS --- #

            self._showItems()
            self._showItemInfoSpot()
            self._showPlayerStats()

            self.Game.screen.blit(self.surf, self.rect)
            self._showDraggedItem()

    def _showItems(self):
        """method bliting the item on the inventory surf"""
        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):
                if self.storage["tab"][j][i] != None:
                    self.surf.blit(
                        self.storage["tab"][j][i].icon, self.storage["tab"][j][i].rect
                    )

        for slot in self.equipment:
            if self.equipment[slot]["item"] != None:
                self.surf.blit(
                    self.equipment[slot]["item"].icon, self.equipment[slot]["slotRect"]
                )

    def _checkItemSelection(self, event, protected=False):
        """method handling the dragging of an item, the displaying of information if one item's icon is hovered,
        the protected arg is a flag to make sure that, when the game is online, no other entites can modify the items of the player"""

        mousePosTranslated = [
            coor - self.rect.topleft[i]
            for coor, i in zip(pygame.mouse.get_pos(), [0, 1])
        ]
        # ------------------ STORAGE HANDLING -------------- #
        self.itemHovered = False
        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):

                if self.storage["tab"][j][i] != None:

                    # Checking item selection
                    if self.storage["tab"][j][i].rect.collidepoint(mousePosTranslated):
                        # The case is an item, we handle swaping, draging and hovering
                        self.itemHovered = True

                        # Check if the item is clicked or not
                        if (
                            event.type == MOUSEBUTTONDOWN
                            and event.button == 1
                            and not protected
                        ):
                            if (
                                self.draggedItemCoor == None
                                and self.equipmentDraggedCoor == None
                            ):
                                self.draggedItemCoor = [i, j]
                            else:
                                if (
                                    self.draggedItemCoor != None
                                ):  # Means dragged item is from storage
                                    # If the item is dragged with himself, cancel
                                    if [i, j] == self.draggedItemCoor:
                                        self.draggedItemCoor = None
                                    # Swaps otherwise if the item is dragged and is from the storage
                                    else:

                                        # We need to switch the objects, but also the rect that goes with
                                        (
                                            self.storage["tab"][
                                                self.draggedItemCoor[1]
                                            ][self.draggedItemCoor[0]],
                                            self.storage["tab"][j][i],
                                        ) = (
                                            self.storage["tab"][j][i],
                                            self.storage["tab"][
                                                self.draggedItemCoor[1]
                                            ][self.draggedItemCoor[0]],
                                        )

                                        # Switching rect by updating coors
                                        draggedCoor = self.storage["tab"][
                                            self.draggedItemCoor[1]
                                        ][self.draggedItemCoor[0]].centerCoor

                                        self.storage["tab"][self.draggedItemCoor[1]][
                                            self.draggedItemCoor[0]
                                        ].setCoor(self.storage["tab"][j][i].centerCoor)
                                        self.storage["tab"][j][i].setCoor(draggedCoor)

                                        self.draggedItemCoor = None

                                else:  # dragged item from the equipment
                                    # checking the type for exchange
                                    if (
                                        self.equipment[self.equipmentDraggedCoor][
                                            "item"
                                        ].property["slotId"]
                                        == self.storage["tab"][j][i].property["slotId"]
                                        and CLASSES_NAMES[self.Hero.classId]
                                        in self.equipment[self.equipmentDraggedCoor][
                                            "item"
                                        ].property["classRestriction"]
                                    ):
                                        self.equipment[self.equipmentDraggedCoor][
                                            "item"
                                        ].setCoor(self.storage["tab"][j][i].centerCoor)
                                        # Switching items
                                        (
                                            self.storage["tab"][j][i],
                                            self.equipment[self.equipmentDraggedCoor][
                                                "item"
                                            ],
                                        ) = (
                                            self.equipment[self.equipmentDraggedCoor][
                                                "item"
                                            ],
                                            self.storage["tab"][j][i],
                                        )
                                        self.equipmentDraggedCoor = None
                                    else:
                                        continue  # skip and goes to the next case

                        # Handling the information spot
                        else:
                            self.informationSpot["item"] = self.storage["tab"][j][i]
                            self.informationSpot["coor"] = [i, j]

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
                        and not protected
                    ):
                        if self.draggedItemCoor != None:
                            self.storage["tab"][j][i] = self.storage["tab"][
                                self.draggedItemCoor[1]
                            ][self.draggedItemCoor[0]]
                            self.storage["tab"][self.draggedItemCoor[1]][
                                self.draggedItemCoor[0]
                            ] = None

                            self.storage["tab"][j][i].setCoor(
                                [
                                    self.storage["initPoint"][0]
                                    + i * self.storage["offset"][0],
                                    self.storage["initPoint"][1]
                                    + j * self.storage["offset"][1],
                                ]
                            )

                            self.draggedItemCoor = None
                        elif self.equipmentDraggedCoor != None:

                            self.storage["tab"][j][i] = self.equipment[
                                self.equipmentDraggedCoor
                            ]["item"]
                            self.equipment[self.equipmentDraggedCoor]["item"] = None

                            self.storage["tab"][j][i].setCoor(
                                [
                                    self.storage["initPoint"][0]
                                    + i * self.storage["offset"][0],
                                    self.storage["initPoint"][1]
                                    + j * self.storage["offset"][1],
                                ]
                            )
                            self.equipmentDraggedCoor = None

        # ------------------ EQUIPMENT HANDLING ---------------- #

        # the keys of self.equipment are the same as the slotId !
        for itemSlot in self.equipment:
            if self.equipment[itemSlot]["item"] != None:
                if self.equipment[itemSlot]["slotRect"].collidepoint(
                    mousePosTranslated
                ):
                    self.itemHovered = True

                    if (
                        event.type == MOUSEBUTTONDOWN
                        and event.button == 1
                        and not protected
                    ):
                        if (
                            self.draggedItemCoor == None
                            and self.equipmentDraggedCoor == None
                        ):
                            self.equipmentDraggedCoor = itemSlot
                        else:
                            if self.equipmentDraggedCoor != None:
                                if self.equipmentDraggedCoor == itemSlot:
                                    self.equipmentDraggedCoor = None
                                else:  # as we can't swap equipments as they are of a diffenrent type, we continue to the next iteration
                                    self.equipmentDraggedCoor = None
                                    continue

                            elif self.draggedItemCoor != None:

                                self.equipment[itemSlot]["item"].setCoor(
                                    self.storage["tab"][self.draggedItemCoor[1]][
                                        self.draggedItemCoor[0]
                                    ].centerCoor
                                )

                                # if (
                                #     self.equipment[itemSlot]["item"].property["typeId"]
                                #     in WEAPON_2_HAND_IDS
                                # ):
                                #     if itemSlot == 6:
                                #         self.equipment[4]["item"] = None
                                #     else:
                                #         self.equipment[6]["item"] = None

                                # Switching items
                                (
                                    self.storage["tab"][self.draggedItemCoor[1]][
                                        self.draggedItemCoor[0]
                                    ],
                                    self.equipment[itemSlot]["item"],
                                ) = (
                                    self.equipment[itemSlot]["item"],
                                    self.storage["tab"][self.draggedItemCoor[1]][
                                        self.draggedItemCoor[0]
                                    ],
                                )

                                # if (
                                #     self.equipment[itemSlot]["item"].property["typeId"]
                                #     in WEAPON_2_HAND_IDS
                                # ):
                                #     self.twoHandedWeaponEquiped = True
                                # else:
                                #     self.twoHandedWeaponEquiped = False

                                self.draggedItemCoor = None

                    else:  # Handling information spot
                        self.informationSpot["item"] = self.equipment[itemSlot]["item"]

            else:
                if (
                    event.type == MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.equipment[itemSlot]["slotRect"].collidepoint(
                        mousePosTranslated
                    )
                    and not protected
                ):
                    if self.equipmentDraggedCoor != None:
                        self.equipmentDraggedCoor = None  # as there is no swaps between 2 items in the equipment zone
                        continue

                    if self.draggedItemCoor != None:
                        logger.debug(
                            f"Dragging in coming from storage to equipment, {self.storage['tab'][self.draggedItemCoor[1]][self.draggedItemCoor[0]].property['slotId']} -> {itemSlot}"
                        )

                        if (
                            CLASSES_NAMES[self.Hero.classId]
                            in self.storage["tab"][self.draggedItemCoor[1]][
                                self.draggedItemCoor[0]
                            ].property["classRestriction"]
                            and itemSlot
                            == self.storage["tab"][self.draggedItemCoor[1]][
                                self.draggedItemCoor[0]
                            ].property["slotId"]
                        ):

                            self.equipment[itemSlot]["item"] = self.storage["tab"][
                                self.draggedItemCoor[1]
                            ][self.draggedItemCoor[0]]
                            self.storage["tab"][self.draggedItemCoor[1]][
                                self.draggedItemCoor[0]
                            ] = None

                            # if (
                            #     self.equipment[itemSlot]["item"].property["typeId"]
                            #     in WEAPON_2_HAND_IDS
                            # ):
                            #     self.twoHandedWeaponEquiped = True
                            # else:
                            #     self.twoHandedWeaponEquiped = False

                        else:
                            continue

                        self.draggedItemCoor = None

        if not self.itemHovered:
            self.informationSpot["item"] = None
            self.informationSpot["coor"] = []

        # if self.Game.debug_mode: logger.debug(
        #     f" Storage state : {[[self.storage['tab'][y][x].property['name'] if self.storage['tab'][y][x] != None else 'EMPTY' for x in range(INVENTORY_STORAGE_WIDTH)] for y in range(INVENTORY_STORAGE_HEIGHT)]}"
        # )

    # def _handleDoubleHandItems(self):
    #     """If a item that goes in double hands is equiped, the right hand take the icon of the left one"""

    #     self.equipment[6]["item"] = self.equipment[4]["item"]

    def _handleDragSpot(self, event):
        """Method showing the dragged item onto the mouse and
        putting it somewhere given actions describes as follows.

        If the player left click while dragging an item on :
        - an other item icon in the storage : swap with it (handle by _checkItemSelection method)
        - an other item icon in the equipment : swap if it's the same object type
        - somewhere outside of the surf : cancel the dragging and put the item outside of the inventory"""

        if self.draggedItemCoor != None or self.equipmentDraggedCoor != None:

            if (
                event.type == MOUSEBUTTONDOWN
                and event.button == 1
                and not self.rect.collidepoint(pygame.mouse.get_pos())
            ):

                if self.equipmentDraggedCoor != None:
                    self.equipment[self.equipmentDraggedCoor].setInitPos(
                        [self.Game.resolution // 2, self.Game.resolution // 2],
                    )
                    if self.Hero.currentPlace == "openWorld":

                        self.Hero.Map.envGenerator.items.append(
                            copy(self.equipment[self.equipmentDraggedCoor])
                        )
                    elif self.Hero.currentPlace == "building":
                        self.Hero.currentBuilding.items.append(
                            self.equipment[self.equipmentDraggedCoor]
                        )

                    self.equipment[self.equipmentDraggedCoor] = None

                elif self.draggedItemCoor != None:
                    self.storage["tab"][self.draggedItemCoor[1]][
                        self.draggedItemCoor[0]
                    ].setInitPos(
                        [self.Game.resolution // 2, self.Game.resolution // 2],
                    )

                    if self.Hero.currentPlace == "openWorld":
                        self.Hero.Map.envGenerator.items.append(
                            copy(
                                self.storage["tab"][self.draggedItemCoor[1]][
                                    self.draggedItemCoor[0]
                                ]
                            )
                        )

                    elif self.Hero.currentPlace == "building":
                        self.Hero.currentBuilding.items.append(
                            copy(
                                self.storage["tab"][self.draggedItemCoor[1]][
                                    self.draggedItemCoor[0]
                                ]
                            )
                        )
                    self.storage["tab"][self.draggedItemCoor[1]][
                        self.draggedItemCoor[0]
                    ] = None

                self.draggedItemCoor = None
                self.equipmentDraggedCoor = None

    def _showDraggedItem(self):
        if self.draggedItemCoor != None or self.equipmentDraggedCoor != None:

            draggedItem = (
                self.storage["tab"][self.draggedItemCoor[1]][self.draggedItemCoor[0]]
                if self.draggedItemCoor != None
                else self.equipment[self.equipmentDraggedCoor]["item"]
            )
            # Make the effet of "selected item"
            dragSurf = pygame.transform.scale(
                draggedItem.icon,
                (
                    int(draggedItem.rect.width * 1.25),
                    int(draggedItem.rect.height * 1.25),
                ),
            )

            dragRect = dragSurf.get_rect(center=pygame.mouse.get_pos())
            self.Game.screen.blit(dragSurf, dragRect)

    def _showItemInfoSpot(self):

        if self.informationSpot["item"] != None:

            def formatPropertyText(propertyName, value):

                fValue = value
                fColor = (255, 255, 255)

                if propertyName == "slotId":
                    if fValue == -1:
                        fValue = ""
                    else:
                        fValue = ITEM_SLOT_TYPES[value]
                elif propertyName == "name":
                    fColor = RARETY_TYPES[
                        self.informationSpot["item"].property["rarety"]
                    ]["color"]
                elif propertyName == "typeId":
                    if fValue == -1:
                        fValue = ""
                    else:
                        fValue = ITEM_TYPES[value]
                elif propertyName == "durability":
                    fValue = f"{value['currentDurability']}/{value['maxDurability']}"
                elif propertyName == "sellValue":
                    fValue = value["currentSellValue"]
                elif propertyName == "stats":
                    if self.informationSpot["item"].property["metaType"] == "ARMOR":
                        fValue = f"DEF : {value}"
                    elif self.informationSpot["item"].property["metaType"] == "WEAPON":
                        fValue = f"ATK : {value}"
                    else:
                        fValue = ""
                elif propertyName == "classRestriction":
                    fValue = f"Only for {' , '.join(value)}"
                    fColor = (
                        (0, 255, 0)
                        if CLASSES_NAMES[self.Hero.classId] in value
                        else (255, 0, 0)
                    )  # Green color if the class restriction is respected, red otherwise

                return (str(fValue), True, fColor)

            # INFO BLITING
            fonts = [
                pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE)
                if propertyName not in ["classRestriction", "slotId", "typeId"]
                else pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE)
                for propertyName in ITEM_INFO_POS.keys()
            ]

            propertiesFont = [
                fonts[i].render(
                    *formatPropertyText(
                        propertyName,
                        self.informationSpot["item"].property[propertyName],
                    )
                )
                for i, propertyName in enumerate(ITEM_INFO_POS.keys())
            ]

            def formatPropertyPos(propertyFontIndex, propertyName):

                propertyFont = propertiesFont[propertyFontIndex]
                if ITEM_INFO_POS[propertyName][0] == "customWidth":
                    return propertyFont.get_rect(
                        center=(self.rect.width // 2, ITEM_INFO_POS[propertyName][1])
                    )
                else:
                    return propertyFont.get_rect(center=ITEM_INFO_POS[propertyName])

            propertiesFontRect = [
                formatPropertyPos(*infoPos)
                for infoPos in enumerate(ITEM_INFO_POS.keys())
            ]

            # ICON BLITING
            infoIcon = pygame.transform.scale(
                self.informationSpot["item"].icon, tuple(ITEM_INFO_ICON_DIM)
            )
            infoRect = infoIcon.get_rect(
                center=tuple(self.informationSpot["blitPoint"])
            )

            # DESC BLITING

            self.informationSpot["item"].property["desc"]["descText"].update()
            self.surf.blit(
                self.informationSpot["item"].property["desc"]["surf"],
                self.informationSpot["item"].property["desc"]["rect"],
            )

            # GENERAL BLITING
            for propertySurf, propertyRect in zip(propertiesFont, propertiesFontRect):
                self.surf.blit(propertySurf, propertyRect)

            for icon in HUDConf.ITEM_INFO_ICONS.values():
                self.surf.blit(icon["surf"], icon["rect"])

            self.surf.blit(infoIcon, infoRect)

    def _showPlayerStats(self):

        for statName in self.Hero.stats:

            fontText = str(self.Hero.stats[statName])

            if statName == "HP":
                fontText = f"{self.Hero.stats[statName]}/{self.Hero.stats['HP_max']}"
            elif statName == "Mana":
                fontText = f"{self.Hero.stats[statName]}/{self.Hero.stats['Mana_max']}"
            elif statName in ["DEF", "ATK"]:
                DEFTotal = self.Hero.stats[statName]
                ATKTotal = self.Hero.stats[statName]
                for itemEquipId, item in enumerate(self.equipment.values()):
                    if item["item"] != None:
                        if item["item"].property["metaType"] == "ARMOR":
                            DEFTotal += item["item"].property["stats"]
                        elif item["item"].property["metaType"] == "WEAPON":
                            # if (
                            #     self.twoHandedWeaponEquiped and not itemEquipId == 6
                            # ):  # Not counting the right hand as this is a 2hand weapon
                            ATKTotal += item["item"].property["stats"]

                fontText = str(DEFTotal) if statName == "DEF" else str(ATKTotal)
            elif statName in ["HP_max", "Mana_max"]:
                continue

            statFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
                fontText, True, (255, 255, 255)
            )
            statRect = statFont.get_rect(center=STAT_BLIT_POINTS[statName])
            self.surf.blit(statFont, statRect)

    def resetInventoryActions(self):

        self.draggedItemCoor = None

        self.informationSpot["item"] = None
        self.informationSpot["coor"] = []

    # -------------------------- NETWORK ----------------------- #

    def updateInventory(self, storage_item_ids={}, eq_item_ids={}):
        """Update the inventory given 3 actions :
        + INIT : intialise the inventory with the two lists of ids
        + ADD : add some items copied from the given ids, the eq_item_ids is made with the folliwing pattern : key = eq_slot_id and value = item's db ID
        + REMOVE : remove some items copied identified by the given ids, note : the eq_item_ids's values will be useless as only the keys will be used to remove the adequate items

        Args:
            action_type (str): [description]
            eq_item_ids (dict, optional): [description]. Defaults to {}.
            storage_item_ids (list, optional): [description]. Defaults to [].
        """
        # Storage part, simple version not optimised taking into account positions ! It means that at each change on one client's inventory, all the inventory is reload e.g the textures of each items

        # Creating a dict containing the current player infos , matching the scheme on the datas.json file
        p_items = {
            str(self.storage["tab"][j][i].property["Id"]): [i, j]
            for j in range(INVENTORY_STORAGE_HEIGHT)
            for i in range(INVENTORY_STORAGE_WIDTH)
            if self.storage["tab"][j][i] != None
        }

        if p_items != storage_item_ids:
            for j in range(INVENTORY_STORAGE_HEIGHT):
                for i in range(INVENTORY_STORAGE_WIDTH):
                    self.storage["tab"][j][i] = None

            for item_id, (i, j) in storage_item_ids.items():
                self.storage["tab"][j][i] = deepcopy(itemConf.ITEM_DB[int(item_id)])
                self.storage["tab"][j][i].loadIcon()
                self.storage["tab"][j][i].loadSurfDesc()
                self.storage["tab"][j][i].setCoor(
                    (
                        self.storage["initPoint"][0] + i * self.storage["offset"][0],
                        self.storage["initPoint"][1] + j * self.storage["offset"][1],
                    )
                )

        if list(eq_item_ids.values()) != [
            slot_item["item"].property["Id"]
            for slot_item in self.equipment.values()
            if slot_item["item"] != None
        ]:
            for slot_id, item_id in eq_item_ids.items():
                self.equipment[int(slot_id)]["item"] = deepcopy(
                    itemConf.ITEM_DB[item_id]
                )
                self.equipment[int(slot_id)]["item"].loadIcon()
                self.equipment[int(slot_id)]["item"].loadSurfDesc()

    def transmitInvInfos(self):
        inv_packet = deepcopy(TEMPLATE_INVENTORY)
        inv_packet["sender_id"] = self.Hero.networkId
        inv_packet["storage"] = {
            str(self.storage["tab"][j][i].property["Id"]): (i, j)
            for j in range(INVENTORY_STORAGE_HEIGHT)
            for i in range(INVENTORY_STORAGE_WIDTH)
            if self.storage["tab"][j][i] != None
        }
        inv_packet["equipment"] = {
            str(slot): int(slot_item["item"].property["Id"])
            for slot, slot_item in self.equipment.items()
            if slot_item["item"] != None
        }
        write_to_pipe(IPC_FIFO_OUTPUT_CREA if self.Game.NetworkController.isSessionCreator else IPC_FIFO_OUTPUT_JOINER, inv_packet)

    # def __getstate__(self):

    #     state = self.__dict__.copy()

    #     for attrName in ["inventorySurf", "surf"]:
    #         state.pop(attrName)

    # def __setstate__(self, state):

    #     self.__dict__.update(state)
    #     self.__init__(self.Game, self.Hero)
