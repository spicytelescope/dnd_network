import json, sys
from math import sqrt
import threading
import time
import os, sys
import pygame

from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from Player.Character import Character
from UI.UI_utils_text import SelectPopUp
from config import playerConf
from config.UIConf import BUTTON_FONT_SIZE, DUNGEON_FONT
from config.playerConf import CLASSES_NAMES
from utils.utils import logger
import uuid

import config.HUDConf as HUDConf

# write data to info_input
def write(data):
    FIFO_PATH2 = "info_input"

    pipe = open(FIFO_PATH2, "w")
    pipe.write(data)


class NetworkController:
    def __init__(self, gameController, Map, Hero, ContextMenu) -> None:

        self.Game = gameController
        self.Map = Map
        self.Hero = Hero
        self.ContextMenu = ContextMenu
        ContextMenu.networkController = self

        self.players = {}  # Contains only the other players
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

        logger.info(f"#{new_id} connected to the server !")

        self.players.update({new_id: Character(self.Game, self.Map)})
        self.players[new_id].initHUD()
        self.players[new_id].name = name
        self.players[new_id].networkId = new_id

    def createTestConnection(self):

        self.Game.isOnline = True
        # Adding the hero
        data = json.load(open("./datas.json"))

        with open("./datas.json", "w") as f:

            # BASE SCHEME
            data["players"][self.Hero.networkId] = {
                "chunkPos": self.Hero.posMainChunkCenter,
                "chunkCoor": self.Hero.Map.chunkData["currentChunkPos"],
                "inventory": {"storage": {}, "equipment": {}},
                "creator": not any(
                    [player["creator"] for player in data["players"].values()]
                ),
                "characterInfo": {
                    "classId": self.Hero.classId,
                    "imagePos": self.Hero.imageState["imagePos"],
                    "direction": self.Hero.direction,
                    "spellsID": self.Hero.spellsID,
                    "name": self.Hero.name,
                    "stats": self.Hero.stats,
                },
                "mapInfo": {
                    "seed": self.Map.mapSeed
                    if not any(
                        [player["creator"] for player in data["players"].values()]
                    )
                    else None,
                    "chunkData": {},
                },
                "trade": {
                    "tradeInvitation": {"state": False, "to": None, "refused": False},
                    "tradedItems": [],
                    "confirmFlag": False,  # Flag send when player 1 lock and ask for confirmation
                    "tradeState": "UNDEFINED",  # Flag send when player 2 accept the trade
                },
            }
            logger.debug(f"Dumping {data}")
            json.dump(data, f)

        # MAP LOADING (if the player join a game)
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

    def handleConnectedPlayers(self):

        # ------------------ DATA TRANSMISSION ---------------------- #

        try:
            data = json.load(open("./datas.json"))  # Insérer ici pipe de Younes
            with open("datas.json", "w") as f:

                # ---------------------- CLIENT UPDATE (SEND PART) ------------ #
                self.Hero.Inventory.transmitInventoryInfos(self.Hero.networkId, data)
                self.Hero.Map.transmitPosInfos(self.Hero.networkId, data)
                self.Hero.transmitAnimInfos(self.Hero.networkId, data)
                # self.Hero.Map.transmitChunkCoors(
                #     self.Hero.networkId, data, self.sessionChunks
                # )

                # --------------------------- TRADE UI -------------- #
                if self.ContextMenu.tradeUI != None:
                    self.ContextMenu.tradeUI.transmitItems(self.Hero.networkId, data)

                if self.resetTradeSettings:
                    self.resetTradeSettings = False
                    resetDict = {
                        "state": False,
                        "to": None,
                        "refused": False,
                    }
                    #     },
                    #     "tradedItems": []
                    #     "confirmFlag": False,  # Flag send when player 1 lock and ask for confirmation
                    #     "tradeState": "UNDEFINED",  # Flag send when player 2 accept the trade
                    # }
                    data["players"][self.Hero.networkId]["trade"][
                        "tradeInvitation"
                    ] = resetDict
                    data["players"][self.Hero.networkId]["trade"][
                        "tradeState"
                    ] = "UNDEFINED"

                    data["players"][self.Hero.networkId]["trade"][
                        "tradeInvitation"
                    ] = "UNDEFINED"
                    data["players"][self.ContextMenu.tradeUI.target.networkId]["trade"][
                        "tradeInvitation"
                    ] = resetDict

                if self.sendTradeDestId != None:
                    data["players"][self.Hero.networkId]["trade"]["tradeInvitation"] = {
                        "state": True,
                        "to": self.sendTradeDestId,
                        "refused": False,
                    }
                    self.sendTradeDestId = None

                if self.tradeInvRefused != None:
                    data["players"][self.tradeInvRefused]["trade"]["tradeInvitation"][
                        "refused"
                    ] = True
                    self.tradeInvRefused = None

                if self.sendTradeConf:
                    self.sendTradeConf = False
                    data["players"][self.Hero.networkId]["trade"]["confirmFlag"] = True

                if self.acceptTradeState == "ACCEPTED":
                    data["players"][self.Hero.networkId]["trade"][
                        "tradeState"
                    ] = "ACCEPTED"
                    self.acceptTradeState = "UNDEFINED"

                elif self.acceptTradeState == "REFUSED":
                    self.acceptTradeState = "UNDEFINED"
                    data["players"][self.Hero.networkId]["trade"][
                        "tradeState"
                    ] = "REFUSED"

                json.dump(data, f)

                # --------------- NEW PLAYER DETECTION -------------------------- #
                for player_id in data["players"]:
                    if player_id != self.Hero.networkId:
                        if player_id not in self.players:
                            self.addPlayer(
                                player_id,
                                data["players"][player_id]["characterInfo"]["name"],
                            )

                # ------------------- Other PLAYERS UPDATING (RECV PART) ---------- #

                if data["players"][self.Hero.networkId]["trade"]["tradeInvitation"][
                    "refused"
                ]:
                    self.ContextMenu.tradeUI.hide()

                for player_id, player in self.players.items():

                    # ------------------ INVENTORY RECEIVING ------------------- #
                    player.Inventory.updateInventory(
                        data["players"][player_id]["inventory"]["storage"],
                        data["players"][player_id]["inventory"]["equipment"],
                    )

                    # ----------------- CHARAC INFO RECEIVING ------------------ #
                    player.classId = data["players"][player_id]["characterInfo"][
                        "classId"
                    ]
                    player.direction = data["players"][player_id]["characterInfo"][
                        "direction"
                    ]
                    player.stats = data["players"][player_id]["characterInfo"]["stats"]

                    player.imageState = {
                        "image": playerConf.CLASSES[player.classId]["directions"][
                            player.direction
                        ][data["players"][player_id]["characterInfo"]["imagePos"]],
                        "imagePos": data["players"][player_id]["characterInfo"][
                            "imagePos"
                        ],
                    }
                    p_spells = sorted(player.spellsID[::])
                    d_spells = sorted(
                        data["players"][player_id]["characterInfo"]["spellsID"][::]
                    )
                    if p_spells != d_spells:
                        player.spellsID = data["players"][player_id]["characterInfo"][
                            "spellsID"
                        ]
                        player.SpellBook.updateSpellBook()

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
                                        "Yes": lambda: self.acceptTradeInv(_player_id),
                                        "No": lambda: self.refuseTradeInv(_player_id),
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
                            data["players"][self.ContextMenu.tradeUI.target.networkId][
                                "trade"
                            ]["confirmFlag"]
                            and not self.ContextMenu.tradeUI.confirmRecvFlag
                        ):
                            self.ContextMenu.tradeUI.confirmRecvFlag = True

                        self.ContextMenu.tradeUI.targetAcceptedTrade = data["players"][
                            self.ContextMenu.tradeUI.target.networkId
                        ]["trade"]["tradeState"]

                        self.ContextMenu.tradeUI.updateStuff(
                            self.ContextMenu.tradeUI.target.networkId, data
                        )

                    #  ------------------- MAP RECEIVING ----------------------- #
                    for pChunkCoor, pChunkElementTab in data["players"][player_id][
                        "mapInfo"
                    ]["chunkData"].items():
                        if pChunkCoor not in self.sessionChunks:
                            self.sessionChunks[pChunkCoor] = pChunkElementTab

                    # Check wether the player and the other connected are on the same chunk or not
                    player.posMainChunkCenter = data["players"][player_id]["chunkPos"]
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
                    # ) <= self.Map.renderDistance

        except Exception as e:
            #     # logger.error(f"Latency case for entity {self.Hero.networkId}!")
            logger.error(e)

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
