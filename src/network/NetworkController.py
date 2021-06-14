import json
from logging import Logger
from network.chat import Chat
import sys
from math import sqrt
import threading
import time
import os
import sys
import pygame

from pygame.constants import MOUSEBUTTONUP
from Player.Character import Character
from UI.UI_utils_text import Dialog, SelectPopUp, TextBoxControl
from config import playerConf
from config.UIConf import BUTTON_FONT_SIZE, DUNGEON_FONT
from config.playerConf import CLASSES_NAMES
from utils.utils import logger
import uuid
import select

import config.HUDConf as HUDConf
from utils.Network_helpers import *
from .packet_types import *
from config.netConf import *
import socket
import copy


class NetworkController:
    def __init__(self, gameController, Map, Hero, ContextMenu) -> None:

        self.Game = gameController
        self.Map = Map
        self.Hero = Hero
        self.ContextMenu = ContextMenu
        self.LoadingMenu = None
        self.PauseMenu = None
        ContextMenu.networkController = self

        # ------------- PLAYERS HANDLING -------------- #
        self.players = {}  # Contains only the other players
        self.monsters = []
        self.Hero.networkId = str(uuid.uuid4())
        self.sessionChunks = (
            {}
        )  # Contains the chunkCoors/elementsTab discovered by ALL the players in the game
        self.players_timeout = {}

        # --------------- SESSION SETTINGS -------------- #
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 1))  # connect() for UDP doesn't send packets
        self.local_ip_address = s.getsockname()[0]
        s.close()
        self.isSessionCreator = False

        # ------------------- THREAD HANDLING ---------------#

        self.total_packet_transmitted = 0
        self.packet_transmitted = 0
        self.threads = {
            "C_client_creation": threading.Thread(
                target=run_C_client, args=(self.Hero.networkId,)
            ),
            "C_client_joiner": threading.Thread(
                target=run_C_client, args=(self.Hero.networkId, "")
            ),
            "connection_handler": threading.Thread(target=self.handleConnectedPlayers),
        }

        # ------------ GRAPHICAL PANNEL --------------- #

        self._show = False

        # Chat
        self.chat = Chat(self.Game, self.Hero)

        # Trade UI
        self.inTrade = False
        self.sendTradeDestId = None
        self.tradeInvRefused = None
        self.sendTradeConf = False
        self.acceptTradeState = "UNDEFINED"
        self.resetTradeSettings = False

        # -------------- NETWORK ---------------- #

        self.textBox = TextBoxControl(
            (self.Game.resolution // 2, self.Game.resolution // 3)
        )

    def addPlayer(self, new_id, name):
        """Create a Character Instance based of the informations given by the connexion of the player"""

        logger.info(f"#{new_id} joined the party !")

        self.players[new_id] = Character(self.Game, self.Map)
        self.players[new_id].initHUD()
        self.players[new_id].name = name
        self.players[new_id].networkId = new_id

        self.players_timeout[new_id] = time.time()

    def joinConnection(self, ip_addr="127.0.0.1"):

        self.Game.isOnline = True

        try:
            Dialog(
                f"Enter the host's ip : ",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                ONLINE_DIALOG_COLOR,
                self.Game,
            ).mainShow()

            self.textBox.input._show = True
            self.bg = self.Game.screen.copy()
            while 1:
                self.Game.screen.blit(self.bg, (0, 0))
                for e in pygame.event.get():
                    self.textBox.checkEvent(e)

                self.textBox.show(self.Game.screen)
                self.Game.show()

                if not self.textBox.input._show:
                    if ping(self.textBox.name):
                        self.setupNetworkSettings(join=True, ip_addr=self.textBox.name)
                        break
                    else:
                        Dialog(
                            f"This IP address isn't active in the LAN, enter another one !",
                            (self.Game.resolution // 2, self.Game.resolution // 2),
                            self.Game.screen,
                            ONLINE_DIALOG_COLOR,
                            self.Game,
                            error=True,
                        ).mainShow()
                        self.textBox.reset()
                        self.textBox.input._show = True

            Dialog(
                f"Joining {self.textBox.name}:{DEFAULT_PORT} !",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                ONLINE_DIALOG_COLOR,
                self.Game,
            ).mainShow()

        except:
            Dialog(
                f"The game cannot be joined.",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                ONLINE_DIALOG_COLOR,
                self.Game,
                error=True,
            ).mainShow()

        # with open(IPC_FIFO_OUTPUT_JOINER) as fifo:
        #     # data = fifo.read()
        #     str_data = get_raw_data_to_str(fifo)
        #     data = json.loads(str_data, indent=2)

        # # fifo = os.open(IPC_FIFO_OUTPUT, os.O_WRONLY)
        # # user_encode_data = json.dumps(data, indent=2).encode("utf-8")
        # # os.write(fifo, create_msg(user_encode_data))
        # # os.close(fifo)

        # # MAP LOADING
        # if not data["players"][self.Hero.networkId]["creator"]:

        #     new_seed = None
        #     for player in data["players"].values():
        #         if player["creator"]:
        #             new_seed = player["mapInfo"]["seed"]
        #             break

        #     if new_seed != self.Map.mapSeed:
        #         self.Game.loadNewGame()  # State to 'loadingNewGame'

        #         self.LoadingMenu.confirmLoading("HUDLoading")
        #         self.LoadingMenu.confirmLoading("ItemDBLoading", "gameObjectLoading")
        #         self.LoadingMenu.confirmLoading("spellDBLoading", "gameObjectLoading")

        #         def reGenMap():
        #             # reseting chunks for flags update
        #             self.Map.mapSeed = new_seed
        #             self.Map.chunkData = {
        #                 "mainChunk": pygame.Surface(
        #                     (
        #                         self.Map.CHUNK_SIZE * (self.Map.renderDistance + 2),
        #                         self.Map.CHUNK_SIZE * (self.Map.renderDistance + 2),
        #                     )
        #                 ),
        #                 "currentChunkPos": [0, 0],
        #             }

        #             for Hero in self.Game.heroesGroup:
        #                 self.Map.loadPlayerdMap(self.Map.maxChunkGen, Hero)

        #         loadingThread = threading.Thread(target=reGenMap)
        #         loadingThread.start()

        #         self.LoadingMenu.worldflags = None
        #         while self.Game.currentState == "loadingNewGame":
        #             self.LoadingMenu.show()

        #         # self.Map.miniMap.worldMapSurf = (
        #         #     None  # Retrigger the minimap "world map" loading
        #         # )
        #         # self.Map.miniMap.WorldMap.mapSeed = new_seed

    def createConnection(self):

        try:
            # Local version
            self.setupNetworkSettings()
            self.Game.isOnline = True
            self.isSessionCreator = True

            Dialog(
                f"Your game is online, on {self.local_ip_address}:{DEFAULT_PORT} ! Share this adress to someone who wants to join you on your LAN !",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                ONLINE_DIALOG_COLOR,
                self.Game,
            ).mainShow()

            # INSERT HERE DISCOVERY PACKET
            self.Hero.transmitCharacInfos()

        except:
            Dialog(
                f"The game can't be ported on LAN.",
                (self.Game.resolution // 2, self.Game.resolution // 2),
                self.Game.screen,
                ONLINE_DIALOG_COLOR,
                self.Game,
                error=True,
            ).mainShow()

    def setupNetworkSettings(self, join=False, ip_addr="") -> None:
        """
        Setting up the network by doing the following :
        - creating the 2 system pipes for python/C two-waay communication
        - running the C client
        - running the thread for handling input data from the C client (through the input pipe)
        """

        try:
            logger.info("[+] Creating the pipes")

            os.mkfifo(IPC_FIFO_INPUT)
            os.mkfifo(IPC_FIFO_OUTPUT)
        except:

            logger.warn("[x] FIFOs are already created, proceeding ...")

        logger.info(
            f"[+] Starting C Module [{'PARTY OWNER' if not join else 'PARTY JOINER'}] "
        )
        if not join:
            self.threads["C_client_creation"].start()
        else:
            self.threads["C_client_joiner"] = threading.Thread(
                target=run_C_client, args=(self.Hero.networkId, ip_addr)
            )
            self.threads["C_client_joiner"].start()

        logger.info("[+] Starting handle connection thread")
        self.threads["connection_handler"].start()

        # Packet send to "wake up" the client with the pipe file descriptor e.g add in in the select's active fd
        # fifo = os.open(IPC_FIFO_OUTPUT, os.O_WRONLY)
        # os.write(fifo, OPEN_CONNEXION_BYTE)
        # os.close(fifo)

    def handleConnectedPlayers(self):

        # ------------------ DATA RECV PART ---------------------- #

        # str_data = get_raw_data_to_str(self.isSessionCreator)
        # Open the pipe in non-blocking mode for reading
        fifo = os.open(
            IPC_FIFO_INPUT,
            os.O_RDONLY | os.O_NONBLOCK,
        )
        try:
            # Create a polling object to monitor the pipe for new data
            poll = select.poll()
            poll.register(fifo, select.POLLIN)
            try:
                while True:
                    # Check if there's data to read. Timeout after config.netCof.POLLIN_TIMEOUT sec.
                    if (fifo, select.POLLIN) in poll.poll(POLLIN_TIMEOUT * 10000):
                        # msg_size_bytes = os.read(fifo, 4)
                        # msg_size = decode_msg_size(msg_size_bytes)
                        # print(f"Reading {msg_size} bytes !")
                        try:
                            str_data = os.read(fifo, 2048).decode("utf-8")
                        except:
                            print(
                                "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc0 in position 0: invalid start byte"
                            )
                            str_data = ""

                        if len(str_data) > 2:
                            self.total_packet_transmitted += 1
                            print("receved from python : ", str_data)

                            try:
                                if "}{" in str_data:
                                    str_data = str_data[0 : str_data.index("}{") + 1]
                                    print("corrected : ", str_data)

                                packet = json.loads(str_data)
                                self.packet_transmitted += 1

                                # --------------- TIMEOUT HANDLING ---------------- #
                                # self.players_timeout[
                                #     packet["sender_id"]
                                # ] = time.time()  # reset the timer

                                # for (
                                #     player_id,
                                #     current_timer,
                                # ) in self.players_timeout.items():
                                #     if (
                                #         current_timer - time.time()
                                #     ) >= PLAYER_DECONNECTION_TIMEOUT * 60:
                                #         fifo = os.open(IPC_FIFO_OUTPUT, os.O_WRONLY)
                                #         os.write(fifo, DECONNECTION_TIMEOUT_BYTES)
                                #         os.write(fifo, player_id.encode("utf-8"))
                                #         os.close(fifo)

                                # --------------- NEW PLAYER DETECTION -------------------------- #

                                if packet["type"] == "discovery_request":

                                    print("Recv disco request paquet from client")
                                    disc_packet = copy.deepcopy(TEMPLATE_NEW_CONNECTION)
                                    disc_packet["classId"] = self.Hero.classId
                                    disc_packet["sender_id"] = self.Hero.networkId
                                    disc_packet["spellsID"] = self.Hero.spellsID
                                    disc_packet["stats"] = self.Hero.stats
                                    disc_packet["player_name"] = self.Hero.name
                                    disc_packet["map_seed"] = self.Map.mapSeed
                                    disc_packet["storage"] = {
                                        str(self.Hero.Inventory.storage["tab"][j][i].property["Id"]): (i, j)
                                        for j in range(INVENTORY_STORAGE_HEIGHT)
                                        for i in range(INVENTORY_STORAGE_WIDTH)
                                        if self.Hero.Inventory.storage["tab"][j][i] != None
                                    }
                                    disc_packet["equipment"] = {
                                        str(slot): int(slot_item["item"].property["Id"])
                                        for slot, slot_item in self.Hero.Inventory.equipment.items()
                                        if slot_item["item"] != None
                                    }

                                    write_to_pipe(IPC_FIFO_OUTPUT, disc_packet)
                                    print("End of disc request packet")

                                if packet["type"] == "discovery" and packet[
                                    "sender_id"
                                ] not in list(self.players.keys()) + [
                                    self.Hero.networkId
                                ]:
                                    self.addPlayer(
                                        packet["sender_id"],
                                        packet["player_name"],
                                    )
                                    self.chat.chatWindow.addText(
                                        packet["player_name"],
                                        "joined the game !",
                                        True,
                                        "CONNEXION",
                                    )
                                    print("Receiving desc packet")

                                    self.Hero.classId = packet["classId"]
                                    self.Hero.name = packet["player_name"]
                                    self.Map.mapSeed = packet["map_seed"]
                                    self.Hero.stats = packet["stats"]
                                    self.Hero.Inventory.updateInventory(
                                                packet["storage"],
                                                packet["equipment"],
                                            )

                                    print("Sending packet")
                                    disc_packet = copy.deepcopy(TEMPLATE_NEW_CONNECTION)
                                    disc_packet["classId"] = self.Hero.classId
                                    disc_packet["sender_id"] = self.Hero.networkId
                                    disc_packet["spellsID"] = self.Hero.spellsID
                                    disc_packet["stats"] = self.Hero.stats
                                    disc_packet["player_name"] = self.Hero.name
                                    disc_packet["map_seed"] = self.Map.mapSeed
                                    disc_packet["storage"] = {
                                        str(self.Hero.Inventory.storage["tab"][j][i].property["Id"]): (i, j)
                                        for j in range(INVENTORY_STORAGE_HEIGHT)
                                        for i in range(INVENTORY_STORAGE_WIDTH)
                                        if self.Hero.Inventory.storage["tab"][j][i] != None
                                    }
                                    disc_packet["equipment"] = {
                                        str(slot): int(slot_item["item"].property["Id"])
                                        for slot, slot_item in self.Hero.Inventory.equipment.items()
                                        if slot_item["item"] != None
                                    }

                                    print("disc packet send !")
                                    write_to_pipe(IPC_FIFO_OUTPUT, disc_packet)

                                for player_id, player in self.players.items():
                                    if player_id == packet["sender_id"]:

                                        # -------------- MAP RECV ------------ #
                                        if packet["type"] == "info_pos":

                                            # if packet["chunkCoor"] not in self.sessionChunks:
                                            #     self.sessionChunks[packet["chunkCoor"]] = []  # TODO

                                            # Check wether the player and the other connected are on the same chunk or not
                                            player.posMainChunkCenter = packet[
                                                "chunkPos"
                                            ]
                                            player.direction = packet["direction"]
                                            player.imageState = {
                                                "image": playerConf.CLASSES[
                                                    player.classId
                                                ]["directions"][player.direction][
                                                    packet["imagePos"]
                                                ],
                                                "imagePos": packet["imagePos"],
                                            }
                                            player.currentPlace = packet["currentPlace"]
                                            # player.Map.chunkData[
                                            #     "currentChunkPos"
                                            # ] = packet["chunkCoor"]

                                            # logger.debug(
                                            #     f"[+] Updating pos for player {player_id}"
                                            # )

                                            # Chunk rendering optimisation TODO
                                            # if (
                                            #     sqrt(
                                            #         sum(
                                            #             [
                                            #                 (p1coor - p2coor) ** 2
                                            #                 for p1coor, p2coor in zip(
                                            #                     data["players"][player_id]["chunkPos"],
                                            #                     self.Hero.Map.chunkData["currentChsunkPos"],
                                            #                 )
                                            #             ]
                                            #         )
                                            #     )
                                            # ) <= self.Map.renderDistance :

                                        # -------------------- FIGHT RECV ------------------- #
                                        if packet["type"] == "fight":
                                            if self.Game.fightMode.fightOn == False:
                                                self.Game.fightMode.fightOn = True
                                                self.Game.fightMode.challengerId = (
                                                    self.players[packet["sender_id"]]
                                                )
                                                self.players[
                                                    packet["sender_id"]
                                                ] = False

                                            if len(
                                                self.Game.fightMode.list_tour
                                            ) > 1 and packet[
                                                "dest"
                                            ] != self.Game.fightMode.list_tour[
                                                0
                                            ].trouver_case(
                                                self.Game.fightMode.list_case
                                            ).numero_case(
                                                self.Game.fightMode.list_case
                                            ):
                                                print("Entering fight mode")
                                                self.Game.fightMode.print_anim(
                                                    self.Game.fightMode.list_tour[
                                                        0
                                                    ].trouver_case(
                                                        self.Game.fightMode.list_case
                                                    ),
                                                    self.Game.fightMode.list_case[
                                                        packet["dest"]
                                                    ],
                                                    self.Game.fightMode.list_case,
                                                )
                                                print("1")

                                                self.Game.fightMode.list_case[
                                                    packet["dest"]
                                                ].in_case = self.Game.fightMode.list_tour[
                                                    0
                                                ]
                                                self.Game.fightMode.list_tour[
                                                    0
                                                ].trouver_case(
                                                    self.Game.fightMode.list_case
                                                ).in_case = None
                                                print("2")
                                                self.Game.fightMode.running = False

                                        # ------------------ INVENTORY RECV ------------------- #
                                        if packet["type"] == "info_inv":
                                            player.Inventory.updateInventory(
                                                packet["storage"],
                                                packet["equipment"],
                                            )

                                        # ----------------- CHARAC INFO RECV ------------------ #
                                        if packet["type"] == "info_charac":
                                            player.classId = packet["classId"]
                                            player.direction = packet["direction"]
                                            player.stats = packet["stats"]

                                            p_spells = sorted(player.spellsID[::])
                                            d_spells = sorted(packet["spellsID"][::])
                                            if p_spells != d_spells:
                                                player.spellsID = packet["spellsID"]
                                                player.SpellBook.updateSpellBook()

                                        # ------------------ TRADE RECV ----------- #
                                        if packet["type"] == "trade":
                                            pass

                                        # ------------------ MESSAGE RECV ----------- #
                                        if packet["type"] == "message":
                                            print(
                                                "OUI LE MESSAGE : ", packet["content"]
                                            )

                                            self.chat.chatWindow.addText(
                                                self.players[packet["sender_id"]].name,
                                                packet["content"],
                                                packet["italic"],
                                                packet["color_code"],
                                                recv=True,
                                            )

                                        # ---------------- DECONNEXION RECV ------------ #
                                        if packet["type"] == "deconnection":

                                            print("deconnection entering")
                                            self.chat.chatWindow.addText(
                                                packet["player_name"],
                                                "left the game !",
                                                True,
                                                "DECONNEXION",
                                            )
                                            self.players = {
                                                k: v
                                                for k, v in self.players.items()
                                                if k != packet["sender_id"]
                                            }

                            except:
                                print("error on this packet : ", str_data)
                                packet = {
                                    "name": "test_packet_bug",
                                    "sender_id": "Unknown_id",
                                }
            finally:
                poll.unregister(fifo)
        finally:
            os.close(fifo)

            # if data["players"][self.Hero.networkId]["trade"][
            #     "tradeInvitation"
            # ]["refused"]:
            #     self.ContextMenu.tradeUI.hide()

            # for player_id, player in self.players.items():

            #     # ----------------------------- TRADES HANDLING ------------------ #

            #     # Invitation to trade handling
            #     if not self.inTrade:
            #         for _player_id, _player in data["players"].items():
            #             if (
            #                 _player["trade"]["tradeInvitation"]["to"]
            #                 == self.Hero.networkId
            #             ):
            #                 SelectPopUp(
            #                     {
            #                         "Yes": lambda: self.acceptTradeInv(
            #                             _player_id
            #                         ),
            #                         "No": lambda: self.refuseTradeInv(
            #                             _player_id
            #                         ),
            #                     },
            #                     self.Game.screen,
            #                     self.Game,
            #                     (
            #                         self.Game.resolution // 2,
            #                         self.Game.resolution // 2,
            #                     ),
            #                     f"{self.players[_player_id].name} wants to trade with you, do you accept ?",
            #                 ).show()
            #                 break

            #     if self.ContextMenu.tradeUI != None:

            #         if (
            #             data["players"][
            #                 self.ContextMenu.tradeUI.target.networkId
            #             ]["trade"]["confirmFlag"]
            #             and not self.ContextMenu.tradeUI.confirmRecvFlag
            #         ):
            #             self.ContextMenu.tradeUI.confirmRecvFlag = True

            #         self.ContextMenu.tradeUI.targetAcceptedTrade = data[
            #             "players"
            #         ][self.ContextMenu.tradeUI.target.networkId][
            #             "trade"
            #         ][
            #             "tradeState"
            #         ]

            #         self.ContextMenu.tradeUI.updateStuff(
            #             self.ContextMenu.tradeUI.target.networkId, data
            #         )

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

    def updateGraphics(self):

        # --------------------------------- GRAPHICAL UPDATING ------------------------- #

        for player in self.players.values():

            # HUD Updating
            if (
                player.Inventory != None
                and player.SpellBook != None
                and player.CharBar != None
            ):
                player.Inventory.draw()
                player.SpellBook.draw()

            # logger.debug(f"[+] Bliting image pos for player")
            if player.currentPlace == self.Hero.currentPlace:
                if player.currentPlace == "openWorld":

                    # Map pos updating
                    if (
                        self.Hero.Map.chunkData["currentChunkPos"]
                        != player.Map.chunkData["currentChunkPos"]
                    ):
                        playersDist = [
                            (pos2 - pos1)
                            + 2
                            * (1 if pos2 > pos1 else -1)
                            * (self.Map.CHUNK_SIZE // 2 - abs((pos2 - pos1)))
                            for pos1, pos2 in zip(
                                player.posMainChunkCenter, self.Hero.posMainChunkCenter
                            )
                        ]
                        print("debug : ", playersDist)
                    else:
                        playersDist = [
                            pos1 - pos2
                            for pos1, pos2 in zip(
                                player.posMainChunkCenter, self.Hero.posMainChunkCenter
                            )
                        ]
                else:
                    playersDist = [
                        pos1 - pos2
                        for pos1, pos2 in zip(
                            [player.buildingPosX, player.buildingPosY],
                            [self.Hero.buildingPosX, self.Hero.buildingPosY],
                        )
                    ]
                self.Game.screen.blit(
                    player.imageState["image"],
                    player.imageState["image"].get_rect(
                        center=[
                            self.Game.resolution // 2 + distCoor
                            for distCoor in playersDist
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
            # Handle thread
            if player.SpellBook != None and player.Inventory != None:
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

    def quitOnline(self):

        """Whether you are the creator of the game or a joiner, you can leave a game the same way"""

        dump_network_logs(
            (1 - (self.packet_transmitted / self.total_packet_transmitted))
            if self.total_packet_transmitted != 0
            else 0
        )

        # fifo = os.open(IPC_FIFO_OUTPUT, os.O_WRONLY)
        # os.write(fifo, DECONNECTION_MANUAL_BYTES)
        # os.close(fifo)
        deco_packet = copy.deepcopy(TEMPLATE_DECONNEXION)
        deco_packet["sender_id"] = self.Hero.networkId
        deco_packet["player_name"] = self.Hero.name
        write_to_pipe(IPC_FIFO_OUTPUT, deco_packet)

        # for t in self.threads.values():
        #     if t.is_alive:
        #         t.join(0.5)

        self.players = {}  # Contains only the other players
        self.monsters = []
        self.Hero.networkId = str(uuid.uuid4())
        self.total_packet_transmitted = 0
        self.packet_transmitted = 0

        self.isSessionCreator = False
        self.Game.isOnline = False

        self.PauseMenu.setButtons()

        os.remove(IPC_FIFO_INPUT)
        os.remove(IPC_FIFO_OUTPUT)

        Dialog(
            "You left the party, you can now see the logs of your session in /src/network/net_session.log",
            (self.Game.resolution // 2, self.Game.resolution // 2),
            self.Game.screen,
            (0, 0, 0),
            self.Game,
        ).mainShow()

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
