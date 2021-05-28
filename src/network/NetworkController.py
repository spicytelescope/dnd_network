import json
import sys
from math import sqrt
import threading
import time
import os
import sys
import pygame
import copy

from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from Player.Character import Character
from UI.UI_utils_text import SelectPopUp
from config import playerConf
from config.UIConf import BUTTON_FONT_SIZE, DUNGEON_FONT
from config.playerConf import CLASSES_NAMES
from utils.utils import logger
import uuid

import config.HUDConf as HUDConf
from utils.Network_helpers import *
from .packet_types import *
from config.netConf import *


class NetworkController:
    def __init__(self, gameController, Map, Hero, ContextMenu) -> None:

        self.Game = gameController
        self.Map = Map
        self.Hero = Hero
        self.ContextMenu = ContextMenu
        ContextMenu.networkController = self

        self.players = {}  # Contains only the other players
        self.cache_data = {}
        self.monsters = []
        self.Hero.networkId = str(uuid.uuid4())
        self.LoadingMenu = None

        self.sessionChunks = (
            {}
        )  # Contains the chunkCoors/elementsTab discovered by ALL the players in the game

        # ------------ GRAPHICAL PANNEL --------------- #

        self._show = False

        # Trade UI
        self.inTrade = False
        self.sendTradeDestId = None
        self.tradeInvRefused = None
        self.sendTradeConf = False
        self.acceptTradeState = "UNDEFINED"
        self.resetTradeSettings = False

    def addPlayer(self, new_id, name):
        """Create a Character Instance based of the informations given by the connexion of the player"""

        logger.info(f"#{new_id} joined the party !")

        self.players.update({new_id: Character(self.Game, self.Map)})
        self.players[new_id].initHUD()
        self.players[new_id].name = name
        self.players[new_id].networkId = new_id

    def joinConnection(self, ip_addr):

        self.Game.isOnline = True

        with open(IPC_FIFO_OUTPUT) as fifo:
            data = fifo.read()
            if len(data) == 0:
                data = self.cache_data
            else:
                str_data = get_raw_data_to_str(fifo)
                data = json.loads(str_data, indent=2)

        fifo = os.open(IPC_FIFO_OUTPUT, os.O_WRONLY)
        user_encode_data = json.dumps(data, indent=2).encode("utf-8")
        os.write(fifo, create_msg(user_encode_data))
        os.close(fifo)

        # MAP LOADING
        if not data["players"][self.Hero.networkId]["creator"]:

            new_seed = None
            for player in data["players"].values():
                if player["creator"]:
                    new_seed = player["mapInfo"]["seed"]
                    break

            if new_seed != self.Map.mapSeed:
                self.Game.loadNewGame()  # State to 'loadingNewGame'

                self.LoadingMenu.confirmLoading("HUDLoading")
                self.LoadingMenu.confirmLoading("ItemDBLoading", "gameObjectLoading")
                self.LoadingMenu.confirmLoading("spellDBLoading", "gameObjectLoading")

                def reGenMap():
                    # reseting chunks for flags update
                    self.Map.mapSeed = new_seed
                    self.Map.chunkData = {
                        "mainChunk": pygame.Surface(
                            (
                                self.Map.CHUNK_SIZE * (self.Map.renderDistance + 2),
                                self.Map.CHUNK_SIZE * (self.Map.renderDistance + 2),
                            )
                        ),
                        "currentChunkPos": [0, 0],
                    }

                    for Hero in self.Game.heroesGroup:
                        self.Map.loadPlayerdMap(self.Map.maxChunkGen, Hero)

                loadingThread = threading.Thread(target=reGenMap)
                loadingThread.start()

                self.LoadingMenu.worldflags = None
                while self.Game.currentState == "loadingNewGame":
                    self.LoadingMenu.show()

                # self.Map.miniMap.worldMapSurf = (
                #     None  # Retrigger the minimap "world map" loading
                # )
                # self.Map.miniMap.WorldMap.mapSeed = new_seed

    def createConnection(self):

        self.Game.isOnline = True

    def handleConnectedPlayers(self):

        # ------------------ DATA RECV PART ---------------------- #

        with open(IPC_FIFO_INPUT, os.O_RDONLY | os.O_NONBLOCK) as fifo:
            data = fifo.read()
            if len(data) == 0:
                # data = self.cache_data
                logger.debug("No input data")
            else:

                str_data = get_raw_data_to_str(fifo)
                packet = json.loads(str_data, indent=2)

                # --------------- NEW PLAYER DETECTION -------------------------- #

                if packet["name"] == "discovery" and packet["sender_id"] not in list(
                    self.players.keys()
                ) + [self.Hero.networkId]:
                    self.addPlayer(
                        packet["sender_id"],
                        packet["player_name"],
                    )

                for player_id, player in self.players.items():
                    if player_id == packet["sender_id"]:

                        # -------------- MAP RECV ------------ #
                        if packet["name"] == "info_pos":

                            if packet["chunkCoor"] not in self.sessionChunks:
                                self.sessionChunks[packet["chunkCoor"]] = []  # TODO

                            # Check wether the player and the other connected are on the same chunk or not
                            player.posMainChunkCenter = data["players"][player_id][
                                "chunkPos"
                            ]

                            player.imageState = {
                                "image": playerConf.CLASSES[player.classId][
                                    "directions"
                                ][player.direction][packet["imagePos"]],
                                "imagePos": packet["imagePos"],
                            }

                            # Chunk rendering optimisation TODO
                            # if (
                            #     sqrt(
                            #         sum(
                            #             [
                            #                 (p1coor - p2coor) ** 2
                            #                 for p1coor, p2coor in zip(
                            #                     data["players"][player_id]["chunkPos"],
                            #                     self.Hero.Map.chunkData["currentChunkPos"],
                            #                 )
                            #             ]
                            #         )
                            #     )
                            # ) <= self.Map.renderDistance :
                        # ------------------ INVENTORY RECV ------------------- #
                        if packet["name"] == "info_inv":
                            player.Inventory.updateInventory(
                                packet["storage"],
                                packet["equipment"],
                            )

                        # ----------------- CHARAC INFO RECV ------------------ #
                        if packet["name"] == "info_charac":
                            player.classId = packet["classId"]
                            player.direction = packet["direction"]
                            player.stats = packet["stats"]

                            p_spells = sorted(player.spellsID[::])
                            d_spells = sorted(packet["spellsID"][::])
                            if p_spells != d_spells:
                                player.spellsID = packet["spellsID"]
                                player.SpellBook.updateSpellBook()

                        # ------------------ TRADE RECV ----------- #
                        if packet["name"] == "trade":
                            if data["players"][self.Hero.networkId]["trade"][
                                "tradeInvitation"
                            ]["refused"]:
                                self.ContextMenu.tradeUI.hide()

                            for player_id, player in self.players.items():

                                # ----------------------------- TRADES HANDLING ------------------ #

                                # Invitation to trade handling
                                if not self.inTrade:
                                    for _player_id, _player in data["players"].items():
                                        if (
                                            _player["trade"]["tradeInvitation"]["to"]
                                            == self.Hero.networkId
                                        ):
                                            SelectPopUp(
                                                {
                                                    "Yes": lambda: self.acceptTradeInv(
                                                        _player_id
                                                    ),
                                                    "No": lambda: self.refuseTradeInv(
                                                        _player_id
                                                    ),
                                                },
                                                self.Game.screen,
                                                self.Game,
                                                (
                                                    self.Game.resolution // 2,
                                                    self.Game.resolution // 2,
                                                ),
                                                f"{self.players[_player_id].name} wants to trade with you, do you accept ?",
                                            ).show()
                                            break

                                if self.ContextMenu.tradeUI != None:

                                    if (
                                        data["players"][
                                            self.ContextMenu.tradeUI.target.networkId
                                        ]["trade"]["confirmFlag"]
                                        and not self.ContextMenu.tradeUI.confirmRecvFlag
                                    ):
                                        self.ContextMenu.tradeUI.confirmRecvFlag = True

                                    self.ContextMenu.tradeUI.targetAcceptedTrade = data[
                                        "players"
                                    ][self.ContextMenu.tradeUI.target.networkId][
                                        "trade"
                                    ][
                                        "tradeState"
                                    ]

                                    self.ContextMenu.tradeUI.updateStuff(
                                        self.ContextMenu.tradeUI.target.networkId, data
                                    )

        # # --------------------------- TRADE UI -------------- #
        # if self.ContextMenu.tradeUI != None:
        #     self.ContextMenu.tradeUI.transmitItems(self.Hero.networkId, data)

        # if self.resetTradeSettings:
        #     self.resetTradeSettings = False
        #     resetDict = {
        #         "state": False,
        #         "to": None,
        #         "refused": False,
        #     }
        #     #     },
        #     #     "tradedItems": []
        #     #     "confirmFlag": False,  # Flag send when player 1 lock and ask for confirmation
        #     #     "tradeState": "UNDEFINED",  # Flag send when player 2 accept the trade
        #     # }
        #     data["players"][self.Hero.networkId]["trade"]["tradeInvitation"] = resetDict
        #     data["players"][self.Hero.networkId]["trade"]["tradeState"] = "UNDEFINED"

        #     data["players"][self.Hero.networkId]["trade"][
        #         "tradeInvitation"
        #     ] = "UNDEFINED"
        #     data["players"][self.ContextMenu.tradeUI.target.networkId]["trade"][
        #         "tradeInvitation"
        #     ] = resetDict

        # if self.sendTradeDestId != None:
        #     data["players"][self.Hero.networkId]["trade"]["tradeInvitation"] = {
        #         "state": True,
        #         "to": self.sendTradeDestId,
        #         "refused": False,
        #     }
        #     self.sendTradeDestId = None

        # if self.tradeInvRefused != None:
        #     data["players"][self.tradeInvRefused]["trade"]["tradeInvitation"][
        #         "refused"
        #     ] = True
        #     self.tradeInvRefused = None

        # if self.sendTradeConf:
        #     self.sendTradeConf = False
        #     data["players"][self.Hero.networkId]["trade"]["confirmFlag"] = True

        # if self.acceptTradeState == "ACCEPTED":
        #     data["players"][self.Hero.networkId]["trade"]["tradeState"] = "ACCEPTED"
        #     self.acceptTradeState = "UNDEFINED"

        # elif self.acceptTradeState == "REFUSED":
        #     self.acceptTradeState = "UNDEFINED"
        #     data["players"][self.Hero.networkId]["trade"]["tradeState"] = "REFUSED"

        # --------------------------------- GRAPHICAL UPDATING ------------------------- #

        for player in self.players.values():

            # HUD Updating
            player.Inventory.draw()
            player.SpellBook.draw()

            # Map pos updating
            playersDist = [
                pos1 - pos2
                for pos1, pos2 in zip(
                    player.posMainChunkCenter, self.Hero.posMainChunkCenter
                )
            ]
            self.Game.screen.blit(
                player.imageState["image"],
                player.imageState["image"].get_rect(
                    center=[
                        self.Game.resolution // 2 + distCoor for distCoor in playersDist
                    ]
                ),
            )

    def handleInteractions(self, event):
        """Handle the right click and the apparition of the pop-up menu to enable interactions between players"""
        mousePosTranslated = [
            coor + (self.Map.renderDistance * self.Map.CHUNK_SIZE) - offset
            for coor, offset in zip(pygame.mouse.get_pos(), self.Hero.blitOffset)
        ]

        self.ContextMenu.checkEvents(event)
        if self.ContextMenu.tradeUI != None:
            self.ContextMenu.tradeUI.checkActions(event)

        for player in self.players.values():
            if player.SpellBook._show:
                player.SpellBook.checkActions(event)
            if player.Inventory._show:
                player.Inventory.checkActions(event, protected=True)

            if event.type == MOUSEBUTTONUP and event.button == 1:
                if (
                    player.imageState["image"]
                    .get_rect(center=player.posMainChunkCenter)
                    .collidepoint(mousePosTranslated)
                ):
                    self.ContextMenu.bind(
                        self.Game.heroesGroup[self.Game.heroIndex], player
                    )
                    self.ContextMenu.show()

                    break

    # ---------------------- GRAPHICAL UI -------------------------- #

    def drawPannel(self):

        if self._show:

            layout = pygame.transform.scale(
                HUDConf.QUEST_JOURNAL_MAIN_SURF,
                (self.Game.resolution // 2, self.Game.resolution // 2),
            )

            layoutRect = layout.get_rect(
                center=(self.Game.resolution // 2, self.Game.resolution // 2)
            )

            title = pygame.font.Font(DUNGEON_FONT, 50).render(
                "CONNECTED PLAYERS", True, (0, 0, 0)
            )
            heroFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
                f"{self.Hero.name} (You)", True, (0, 0, 0)
            )

            layout.blit(
                title,
                title.get_rect(
                    center=(layoutRect.width // 2, 100 + title.get_height() / 2)
                ),
            )
            layout.blit(
                heroFont, heroFont.get_rect(center=(layoutRect.width // 2, 200))
            )
            for i, (player_id, player) in enumerate(self.players.items()):

                nameFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
                    f"{player.name} - {CLASSES_NAMES[player.classId]} Lv {player._Level}",
                    True,
                    (0, 0, 0),
                )
                layout.blit(
                    nameFont,
                    nameFont.get_rect(
                        center=(
                            layoutRect.width // 2,
                            200 + (30) * (i + 1),
                        )
                    ),
                )
            self.Game.screen.blit(layout, layoutRect)

    # ------------------------------- TRADE UI ------------------------- #

    def sendTradeConfirmation(self):

        self.sendTradeConf = True

    def acceptTradeInv(self, sender_id):
        self.ContextMenu.bind(
            self.Game.heroesGroup[self.Game.heroIndex],
            self.players[sender_id],
        )
        self.ContextMenu.tradeUI._show = True
        self.inTrade = True

    def refuseTradeInv(self, sender_id):
        self.tradeInvRefused = sender_id

    def acceptTrade(self):

        self.acceptTradeState = "ACCEPTED"

    def refuseTrade(self):
        self.acceptTradeState = "REFUSED"

    def sendTradeInv(self, dest_id):
        self.sendTradeDestId = dest_id

    def resetTrade(self):
        self.resetTradeSettings = True
