import pygame
from config.UIConf import *


class Cursor:
    def __init__(self, parentSurface) -> None:

        self.state = "main"
        self.parentSurface = parentSurface
        self.showFlag = True

        self.show()

    def mainLoop(self):

        if self.showFlag:
            self.parentSurface.screen.blit(
                CURSORS_SURF[self.state], (pygame.mouse.get_pos())
            )

    def hide(self):
        self.showFlag = False
        pygame.mouse.set_visible(True)

    def show(self):
        self.showFlag = True
        pygame.mouse.set_visible(False)

    def set(self, state="main"):
        """[summary]

        Args:
            + state (str, optional): Can be either "main" or "interact" . Defaults to "main".
        """
        self.state = state
