from pandas.core.indexes import base
from UI.UI_utils_text import Dialog, SelectPopUp
import copy
import random
from threading import Thread

from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN
from config import UIConf
from config import HUDConf

import config.itemConf as itemConf
import config.NPCConf as NPCConf
import pygame, time
from config.HUDConf import *
from config.itemConf import *
from config.playerConf import *
from config.UIConf import *


class TradeUI:

    """
    Interface made of the storage of a chest and
    the information spot of an item
    """

    def __init__(self, gameController, Hero, Target, NetworkController) -> None:

        self.Game = gameController
        self.Hero = Hero
        self.target = Target
        self._show = False
        self.NetworkController = NetworkController

        # TEXTURES
        self.blank_surf = UIConf.TRADING_SURF
        self.surf = self.blank_surf.copy()
        self.rect = self.surf.get_rect(
            center=(self.Game.resolution // 2, int(self.Game.resolution * 0.75))
        )

        # ------------- BUTTONS  ------------------- #

        self.lockBtn = TRADE_LOCK_BTN
        self.lockBtnRect = self.lockBtn.get_rect(center=LOCK_BUTTON_POS)
        self.acceptPopUp = SelectPopUp(
            {"Yes": self.sendTradeAccept, "No": self.sendTradeRefuse},
            self.Game.screen,
            self.Game,
            (self.Game.resolution // 2, self.Game.resolution // 2),
            f"{self.target.name} locked the trade, do you accept it ?",
        )
        # -------------------- ITEMS -------------------- #

        self.storageLength = [
            6,
            1,
        ]

        self.player_storage = {
            "tab": [
                [None for _ in range(self.storageLength[0])]
                for _ in range(self.storageLength[1])
            ],
            "offset": NPCConf.SELLER_STORAGE_OFFSET,
        }

        self.target_storage = {
            "tab": [
                [None for _ in range(self.storageLength[0])]
                for _ in range(self.storageLength[1])
            ],
            "offset": NPCConf.SELLER_STORAGE_OFFSET,
        }

        self.numRestriction = [DEFAULT_NUM_CHEST_MIN, DEFAULT_NUM_CHEST_MAX]

        # ----------------- NETWORK ---------------- #

        self.confirmRecvFlag = False
        self.targetAcceptedTrade = "UNDEFINED"
        self.waitingFlag = False  #  UI flag to display the waiting for the target to accept/refuse the trade
        self.waitChrono = None
        self.acceptTrade = False

    def _showItems(self):
        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):
                if self.player_storage["tab"][j][i] != None:
                    self.surf.blit(
                        self.player_storage["tab"][j][i].icon,
                        self.player_storage["tab"][j][i].rect,
                    )
                if self.target_storage["tab"][j][i] != None:
                    self.surf.blit(
                        self.target_storage["tab"][j][i].icon,
                        self.target_storage["tab"][j][i].rect,
                    )

    def checkActions(self, event):

        self._checkItemSelection(event)  # checking for trader ui

        # --------------- INVENTORY HANDLING ------------- #

        self.Hero.Inventory._checkItemSelection(event, protected=True)
        self.Hero.Inventory.checkTradeItem(event, self)

        # --------------- CONFIRM HANDLING ------------ #

        if (
            self.lockBtnRect.collidepoint(
                [
                    coor1 - coor2
                    for coor1, coor2 in zip(pygame.mouse.get_pos(), self.rect.topleft)
                ]
            )
            and event.type == MOUSEBUTTONDOWN
        ):
            if not self.confirmRecvFlag:
                self.NetworkController.sendTradeConfirmation()
                self.waitingFlag = True
                self.waitChrono = time.time()

        # ---------- EXIT HANDLING ----------- #

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def draw(self):

        if self._show:
            # HANDLING SELLER PROPER UI
            self.surf = self.blank_surf.copy()

            # NAME BLITING

            baseFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE)
            target_font = baseFont.render(self.target.name, True, (0, 0, 0))
            player_font = baseFont.render(self.Hero.name, True, (0, 0, 0))
            self.surf.blit(target_font, target_font.get_rect(center=NAME_SLOT_1))
            self.surf.blit(player_font, player_font.get_rect(center=NAME_SLOT_2))

            # ---------------- BUTTON HANDLING -------------- #
            if self.lockBtnRect.collidepoint(
                [
                    coor1 - coor2
                    for coor1, coor2 in zip(pygame.mouse.get_pos(), self.rect.topleft)
                ]
            ):
                self.surf.blit(TRADE_LOCK_BTN, self.lockBtnRect)

            else:
                self.surf.blit(TRADE_LOCK_BTN_CLICKED, self.lockBtnRect)

            #  --------------------- TRADE HANDLING ------------- #

            #  Confirm pop-up send, waiting case :
            if self.waitingFlag:
                waitingFont = pygame.font.Font(
                    DUNGEON_FONT, BUTTON_FONT_SIZE + 20
                ).render(
                    f"Waiting for response {'.'*(int(1.5*(time.time()-self.waitChrono)) % 4)}",
                    True,
                    (0, 0, 0),
                )
                layout = pygame.transform.scale(
                    HUDConf.NAME_SLOT.copy(),
                    (
                        int(waitingFont.get_width() * 1.5),
                        int(waitingFont.get_height() * 1.5),
                    ),
                )
                layout.blit(
                    waitingFont,
                    waitingFont.get_rect(
                        center=(layout.get_width() // 2, layout.get_height() // 2)
                    ),
                )
                self.Game.screen.blit(
                    layout,
                    layout.get_rect(
                        center=(
                            self.Game.resolution // 2,
                            int(self.Game.resolution * 0.925),
                        )
                    ),
                )

            # --------------- ITEM HANDLING ----------------- #
            self._showItems()
            self.Game.screen.blit(self.surf, self.rect)

            # When receiving confirmation from the target send by the network, pop up the choice to accept it or not
            if self.confirmRecvFlag and self.NetworkController.inTrade:
                self.acceptPopUp.show()
                self.confirmRecvFlag = False

            if self.targetAcceptedTrade == "ACCEPTED":
                self.proceedTrade()
                self.targetAcceptedTrade = "UNDEFINED"
            elif self.targetAcceptedTrade == "REFUSED":
                self.waitingFlag = False
                self.reset()
                self.targetAcceptedTrade = "UNDEFINED"

            # --------------- INVENTORY HANDLING ---------------- #

            self.Hero.Inventory.nestedShow(
                [self.Game.resolution // 2, self.Game.resolution // 3]
            )

    def _checkItemSelection(self, event):

        mousePosTranslated = [
            coor - rectTopLeftCoor
            for coor, rectTopLeftCoor in zip(pygame.mouse.get_pos(), self.rect.topleft)
        ]

        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):

                # Checking item selection
                if (
                    self.player_storage["tab"][j][i] != None
                    and self.player_storage["tab"][j][i].rect.collidepoint(
                        mousePosTranslated
                    )
                    and event.type == MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    self.trade_to_inv((i, j))

    def inventory_to_trade(self, itemPos):

        itemPlaced = False
        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):
                if self.player_storage["tab"][j][i] == None and not itemPlaced:
                    (
                        self.player_storage["tab"][j][i],
                        self.Hero.Inventory.storage["tab"][itemPos[1]][itemPos[0]],
                    ) = (
                        self.Hero.Inventory.storage["tab"][itemPos[1]][itemPos[0]],
                        self.player_storage["tab"][j][i],
                    )
                    self.player_storage["tab"][j][i].setCoor(
                        (
                            PLAYER_INIT_POINT[0] + i * self.player_storage["offset"][0],
                            PLAYER_INIT_POINT[1] + j * self.player_storage["offset"][1],
                        )
                    )
                    itemPlaced = True
                    break

        if not itemPlaced:

            Dialog(
                "The limit of item placed on the trade interface has been reached.",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                (255, 0, 0),
                self.Game,
                error=True,
                charLimit=100,
            ).mainShow()

    def trade_to_inv(self, itemPos):

        itemPlaced = False
        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):
                if self.Hero.Inventory.storage["tab"][j][i] == None and not itemPlaced:
                    (
                        self.Hero.Inventory.storage["tab"][j][i],
                        self.player_storage["tab"][itemPos[1]][itemPos[0]],
                    ) = (
                        self.player_storage["tab"][itemPos[1]][itemPos[0]],
                        self.Hero.Inventory.storage["tab"][j][i],
                    )

                    self.Hero.Inventory.storage["tab"][j][i].setCoor(
                        (
                            self.Hero.Inventory.storage["initPoint"][0]
                            + i * self.Hero.Inventory.storage["offset"][0],
                            self.Hero.Inventory.storage["initPoint"][1]
                            + j * self.Hero.Inventory.storage["offset"][1],
                        )
                    )
                    itemPlaced = True
                    break

    def hide(self):
        self._show = False
        self.Hero.Inventory.close()

    def reset(self):

        self.__init__(self.Game, self.Hero, self.target, self.NetworkController)
        self.hide()
        self.NetworkController.resetTrade()
        self.NetworkController.inTrade = False

    # --------------------- NETWORK --------------------- #

    def transmitItems(self, player_id, data):

        if self.NetworkController.inTrade:
            data["players"][player_id]["trade"]["tradedItems"] = [
                int(self.player_storage["tab"][j][i].property["Id"])
                for j in range(self.storageLength[1])
                for i in range(self.storageLength[0])
                if self.player_storage["tab"][j][i] != None
            ]

    def updateStuff(self, player_id, data):

        if self.NetworkController.inTrade:

            p_items = [
                self.target_storage["tab"][j][i].property["Id"]
                for j in range(self.storageLength[1])
                for i in range(self.storageLength[0])
                if self.target_storage["tab"][j][i] != None
            ]

            if p_items != data["players"][player_id]["trade"]["tradedItems"]:
                for j in range(self.storageLength[1]):
                    for i in range(self.storageLength[0]):
                        self.target_storage["tab"][j][i] = None

                for i, item_id in enumerate(
                    data["players"][player_id]["trade"]["tradedItems"]
                ):
                    # j = 0 as the storage of the trade is just one line
                    self.target_storage["tab"][0][i] = copy.deepcopy(
                        itemConf.ITEM_DB[item_id]
                    )
                    self.target_storage["tab"][0][i].loadIcon()
                    self.target_storage["tab"][0][i].loadSurfDesc()
                    self.target_storage["tab"][0][i].setCoor(
                        (
                            TARGET_INIT_POINT[0] + i * self.target_storage["offset"][0],
                            TARGET_INIT_POINT[1],
                        )
                    )

    def sendTradeAccept(self):

        self.NetworkController.acceptTrade()  # Send the flag so the local changes can be done onto the target's local version
        self.proceedTrade()  # Contains the reset method call

    def sendTradeRefuse(self):

        self.NetworkController.refuseTrade()
        self.reset()

    def proceedTrade(self):

        logger.debug(
            f"Proceeding with player storage : {self.player_storage} and target storage : {self.target_storage}"
        )

        # First : clean the trade UI slot so the items trade by the player disappear locally
        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):
                self.player_storage["tab"][j][i] = None

        #  Then, creating the item from the IDs of the target
        targetItemLen = (
            len(
                [
                    self.target_storage["tab"][j][i]
                    for i in range(self.storageLength[0])
                    for j in range(self.storageLength[1])
                    if self.target_storage["tab"][j][i] != None
                ]
            )
            - 1
        )

        for j in range(INVENTORY_STORAGE_HEIGHT):
            for i in range(INVENTORY_STORAGE_WIDTH):
                if (
                    self.Hero.Inventory.storage["tab"][j][i] == None
                    and targetItemLen >= 0
                ):
                    (
                        self.target_storage["tab"][0][targetItemLen],
                        self.Hero.Inventory.storage["tab"][j][i],
                    ) = (
                        self.Hero.Inventory.storage["tab"][j][i],
                        self.target_storage["tab"][0][targetItemLen],
                    )
                    self.Hero.Inventory.storage["tab"][j][i].setCoor(
                        (
                            INVENTORY_STORAGE_INIT_POS[0]
                            + i * self.Hero.Inventory.storage["offset"][0],
                            INVENTORY_STORAGE_INIT_POS[1]
                            + j * self.Hero.Inventory.storage["offset"][1],
                        )
                    )
                    targetItemLen -= 1

        self.reset()