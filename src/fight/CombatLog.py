import pygame
from pygame import color
from pygame.constants import *
from UI.UI_utils_fonc import formatDialogContent
from config.UIConf import *


class CombatLog():
    def __init__(self, gameController) -> None:

        self.Game = gameController

        # ------------------ TEXTURES ---------- #

        self.surf = pygame.Surface((1024 // 3, 1024 // 4), SRCALPHA)
        self.rect = self.surf.get_rect(topright=(1024, 0))

        # ---------------- FIGHT ATTR ------------- #

        self.turn = 0
        self.text = []
        self.textSurf = None
        self.textRect = None

        self.COLORS = {"TURN": (0, 255, 00), "SPELL": (0, 0, 255), "DMG": (255, 0, 0)}

        self.addTurn()

    def updateTextSurf(self):

        self.textSurf = pygame.Surface((self.rect.width, len(self.text) * 20), SRCALPHA)
        self.textRect = self.textSurf.get_rect()

        for i, (text, color) in enumerate(self.text):
            self.textSurf.blit(
                pygame.font.SysFont(BUTTON_FONT_NAME, 12).render(text, True, color),
                (0, i * 20),
            )

        self.textRect.bottom = self.rect.height

    def addTurn(self):

        self.turn += 1
        self.text += [
            (
                f"================== TURN N°{self.turn} ======================",
                self.COLORS["TURN"],
            )
        ]
        self.updateTextSurf()

    def rollDice(self, dValue, actionName="DMG"):
        """
        Args:
            + dValue (int): [description]
            + actionName (str): can be either "DMG" or "SPELL"
        """

        self.text += [(f"Rolling a d{dValue} ...", self.COLORS[actionName])]
        self.updateTextSurf()

    def addText(self, text, actionName="DMG"):

        textList = []
        textList += formatDialogContent(text, 40)
        fTextList = []
        for text in textList:
            fTextList.append((text, self.COLORS[actionName]))
        self.text += fTextList
        self.updateTextSurf()

    def reset(self):

        self.text = []
        logger.info("Reseting combat log !")

    def show(self):
        self.surf.fill((0, 0, 0, 127))
        self.surf.blit(self.textSurf, self.textRect)
        self.Game.screen.blit(self.surf, self.rect)

    def update(self, event):

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # if event.type == KEYDOWN:
        #     if event.key == K_SPACE:
        #         self.addTurn()
        #     if event.key == K_t:
        #         self.addText(str(input("Enter your action : ")))

        if event.type == MOUSEBUTTONDOWN:

            if event.button == 4 and self.textRect.top <= 0:
                self.textRect.topleft = [
                    self.textRect.topleft[0],
                    self.textRect.topleft[1] + 5,
                ]

            if event.button == 5 and self.textRect.bottom >= self.rect.height:
                self.textRect.topleft = [
                    self.textRect.topleft[0],
                    self.textRect.topleft[1] - 5,
                ]