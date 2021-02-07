from pandas.core.indexes import base
from UI.UI_utils_text import Dialog
import copy
import random
from threading import Thread

from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN
from config import UIConf

import config.itemConf as itemConf
import config.NPCConf as NPCConf
import pygame
from config.HUDConf import *
from config.itemConf import *
from config.playerConf import *
from config.UIConf import *
from HUD.Inventory import Inventory


class TradeUI:

    """
    Interface made of the storage of a chest and
    the information spot of an item
    """

    def __init__(self, gameController, Hero, Target) -> None:

        self.Game = gameController
        self.Hero = Hero
        self.target = Target
        self.open = False
        self.firstOpen = True

        # TEXTURES
        self.blank_surf = UIConf.TRADING_SURF
        self.surf = self.blank_surf.copy()
        self.rect = self.surf.get_rect(
            center=(self.Game.resolution // 2, int(self.Game.resolution * 0.75))
        )

        # ------------- LOCK BTN ------------------- #

        self.lockedSelected = False
        self.lockBtn = TRADE_LOCK_BTN
        self.lockBtnRect = self.lockBtn.get_rect(center=LOCK_BUTTON_POS)

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
        self.bg = None

    def _showItems(self):
        for j in range(self.storageLength[1]):
            for i in range(self.storageLength[0]):
                if self.player_storage["tab"][j][i] != None:
                    self.surf.blit(
                        self.player_storage["tab"][j][i].icon,
                        self.player_storage["tab"][j][i].rect,
                    )

    def exit(self):

        self.Hero.Inventory._close()
        self.open = False

    def show(self):

        self.open = True
        self.bg = self.Game.screen.copy()
        self.firstOpen = False

        while self.open:
            self.Game.screen.blit(self.bg, (0, 0))

            # HANDLING SELLER PROPER UI
            self.surf = self.blank_surf.copy()

            # NAME BLITING

            baseFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE)
            target_font = baseFont.render(self.target.name, True, (0, 0, 0))
            player_font = baseFont.render(self.Hero.name, True, (0, 0, 0))
            self.surf.blit(target_font, target_font.get_rect(center=NAME_SLOT_1))
            self.surf.blit(player_font, player_font.get_rect(center=NAME_SLOT_2))

            for event in pygame.event.get():

                self._checkItemSelection(event)  # checking for trader ui

                # --------------- INVENTORY HANDLING ------------- #

                self.Hero.Inventory._checkItemSelection(event)
                self.Hero.Inventory.checkTradeItem(event, self)

                # --------------- CONFIRM HANDLING ------------ #

                if (
                    self.lockBtnRect.collidepoint(
                        [
                            coor1 - coor2
                            for coor1, coor2 in zip(
                                pygame.mouse.get_pos(), self.rect.topleft
                            )
                        ]
                    )
                    and event.type == MOUSEBUTTONDOWN
                ):
                    logger.info("CONFIRM FUNC SEND")

                # ---------- EXIT HANDLING ----------- #

                if (
                    event.type == KEYDOWN
                    and event.key == self.Game.KeyBindings["Cancel trade"]["value"]
                ):
                    self.open = False

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            if self.open:

                # ---------------- BUTTON HANDLING -------------- #
                if self.lockBtnRect.collidepoint(
                    [
                        coor1 - coor2
                        for coor1, coor2 in zip(
                            pygame.mouse.get_pos(), self.rect.topleft
                        )
                    ]
                ):
                    self.surf.blit(TRADE_LOCK_BTN, self.lockBtnRect)

                else:
                    self.surf.blit(TRADE_LOCK_BTN_CLICKED, self.lockBtnRect)

                # --------------- ITEM HANDLING ----------------- #
                self._showItems()
                self.Game.screen.blit(self.surf, self.rect)

                # HANDLING INVENTORY
                self.Hero.Inventory.nestedShow(
                    [self.Game.resolution // 2, self.Game.resolution // 3]
                )
                self.Game.show()

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
                    and event.button == 3
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

    def reset(self):

        self._init__(self.Game, self.Hero)
