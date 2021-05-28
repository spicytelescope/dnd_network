from UI.UI_utils_text import Dialog
import copy
from threading import Thread

from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN

import config.itemConf as itemConf
import config.NPCConf as NPCConf
import pygame
from config.HUDConf import *
from config.itemConf import *
from config.playerConf import *
from config.UIConf import *
from gameObjects.Chest import Chest
from HUD.Inventory import Inventory


class SellerInterface(Chest):

    """
    Interface made of the storage of a chest and
    the information spot of an item
    """

    def __init__(self, gameController, Hero, seller, defaultContent=None) -> None:

        self.Game = gameController
        self.Hero = Hero
        self.open = False
        self.firstOpen = True
        self.defaultContent = defaultContent
        self.seller = seller
        super().__init__(gameController, self.Hero)

        # TEXTURES
        self.blank_surf = NPCConf.UI_SELLER_SURF
        self.surf = self.blank_surf.copy()
        self.rect = self.surf.get_rect(center=(self.Game.resolution // 6, 0))
        self.rect.topleft = [self.rect.topleft[0], 0]

        # -------------------- ITEMS -------------------- #

        self.defaultContent = defaultContent
        self.storageLength = [
            NPCConf.SELLER_STORAGE_WIDTH,
            NPCConf.SELLER_STORAGE_HEIGHT,
        ]

        self.storage = {
            "tab": [
                [None for _ in range(self.storageLength[0])]
                for _ in range(self.storageLength[1])
            ],
            # [coor*self.Game.resolutionFactor for coor in INVENTORY_STORAGE_INIT_POS],
            "initPoint": NPCConf.SELLER_STORAGE_INIT_POS,
            # [coor*self.Game.resolutionFactor for coor in INVENTORY_STORAGE_OFFSET]}
            "offset": NPCConf.SELLER_STORAGE_OFFSET,
        }

        self.numRestriction = [DEFAULT_NUM_CHEST_MIN, DEFAULT_NUM_CHEST_MAX]

        self.itemHovered = False
        self.informationSpot = {
            "item": None,
            "blitPoint": [
                coor * self.Game.resolutionFactor
                for coor in NPCConf.SELLER_INFO_RAW_POS_ICON
            ],
            "coor": [],
        }
        self.bg = None

    def initSeller(self) -> None:
        """
        Take the item of the defaultContent of the chest and place them at random position in the storage.
        """
        self.bg = self.Game.screen.copy()

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
                item.setGoldValue(self.Hero._Level)
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
                self.storage["tab"][j][i].loadSurfDesc(
                    (
                        self.rect.width // 2,
                        200 + 17 + 35,
                    )
                )
                self.storage["tab"][j][i].loadIcon()
                self.storage["tab"][j][i].setCoor(
                    (
                        self.storage["initPoint"][0] + i * self.storage["offset"][0],
                        self.storage["initPoint"][1] + j * self.storage["offset"][1],
                    )
                )

    def _showItems(self):
        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):
                if self.storage["tab"][j][i] != None:
                    self.surf.blit(
                        self.storage["tab"][j][i].icon,
                        self.storage["tab"][j][i].rect,
                    )

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
                if propertyName != "classRestriction"
                else pygame.font.Font(DUNGEON_FONT, int(BUTTON_FONT_SIZE * 0.75))
                for propertyName in NPCConf.SELLER_ITEM_INFO_POS.keys()
            ]

            propertiesFont = [
                fonts[i].render(
                    *formatPropertyText(
                        propertyName,
                        self.informationSpot["item"].property[propertyName],
                    )
                )
                for i, propertyName in enumerate(NPCConf.SELLER_ITEM_INFO_POS.keys())
            ]

            def formatPropertyPos(propertyFontIndex, propertyName):

                propertyFont = propertiesFont[propertyFontIndex]
                if propertyName == "slotId":
                    return propertyFont.get_rect(
                        topleft=NPCConf.SELLER_ITEM_INFO_POS[propertyName]
                    )
                elif propertyName == "typeId":
                    return propertyFont.get_rect(
                        topright=NPCConf.SELLER_ITEM_INFO_POS[propertyName]
                    )
                elif NPCConf.SELLER_ITEM_INFO_POS[propertyName][0] == "customWidth":
                    return propertyFont.get_rect(
                        center=(
                            self.rect.width // 2,
                            NPCConf.SELLER_ITEM_INFO_POS[propertyName][1],
                        )
                    )
                else:
                    return propertyFont.get_rect(
                        center=NPCConf.SELLER_ITEM_INFO_POS[propertyName]
                    )

            propertiesFontRect = [
                formatPropertyPos(*infoPos)
                for infoPos in enumerate(NPCConf.SELLER_ITEM_INFO_POS.keys())
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

            for icon in NPCConf.UI_SELLER_INFO_ICONS.values():
                self.surf.blit(icon["surf"], icon["rect"])

            self.surf.blit(infoIcon, infoRect)

    def _checkItemSelection(self, event):

        mousePosTranslated = [
            coor - rectTopLeftCoor
            for coor, rectTopLeftCoor in zip(pygame.mouse.get_pos(), self.rect.topleft)
        ]

        self.itemHovered = False
        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):

                # Checking item selection
                if self.storage["tab"][j][i] != None and self.storage["tab"][j][
                    i
                ].rect.collidepoint(mousePosTranslated):
                    # The case is an item, we handle swaping, draging and hovering
                    self.itemHovered = True
                    self.informationSpot["item"] = self.storage["tab"][j][i]
                    self.informationSpot["coor"] = [i, j]

                    if event.type == MOUSEBUTTONDOWN and event.button == 3:
                        self.buyItem()

        if not self.itemHovered:
            self.informationSpot["item"] = None
            self.informationSpot["coor"] = []

    def exit(self):

        self.Hero.Inventory._close()
        self.open = False

    def show(self):

        self.open = True
        if self.firstOpen:
            self.initSeller()
            self.firstOpen = False

        while self.open:
            self.Game.screen.blit(self.bg, (0, 0))

            # HANDLING SELLER PROPER UI
            self.surf = self.blank_surf.copy()

            for event in pygame.event.get():

                self._checkItemSelection(event)  # checking for seller ui

                # --------------- INVENTORY HANDLING ------------- #

                self.Hero.Inventory._checkItemSelection(event)
                self.Hero.Inventory._handleDragSpot(event)
                self.Hero.Inventory.checkSellItem(event, self)

                # ---------- EXIT HANDLING ----------- #

                if (
                    event.type == pygame.KEYDOWN
                    and event.key
                    == self.Game.KeyBindings["Interact with an element"]["value"]
                ):
                    self.exit()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            if self.open:
                self._showItems()
                self._showItemInfoSpot()

                # Updating gold amount
                self.surf.blit(
                    pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
                        f"{self.seller.goldAmount}", True, (0, 0, 0)
                    ),
                    NPCConf.GOLD_AMOUNT_BLIT_POS,
                )

                self.Game.screen.blit(self.surf, self.rect)

                # HANDLING INVENTORY
                self.Hero.Inventory.nestedShow(
                    [int(self.Game.resolution * 0.65), self.Game.resolution // 2]
                )
                self.Game.show()

    def buyItem(self):

        if (
            self.Hero.stats["Money"]
            - self.informationSpot["item"].property["sellValue"]["currentSellValue"]
        ) < 0:

            Dialog(
                "You've got not enough money to buy this item.",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                (255, 0, 0),
                self.Game,
                error=True,
                charLimit=100,
            ).mainShow()

        elif len(
            [
                self.Hero.Inventory.storage["tab"][y][x]
                for x in range(self.Hero.Inventory.storageLength[0])
                for y in range(self.Hero.Inventory.storageLength[1])
                if self.Hero.Inventory.storage["tab"][y][x] != None
            ]
        ) >= (
            self.Hero.Inventory.storageLength[0] * self.Hero.Inventory.storageLength[1]
        ):
            Dialog(
                "You don't have enough place in your Inventory to buy this item.",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                (255, 0, 0),
                self.Game,
                error=True,
                charLimit=100,
            ).mainShow()

        else:
            self.Hero.stats["Money"] -= self.informationSpot["item"].property[
                "sellValue"
            ]["currentSellValue"]
            self.seller.goldAmount += self.informationSpot["item"].property[
                "sellValue"
            ]["currentSellValue"]

            for j in range(INVENTORY_STORAGE_HEIGHT):
                for i in range(INVENTORY_STORAGE_WIDTH):
                    if (
                        self.Hero.Inventory.storage["tab"][j][i] == None
                        and self.informationSpot["item"] != None
                    ):
                        self.Hero.Inventory.storage["tab"][j][i] = self.informationSpot[
                            "item"
                        ]
                        self.Hero.Inventory.storage["tab"][j][i].setCoor(
                            (
                                self.Hero.Inventory.storage["initPoint"][0]
                                + i * self.Hero.Inventory.storage["offset"][0],
                                self.Hero.Inventory.storage["initPoint"][1]
                                + j * self.Hero.Inventory.storage["offset"][1],
                            )
                        )
                        self.storage["tab"][self.informationSpot["coor"][1]][
                            self.informationSpot["coor"][0]
                        ] = None
                        self.informationSpot["item"] = None

            self.informationSpot["Coor"] = []

    def sellItem(self):

        if (
            self.seller.goldAmount
            - self.Hero.Inventory.informationSpot["item"].property["sellValue"][
                "currentSellValue"
            ]
        ) < 0:
            Dialog(
                "The seller got not enough money to buy you this item.",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                (255, 0, 0),
                self.Game,
                error=True,
                charLimit=100,
            ).mainShow()

        elif len(
            [
                self.storage["tab"][y][x]
                for x in range(self.storageLength[0])
                for y in range(self.storageLength[1])
                if self.storage["tab"][y][x] != None
            ]
        ) >= (self.storageLength[0] * self.storageLength[1]):
            Dialog(
                "The seller got no more place on his bag to buy you this item.",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                (255, 0, 0),
                self.Game,
                error=True,
                charLimit=100,
            ).mainShow()

        else:
            self.Hero.stats["Money"] += self.Hero.Inventory.informationSpot[
                "item"
            ].property["sellValue"]["currentSellValue"]
            self.seller.goldAmount -= self.Hero.Inventory.informationSpot[
                "item"
            ].property["sellValue"]["currentSellValue"]

            for j in range(NPCConf.SELLER_STORAGE_HEIGHT):
                for i in range(NPCConf.SELLER_STORAGE_WIDTH):
                    if (
                        self.storage["tab"][j][i] == None
                        and self.Hero.Inventory.informationSpot["item"] != None
                    ):
                        self.storage["tab"][j][i] = self.Hero.Inventory.informationSpot[
                            "item"
                        ]
                        self.storage["tab"][j][i].setCoor(
                            (
                                self.storage["initPoint"][0]
                                + i * self.storage["offset"][0],
                                self.storage["initPoint"][1]
                                + j * self.storage["offset"][1],
                            )
                        )

                        self.Hero.Inventory.storage["tab"][
                            self.Hero.Inventory.informationSpot["coor"][1]
                        ][self.Hero.Inventory.informationSpot["coor"][0]] = None
                        self.Hero.Inventory.informationSpot["item"] = None

            self.Hero.Inventory.informationSpot["Coor"] = []
