import pygame
from pygame.constants import *
from UI.UI_utils_fonc import formatDialogContent
from config.UIConf import *
from UI.UI_utils_text import TextBoxControl


class GameChat:

    """Fusion of the combat log and an input box with networking helpers"""

    def __init__(self, gameController) -> None:

        self.Game = gameController

        # ------------------ TEXTURES ---------- #

        self.surf = pygame.Surface((1024 // 3, 1024 // 4), SRCALPHA)
        self.rect = self.surf.get_rect(bottomleft=(0, self.Game.resolution))

        # ---------------- CHAT ATTR ------------- #

        self.text = []
        self.textSurf = pygame.Surface((self.rect.width, len(self.text) * 20), SRCALPHA)
        self.textRect = self.textSurf.get_rect()

        self.COLORS = {"NEW": (0, 255, 00), "CHAT": (0, 0, 255), "CHAT_2": (255, 0, 0)}

        # --------------------- INPUT ----------------------- #
        self.inputBox = TextBoxControl(
            (100, int(self.rect.height * 0.9)), size=(self.rect.width - 2, 50)
        )
        self.addText("test")

    def updateTextSurf(self):

        self.textSurf = pygame.Surface((self.rect.width, len(self.text) * 20), SRCALPHA)
        self.textRect = self.textSurf.get_rect()

        for i, (text, color) in enumerate(self.text):
            self.textSurf.blit(
                pygame.font.SysFont(BUTTON_FONT_NAME, 12).render(text, True, color),
                (0, i * 20),
            )

        self.textRect.bottom = self.rect.height

    def addText(self, text, actionName="CHAT"):

        textList = []
        textList += formatDialogContent(text, 40)
        fTextList = []
        for text in textList:
            fTextList.append((text, self.COLORS[actionName]))
        self.text += fTextList
        self.updateTextSurf()

    def reset(self):

        self.text = []

    def show(self):

        self.surf.fill((0, 0, 0, 127))
        self.surf.blit(self.textSurf, self.textRect)
        self.inputBox.show(self.surf)
        self.Game.screen.blit(self.surf, self.rect)

    def update(self, event):

        self.inputBox.checkEvent(event)
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