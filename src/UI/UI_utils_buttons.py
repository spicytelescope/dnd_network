from pygame import *
from pygame.constants import MOUSEBUTTONDOWN
from pygame.locals import *
from config.menuConf import *
from config.UIConf import *
from gameController import *
import math

class Button():

    def __init__(self, blitPointX, blitPointY, textConfig, clickable=True, action=None, surf=None):
        """A button can be in 2 states :
        - default (not selected)
        - hovered (cursor on but not clicked), can be desactivated if clickable option set to False

        Blit a text with the textConfig parameters on blitPointX and blitPointY on a surface.
        textConfig parameters scheme : [text, font, color, size]
        You can override the default button surf with the surf parameter.

        If you do not want to display any text, just an empty button, set the text parameter to an empty string
        """

        # ----------- INIT --------------- #

        self.action = action
        self.x = blitPointX
        self.y = blitPointY
        self.clickable = clickable
        self.text = textConfig[0]
        self.font = textConfig[1]
        self.color = textConfig[2]
        self.fontSize = textConfig[3]

        # ------------ DISPLAY ------------- #

        self.surf = surf if surf != None else BUTTON_SURFS[0] # Initial state : not clicked
        self.rect = self.surf.get_rect(center=(self.x, self.y))

        # assert self.fontSize < self.surf.get_height(
        # ), f"<ERROR> : the font is too large for the button img"

    def blit(self, surface):
        """Blit the button on the surface at self.x and self.y coordonates"""

        if self.text != "":

            fontToBlit = pygame.font.Font(DUNGEON_FONT, self.fontSize)
            fontSurf = fontToBlit.render(self.text, True, self.color)

            # creating a temporary surface resulting of the button surf + the font surf
            finalSurf = pygame.transform.scale(self.surf.copy(), (int(fontSurf.get_width(
            )*1.2+BUTTON_PADDING[0]), int(fontSurf.get_height()+BUTTON_PADDING[1])))
            self.rect = finalSurf.get_rect(center=(self.x, self.y))

            # We choose a rect such as the center is on the center of the button surf, to center the text within it
            fontRect = fontSurf.get_rect(
                center=(finalSurf.get_width()//2, finalSurf.get_height()//2))

            # scaleSurfCoor = [int(coor*self.resolutionFactor) for coor in finalSurf.get_size()]
            finalSurf.blit(fontSurf, fontRect)
            surface.blit(finalSurf, self.rect)

        else:
            surface.blit(self.surf, self.rect)


class Select():

    def __init__(self, blitPointX, blitPointY, direction, clickable=True, action=None):

        super().__init__()

        # ----------- INIT --------------- #

        self.action = action
        self.x = blitPointX
        self.y = blitPointY
        self.clickable = clickable
        self.direction = direction

        # ------------ DISPLAY ------------- #

        self.surf = SELECT_BUTTONS[0] if self.direction == "left" else SELECT_BUTTONS[1]
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    def blit(self, surface):

        surface.blit(self.surf, self.rect)


class UpButton():

    def __init__(self, blitPointX, blitPointY, direction, clickable=True, action=None):

        super().__init__()

        # ----------- INIT --------------- #

        self.action = action
        self.x = blitPointX
        self.y = blitPointY
        self.clickable = clickable
        self.direction = direction

        # ------------ DISPLAY ------------- #

        self.surf = UP_BUTTONS[0] if self.direction == "down" else UP_BUTTONS[1]
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    def blit(self, surface):

        surface.blit(self.surf, self.rect)
