import random

import pygame as pg
from config import HUDConf
from config.HUDConf import *
from config.UIConf import *
from config.UIConf import BUTTON_FONT_NAME, BUTTON_FONT_SIZE
from gameController import GameController
from pygame.constants import MOUSEBUTTONDOWN, QUIT
from UI.textbox import TextBox
from utils.utils import logger

from UI.UI_utils_fonc import blurSurf, formatDialogContent


class Dialog(GameController):
    def __init__(
        self,
        text,
        centerCoor,
        parentSurface,
        color,
        gameController,
        speakerFrame=None,
        charLimit=DEFAULT_CHAR_LIMIT,
        error=False,
    ):

        self.open = False
        self.Game = gameController

        self.textList = formatDialogContent(text, charLimit)
        self.textLen = len(self.textList)
        self.textList[self.textLen - 1] += " (Click to quit)"
        self.index = 0
        self.color = color
        self.centerCoor = centerCoor
        self.errorText = error

        self.parentSurface = parentSurface
        self.fontSurf = pygame.font.Font(
            DUNGEON_FONT, TEXT_FONT_SIZE, bold=self.errorText
        ).render(self.textList[self.index], True, self.color)
        self.rect = self.fontSurf.get_rect(center=(centerCoor[0], centerCoor[1] + 4))
        self.PADDING = [self.rect.width // 2, self.rect.width // 10]

        self.layout = pygame.transform.scale(
            TEXTBOX_LAYOUT,
            (self.rect.width + self.PADDING[0], self.rect.height + self.PADDING[1]),
        )
        self.layoutRect = self.layout.get_rect(center=centerCoor)

        self.nextButton = NEXT_BUTTON
        self.nextButtonRect = self.nextButton.get_rect(
            center=(
                self.layoutRect.width
                - (self.nextButton.get_width() // 2 + self.PADDING[0] // 2),
                self.layoutRect.height // 2,
            )
        )

        self.speakerFrame = speakerFrame
        if speakerFrame != None:
            self.speakerFrame = pygame.transform.scale(
                speakerFrame, (self.Game.resolution, self.Game.resolution)
            )
            self.speakerRect = self.speakerFrame.get_rect(
                center=(self.Game.resolution // 2, self.Game.resolution // 2)
            )
            # self.speakerRect.bottomleft = [
            #     self.speakerRect.bottomleft[0],
            #     self.layoutRect.topleft[1],
            # ]

    def _checkClick(self):

        for event in pygame.event.get():

            if (
                self.rect.collidepoint(pygame.mouse.get_pos())
                and event.type == MOUSEBUTTONDOWN
                and self.textLen > 1
            ):
                if event.button == 1 and self.index != self.textLen - 1:
                    self.index += 1
                    continue

                if event.button == 3 and self.index != 0:
                    self.index -= 1
                    continue

            if self.nextButtonRect.collidepoint(pygame.mouse.get_pos()):
                self.nextButton = NEXT_BUTTON_HOVERED
            else:
                self.nextButton = NEXT_BUTTON

            if (
                self.index == self.textLen - 1
                and self.rect.collidepoint(pygame.mouse.get_pos())
                and event.type == MOUSEBUTTONDOWN
            ):  # last text to displat case, quit at click
                self.open = False
                self.layout.set_alpha(0)
                self.fontSurf.set_alpha(0)
                self.Game.screen.blit(self.bg, (0, 0))

    def mainShow(self):

        self.bg = self.Game.screen.copy()
        self.open = True

        while self.open:

            # Updating surf according to the text
            self.Game.screen.blit(blurSurf(self.bg, 5), (0, 0))

            self._checkClick()

            self.fontSurf = pygame.font.Font(DUNGEON_FONT, TEXT_FONT_SIZE).render(
                self.textList[self.index], True, self.color
            )
            self.rect = self.fontSurf.get_rect(center=self.centerCoor)

            self.layout = pygame.transform.scale(
                TEXTBOX_LAYOUT,
                (self.rect.width + self.PADDING[0], self.rect.height + self.PADDING[1]),
            )
            if self.textLen > 1 or self.index != self.textLen - 1:
                self.layout.blit(self.nextButton, self.nextButtonRect)

            self.layoutRect = self.layout.get_rect(center=self.centerCoor)
            self.nextButtonRect = self.nextButton.get_rect(
                center=(
                    self.layoutRect.width - (self.nextButton.get_width() // 2),
                    self.layoutRect.height // 2,
                )
            )

            if self.speakerFrame != None:
                self.parentSurface.blit(self.speakerFrame, self.speakerRect)

            if self.open:
                self.parentSurface.blit(self.layout, self.layoutRect)
                self.parentSurface.blit(self.fontSurf, self.rect)
                self.Game.show()


# Found on : https://github.com/gunny26/pygame/blob/master/ScrollText.py
# There was not enough time to code a ScrollText, some more important feature needed to be priorized


class ScrollText:
    """Simple 2d Scrolling Text"""

    def __init__(
        self,
        surface,
        text,
        hpos,
        color,
        size=30,
        shaking=False,
        font=BUTTON_FONT_NAME,
        bold=False,
        italic=False,
    ):
        """
        + (pygame.Surface) surface - surface to draw on
        + (string) text - text to draw
        + (int) hpos - horizontal position on y axis
        + (pygame.Color) color - color of font
        + (int) size - size of font
        """
        self.surface = surface
        # prepend and append some blanks
        appendix = " " * (self.surface.get_width() // size)
        self.text = text
        self.hpos = hpos
        self.color = color
        self.size = size
        self.shaking = shaking
        self.italic = italic
        self.bold = bold
        # initialize
        self.position = 0
        self.font = pygame.font.Font(
            DUNGEON_FONT, self.size, italic=self.italic, bold=self.bold
        )
        self.text_surface = self.font.render(self.text, True, self.color)

    def update(self):
        """update every frame"""
        self.surface.fill((*self.color, 0))
        if self.shaking:
            self.hpos = random.randint(1, self.size // 2)
        self.surface.blit(
            self.text_surface,
            (0, self.hpos),
            (self.position, 0, self.surface.get_width(), self.size),
        )
        if self.position <= self.text_surface.get_width():
            self.position += 1
        else:
            self.position = -self.surface.get_width()


class InfoTip:
    """
    An info bubble made to give information about the element the cursor is on.
    """

    def __init__(self, text, gameController, color=(255, 255, 255)) -> None:

        self.Game = gameController
        self.color = color

        self.PADDING = 5

        self.text = text
        self.open = False

    def setText(self, newText):

        self.text = newText

    def show(self):

        # If the text is too long, make it scrollable
        scrolledText = None
        self.open = True
        lineLength = 0
        linesLayout = None

        if len(self.text) > DEFAULT_CHAR_LIMIT:
            scrolledText = ScrollText(self.descSurf, self.text, 0, self.color)

        mousePos = pygame.mouse.get_pos()

        self.descSurf = pygame.Surface(
            [
                coor + self.PADDING
                for coor in pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE)
                .render(self.text, True, self.color)
                .get_size()
            ],
            pygame.SRCALPHA,
        )

        self.descSurf.fill((*self.color, 0))  # Clean the descSurf

        if scrolledText != None:
            scrolledText.update()

            lineLength = scrolledText.text_surface.get_width()
            linesLayout = infoTipLines(
                mousePos,
                "right" if mousePos[0] > self.Game.resolution // 2 else "left",
                lineLength + self.PADDING,
            )

        else:
            fontSurf = pygame.font.Font(DUNGEON_FONT, INFOTIP_DESC_FONT_SIZE).render(
                self.text, True, self.color
            )

            lineLength = fontSurf.get_width() + self.PADDING
            linesLayout = infoTipLines(
                mousePos,
                "right" if mousePos[0] > self.Game.resolution // 2 else "left",
                lineLength + self.PADDING,
            )

            self.descSurfRect = self.descSurf.get_rect(
                center=(
                    (linesLayout[1][0] + linesLayout[2][0]) // 2,
                    linesLayout[1][1]
                    - (self.descSurf.get_height() // 2 + self.PADDING),
                )
            )
            self.descSurf.blit(
                fontSurf,
                fontSurf.get_rect(
                    center=[coor // 2 for coor in self.descSurfRect.size]
                ),
            )

        pygame.draw.lines(self.Game.screen, self.color, False, linesLayout, width=3)
        if not self.Game.screen.get_locked():
            self.Game.screen.blit(self.descSurf, self.descSurfRect)


class SelectPopUp:
    """
    Ui component to display some choices to make on a popup, choosed with a click from the player.
    The choices are made with the following pattern :
    choices = {
        <name>: <action>,
        "choice number 1": doSomething // or lambda: doSomething()
    }
    with "action" value being a function
    """

    def __init__(self, choices, parentSurf, gameController, centerCoor, text="") -> None:

        assert len(choices) != 0, logger.error(
            "Choices must be passed in the select pop up !"
        )
        self.Game = gameController

        self.choices = {f"> {choice}": choices[choice] for choice in choices}
        self.open = False
        self.centerCoor = centerCoor
        self.hovered = [False for elt in self.choices]
        self.text = text

        # --------------- FONTS ------------- #

        self.fonts = [
            pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
                choice, True, (255, 255, 255) if self.hovered else (100, 100, 100)
            )
            for choice in self.choices.keys()
        ]
        self.textFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE + 10).render(
                self.text, True, (0, 0, 0)
            )

        # --------- TEXTURES ---------- #

        maxSurfWidth = max([surf.get_width() for surf in self.fonts]) + self.textFont.get_width()
        totalHeight = sum([surf.get_height() for surf in self.fonts]) + self.textFont.get_height()*2

        self.parentSurf = parentSurf
        self.blank_surf = pygame.transform.scale(
            HUDConf.NAME_SLOT,
            (int(maxSurfWidth * 1.2), int(totalHeight * 2)),
        )
        self.surf = self.blank_surf.copy()

        self.rect = self.surf.get_rect(center=self.centerCoor)
        self.PADDING = totalHeight // len(self.choices)
        self.initPoint = [
            self.rect.width // 2,
            self.rect.height // (len(self.choices) + 1) + int(self.textFont.get_height()*0.75),
        ]

        self.fontRects = [
            font.get_rect(
                center=(self.initPoint[0], self.initPoint[1] + (i * self.PADDING))
            )
            for i, font in enumerate(self.fonts)
        ]

    def checkActions(self):

        mousePosTranslated = [
            coor - offset
            for coor, offset in zip(pygame.mouse.get_pos(), self.rect.topleft)
        ]

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                exit()

            for (i, fontRect), choiceName in zip(
                enumerate(self.fontRects), self.choices.keys()
            ):
                if fontRect.collidepoint(mousePosTranslated):
                    self.hovered[i] = True

                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        self.choices[choiceName]()
                        self.open = False
                else:
                    self.hovered[i] = False

    def show(self):

        self.open = True
        self.bg = self.Game.screen.copy()

        while self.open:

            self.Game.screen.blit(blurSurf(self.bg, 5), (0, 0))
            self.checkActions()

            self.fonts = [
                pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
                    choice, True, (255, 255, 255)
                )
                if not self.hovered[i]
                else pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE, bold=True).render(
                    choice, True, (255, 0, 0)
                )
                for i, choice in enumerate(self.choices.keys())
            ]
            self.fontRects = [
                font.get_rect(
                    center=(self.initPoint[0], self.initPoint[1] + ((i+1) * self.PADDING))
                )
                for i, font in enumerate(self.fonts)
            ]

            if self.open:
                # ------------ BLITING ----------------- #
                self.surf = self.blank_surf.copy()
                if self.text != "":
                    self.surf.blit(self.textFont, self.textFont.get_rect(center=(self.initPoint)))

                for i in range(len(self.choices)):

                    self.surf.blit(self.fonts[i], self.fontRects[i])

                self.parentSurf.blit(self.surf, self.rect)
                self.Game.show()


KEY_REPEAT_SETTING = (200, 70)
MAX_LEN_NAME = 10


class TextBoxControl(object):
    def __init__(self, centerCoor, size=(200,50)):
        self.input = TextBox(
            pygame.Surface(size).get_rect(center=centerCoor),
            command=self.changeName,
            clear_on_enter=True,
            inactive_on_enter=False,
        )
        self.color = (100, 100, 100)
        pg.key.set_repeat(*KEY_REPEAT_SETTING)
        self.name = ""

    def checkEvent(self, event):
        self.input.get_event(event)
 
    def changeName(self, name):
        self.name = ("").join(name)

    def show(self, surface):
        self.input.update()
        self.input.draw(surface)

    def reset(self):
        self.input.buffer = []
        self.name = ""
