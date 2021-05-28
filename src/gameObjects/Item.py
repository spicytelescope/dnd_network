from pygame.constants import SRCALPHA
from config.UIConf import BUTTON_FONT_SIZE
import pygame
import random
from config.mapConf import *
from config.itemConf import *
from config.HUDConf import *
import math
from UI.UI_utils_text import Dialog, ScrollText
import time
import uuid
from config.playerConf import ITEM_PICK_UP_RANGE

class Item:
    """Class representing an item.
    An item has at least an icon, and some properties.
    It may have an effect, given the type of the item, and may be stackable or not.

    The properties are represented by an argument acting as a list, containing the following attributes :

    - ID
    - ID Slot
    - Name
    - Rarety (which manifests as a color)
    - Stats : ATK, DEF, etc (which manifests as a dict)
    - Item's Description
    - Durability
    - ID Type

    """

    def __init__(
        self,
        iconPath,
        properties,
        metaType,
        classRestriction,
        defaultGoldValue,
        effect=None,
        stackable=False,
    ) -> None:

        self._stateSaved = False
        self.stackable = stackable

        # --------- TEXTURES ------------ #
        self.centerCoor = None
        self.iconPath = iconPath

        self.icon = None
        self.rect = None
        self.surfRect = None
        self.centerCoor = None
        self.initLootPos = None

        # Drop bliting

        self.parentSurface = None
        self.dropRect = None
        self.surf = None
        self.lastRendered = time.time()
        self.itemOffsetPos = []
        self.animIndex = 0

        rangeCoor = [elt for elt in range(0, ITEM_ANIM_OFFSET, 2)]
        self.itemOffsetPos += rangeCoor
        self.itemOffsetPos += rangeCoor[::-1]
        self.itemOffsetPos = [
            self.itemOffsetPos[i]
            for i in range(len(self.itemOffsetPos))
            if i != len(self.itemOffsetPos) - 1
            and self.itemOffsetPos[i] != self.itemOffsetPos[i + 1]
        ]
        self.deltaAnim = ITEM_ANIM_TIME / len(self.itemOffsetPos)

        # --------- STATS ------------ #

        self.descSurfDefaultPointPos = (
            int(INVENTORY_SURF_RATIO * 512 * 1) // 2,
            188 + 17 + 45,
        )

        self.property = {
            "UId": uuid.uuid1(),  # Proper id related to the player, serves on network purposes
            "Id": properties[0],  # Object id
            "slotId": properties[1],
            "name": properties[2],
            "rarety": properties[3],
            "stats": properties[4],
            "desc": {"text": properties[5], "surf": None, "descText": None},
            "durability": {
                "currentDurability": properties[6],
                "maxDurability": properties[6],
            },
            "typeId": properties[7],
            "classRestriction": classRestriction,
            "metaType": metaType,
            "sellValue": {
                "defaultGoldValue": defaultGoldValue,
                "currentSellValue": defaultGoldValue,
            },
        }

        self.lastTimeRecovered = None

    def setCoor(self, centerCoor):

        self.centerCoor = centerCoor
        self.rect = self.icon.get_rect(
            center=self.centerCoor
        )  # The topleft is not set properly yet

    def loadSurfDesc(self, centerCoor=[]):

        if centerCoor == []:
            centerCoor = self.descSurfDefaultPointPos

        self.property["desc"]["surf"] = pygame.Surface(
            ITEM_DESC_SURF_DIM, pygame.SRCALPHA
        )
        self.property["desc"]["rect"] = self.property["desc"]["surf"].get_rect(
            center=centerCoor
        )

        self.property["desc"]["surf"].fill((0, 0, 0, 0))
        self.property["desc"]["descText"] = ScrollText(
            self.property["desc"]["surf"],
            self.property["desc"]["text"],
            2,
            (0, 0, 0),
            italic=True,
            bold=True,
            size=BUTTON_FONT_SIZE,
        )

    def loadIcon(self):

        logger.info(f"LOADING {self.iconPath}")
        self.icon = pygame.transform.scale(
            pygame.image.load(self.iconPath), (ITEM_ICON_DIM[0], ITEM_ICON_DIM[1])
        )
        self.rect = self.icon.get_rect()
        self.dropRect = self.icon.get_rect()
        self.surfRect = pygame.transform.scale(
            self.icon, (int(self.rect.width * 0.75), int(self.rect.height * 0.75))
        ).get_rect()

        self.surf = pygame.Surface(
            self.surfRect.size,
            SRCALPHA,
        )
        self.surfRect.height += ITEM_ANIM_OFFSET

    def setGoldValue(self, HeroCurrentLvl):
        """
        Set the stat of the item accordingly to the current level of the Hero and the rarety of the item
        """
        self.property["sellValue"]["currentSellValue"] = (
            math.sqrt(HeroCurrentLvl)
            * RARETY_TYPES[self.property["rarety"]["itemWorthMultiplier"]]
            * self.property["sellValue"]["defaultGoldValue"]
        )

    def setStats(self, HeroCurrentLvl):
        """
        Set the stat of the item accordingly to the current level of the Hero
        """

        self.property["stats"] = [
            elt * math.sqrt(HeroCurrentLvl) for elt in self.property["stats"]
        ]

    def setDurability(self, newDurability):

        if not newDurability < 0:
            self.property["durability"]["currentDurability"] = newDurability
        else:
            self.property["durability"]["currentDurability"] = 0

    def setInitPos(self, pos):
        self.initLootPos = [
            coor + random.uniform(-ITEM_LOOT_RANGE, ITEM_LOOT_RANGE) for coor in pos
        ]
        self.setPos(self.initLootPos)
        self.lastTimeRecovered = time.time()

    def setPos(self, pos):
        """
        This method sets the position of the item in the map to be displayed
        """

        self.pos = list(pos)
        self.dropRect.topleft = self.pos

    def lootHandler(self, Hero, envGenerator, eltIndex):

        if (
            Hero.Game.resolution // 2 - ITEM_PICK_UP_RANGE
            <= self.pos[0]
            <= Hero.Game.resolution // 2 + ITEM_PICK_UP_RANGE
            and Hero.Game.resolution // 2 - ITEM_PICK_UP_RANGE
            <= self.pos[1]
            <= Hero.Game.resolution // 2 + ITEM_PICK_UP_RANGE
        ):
            self.lastTimeRecovered = time.time()

            if len(
                [
                    Hero.Inventory.storage["tab"][y][x]
                    for x in range(Hero.Inventory.storageLength[0])
                    for y in range(Hero.Inventory.storageLength[1])
                    if Hero.Inventory.storage["tab"][y][x] != None
                ]
            ) >= (Hero.Inventory.storageLength[0] * Hero.Inventory.storageLength[1]):
                Dialog(
                    "You don't have enough place in your Inventory to buy this item.",
                    (Hero.Game.resolution // 2, Hero.Game.resolution // 2),
                    Hero.Game.screen,
                    (255, 0, 0),
                    Hero.Game,
                    error=True,
                    charLimit=100,
                ).mainShow()

            else:
                envGenerator.items.pop(eltIndex)

                itemPlaced = False
                for j in range(INVENTORY_STORAGE_HEIGHT):
                    for i in range(INVENTORY_STORAGE_WIDTH):
                        if (
                            Hero.Inventory.storage["tab"][j][i] == None
                            and not itemPlaced
                        ):
                            Hero.Inventory.storage["tab"][j][i] = self
                            Hero.Inventory.storage["tab"][j][i].setCoor(
                                (
                                    Hero.Inventory.storage["initPoint"][0]
                                    + i * Hero.Inventory.storage["offset"][0],
                                    Hero.Inventory.storage["initPoint"][1]
                                    + j * Hero.Inventory.storage["offset"][1],
                                )
                            )
                            itemPlaced = True

    def show(self, parentSurface):

        self.surf = pygame.Surface(
            self.surfRect.size,
            SRCALPHA,
        )

        if (time.time() - self.lastRendered) > self.deltaAnim:
            self.lastRendered = time.time()
            self.surfRect.topleft = [
                self.surfRect.topleft[0],
                self.itemOffsetPos[self.animIndex],
            ]
            self.animIndex = (self.animIndex + 1) % len(self.itemOffsetPos)

        self.surf.blit(
            pygame.transform.scale(
                self.icon, (int(self.rect.width * 0.75), int(self.rect.height * 0.75))
            ),
            self.surfRect,
        )
        parentSurface.blit(self.surf, self.dropRect)

    # def __getstate__(self):

    #     if not self._stateSaved:
    #         self._stateSaved = True
    #         state = self.__dict__.copy()

    #         for attrName in ["icon", "surf"]:
    #             state.pop(attrName)

    #         for attrName in ["surf", "descText"]:

    #             state["property"]["desc"].pop(attrName)

    #         return state

    # def __setstate__(self, state):

    #     self.__dict__.update(state)
    #     self.loadIcon()
    #     self.loadSurfDesc()
