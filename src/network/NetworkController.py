import json
from math import sqrt
import pygame

from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from Player.Character import Character
from config.UIConf import BUTTON_FONT_SIZE, DUNGEON_FONT
from config.playerConf import CLASSES_NAMES
from utils.utils import logger
import uuid

import config.HUDConf as HUDConf


class NetworkController:
    def __init__(self, gameController, Map, Hero, ContextMenu) -> None:

        self.Game = gameController
        self.Map = Map
        self.Hero = Hero
        self.ContextMenu = ContextMenu

        self.players = {}  # Contains only the other players
        self.monsters = []
        self.Hero.networkId = str(uuid.uuid4())

    def addPlayer(self, new_id):
        """Create a Character Instance based of the informations given by the connexion of the player"""

        logger.info(f"#{new_id} connected to the server !")

        self.players.update({new_id: Character(self.Game, self.Map)})
        self.players[new_id].initHUD()

        logger.debug(f"Player list : {self.players}")

    def createTestConnection(self):

        self.Game.isOnline = True
        # Adding the hero
        data = json.load(open("./datas.json"))
        with open("./datas.json", "w") as f:
            data["players"][self.Hero.networkId] = {
                "chunkPos": self.Hero.posMainChunkCenter,
                "chunkCoor": self.Hero.Map.chunkData["currentChunkPos"],
                "inventory": {"storage": [], "equipment": {}},
                "creator": False,
            }
            json.dump(data, f)
        self.Hero.Inventory.transmitInventoryInfos(self.Hero.networkId)

    def handleConnectedPlayers(self):

        # ------------------ DATA TRANSMISSION ---------------------- #

        try:
            with open("datas.json", "r") as f:
                data = json.load(f)

                # New player detection
                for player_id in data["players"]:
                    if player_id != self.Hero.networkId:
                        if player_id not in self.players:
                            self.addPlayer(player_id)
                        else:
                            # Pos update
                            self.players[player_id].posMainChunkCenter = data[
                                "players"
                            ][player_id]["chunkPos"]

                for player_id, player in self.players.items():

                    # player.Inventory.updateInventory({}, [])

                    # -------------------- INTERACTIONS --------------------- #
                    player.Inventory.draw()
                    player.SpellBook.draw()

                    # Check wether the player and the other connected are on the same chunk or not
                    if (
                        sqrt(
                            sum(
                                [
                                    (p1coor - p2coor) ** 2
                                    for p1coor, p2coor in zip(
                                        data["players"][player_id]["chunkPos"],
                                        self.Hero.Map.chunkData["currentChunkPos"],
                                    )
                                ]
                            )
                        )
                    ) <= self.Map.renderDistance:
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
                                    self.Game.resolution // 2 + distCoor
                                    for distCoor in playersDist
                                ]
                            ),
                        )

        except:
            logger.info(f"Latency case for entity {self.Hero.networkId}!")

    def handleInteractions(self, event):

        """Handle the right click and the apparition of the pop-up menu to enable interactions between players"""
        mousePosTranslated = [
            coor + (self.Map.renderDistance * self.Map.CHUNK_SIZE) - offset
            for coor, offset in zip(pygame.mouse.get_pos(), self.Hero.blitOffset)
        ]

        self.ContextMenu.checkEvents(event)

        if event.type == MOUSEBUTTONUP and event.button == 1:
            for player in self.players.values():
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
                "CONNECTED PLAYERS", True, (0,0,0)
            )
            heroFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
                f"{self.Hero.name}", True, (0,0,0)
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
                    f"{player.name} - {CLASSES_NAMES[player.classId]} Lv {player._Level}", True, (0,0,0)
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
