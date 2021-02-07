from math import sqrt
import pygame

from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP
from Player.Character import Character
from utils.utils import logger
import uuid


class NetworkController:
    def __init__(self, gameController, Map, Hero, ContextMenu) -> None:

        self.Game = gameController
        self.Map = Map
        self.Hero = Hero
        self.ContextMenu = ContextMenu

        self.players = {}
        self.monsters = []

    def addPlayer(self, name):
        """Create a Character Instance based of the informations given by the connexion of a player"""

        createdId = uuid.uuid4()
        logger.info(f"{name} (#{createdId}) connected to the server !")
        createdCharacter = Character(self.Game, self.Map)
        createdCharacter.initHUD()

        self.players.update({createdId: createdCharacter})

    def createTestConnection(self):
        self.addPlayer("Test Player 1")

    def showConnectedPlayers(self):

        for player in self.players.values():

            # Check wether the player and the other connected are on the same chunk or not
            if (
                sqrt(
                    sum(
                        [
                            (p1coor - p2coor) ** 2
                            for p1coor, p2coor in zip(
                                player.Map.chunkData["currentChunkPos"],
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
