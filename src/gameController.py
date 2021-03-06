import math
import pickle
from HUD.chatbox import ChatBox
import time

import pygame
from pygame.locals import *

from assets.animation import *
from config.mapConf import *
from config.UIConf import *
from config.defaultConf import *
from UI.Cursor import Cursor
from utils.MusicController import MusicController


class GameController:
    def __init__(self):

        self.states = [
            "mainMenu",
            "selectGame",
            "openWorld",
            "mainMenu_options",
            "loadingNewGame",
            "loading",
            "quit",
            "pause",
            "fight",
            "building",
        ]
        self.currentState = "loadingNewGame"
        self.id = 0  # Depends of the save, 0 = new game, 1 to 3 are ids to the game
        self.heroesGroup = []
        self.heroIndex = 0

        # Pygame General Setting
        self.WINDOW_SIZE = WINDOW_SIZE
        self.MAX_RESOLUTION = MAX_RESOLUTION
        self.MAX_RENDER_DISTANCE = MAX_RENDER_DISTANCE
        self.MAX_REFRESH_RATE = MAX_REFRESH_RATE
        self.WINDOW = pygame.display.set_mode(self.WINDOW_SIZE) #NOFRAME)

        self.enableSound = 0
        self.debug_mode = 1
        self.refresh_rate = 60
        self.resolution = min(self.WINDOW_SIZE)
        self.resolutionFactor = self.resolution / min(self.WINDOW_SIZE)
        self.screen = pygame.Surface((self.resolution, self.resolution))
        self.transitionFlag = False
        self.changesMadeChecker = {
            0: False,  # Main Menu
            1: False,  # Option Menu
            2: False,  # Select Menu
            3: False,  # Pause Menu
        }  # Flag to sync all the classes and re init them if needed due to change of game attributes (mainly resolution)

        pygame.display.set_caption(f"Pyhm World")

        self.difficultyModes = ["EASY", "MEDIUM", "HARD", "LEGENDARY"]
        self.difficultyId = 1
        self.difficulty = self.difficultyModes[self.difficultyId]

        self.KeyBindings = {
            "Move": {
                "value": None,  # if value set to None: bind not modifiable
                "key": "Right Click",
            },
            "Sell/Buy Items on the Seller Store": {
                "value": None,  # if value set to None: bind not modifiable
                "key": "Right Click",
            },
            "Toggle Inventory": {"value": pygame.K_i, "key": "I"},
            "Toggle Minimap": {"value": pygame.K_m, "key": "M"},
            "Toggle Spell Book": {"value": pygame.K_k, "key": "K"},
            "Pause the game": {"value": pygame.K_ESCAPE, "key": "ESC"},
            "Interact with an element": {"value": pygame.K_e, "key": "E"},
            "Pick up items": {"value": pygame.K_e, "key": "E"},
            "Open quest's Journal": {"value": pygame.K_j, "key": "J"},
            "Switch heroes": {"value": pygame.K_TAB, "key": "TAB"},
            "Cancel trade": {"value": pygame.K_ESCAPE, "key": "ESC"},
            "Center the Map's view": {"value": pygame.K_r, "key": "R"},
            "Show the connected player (Online mode only)": {"value": pygame.K_c, "key": "C"},
        }

        self.cursor = Cursor(self)
        self.musicController = MusicController(self)
        # self.musicController.setMusic("menu")

        # ------ FIGHT ---------- #
        self.combatLog = None
        self.fightMode = None

        self.chat_box = ChatBox(self)

        # ---------- NETWORK ------------ #

        self.NetworkController = None
        self.isOnline = False

    def selectGame(self):
        self.currentState = "selectGame"

    def loadNewGame(self):
        self.currentState = "loadingNewGame"

    def loadGame(self, id):
        self.currentState = "loading"
        self.id = id

    def goToOpenWorld(self):
        self.currentState = "openWorld"
        self.transitionFlag = True

    def enterBuilding(self):

        self.currentState = "building"
        self.transitionFlag = True

    def backToMainMenu(self):
        self.currentState = "mainMenu"

    def showOptions(self):
        self.currentState = "mainMenu_options"

    def quitGame(self):
        self.currentState = "quit"

    def pauseGame(self):
        self.currentState = "pause"

    def backToGame(self):
        self.currentState = "openWorld"

    def startFight(self):
        self.currentState = "fight"

    def increaseDifficulty(self):
        self.difficultyId = (
            self.difficultyId + 1
            if self.difficultyId != len(self.difficultyModes) - 1
            else self.difficultyId
        )
        self.difficulty = self.difficultyModes[self.difficultyId]

    def decreaseDifficulty(self):
        self.difficultyId = self.difficultyId - 1 if self.difficultyId != 0 else 0
        self.difficulty = self.difficultyModes[self.difficultyId]

    def show(self, combatMode=False):
        """Method called to take into account the resolution"""

        self.cursor.mainLoop()

        if combatMode:
            self.combatLog.show()

        self.WINDOW.blit(
            pygame.transform.scale(self.screen, self.WINDOW_SIZE),
            (0, 0),
        )
        pygame.display.flip()

    def spaceTransition(self, spaceName):

        """
        Method showing when a transition is made between spaces, like when entering a building
        """

        if self.transitionFlag:

            initAlpha = 0
            spaceFont = pygame.font.Font(DUNGEON_FONT, TITLE_FONT_SIZE).render(
                spaceName, True, (0, 0, 0)
            )
            layout = pygame.transform.scale(
                TEXTBOX_LAYOUT,
                (int(spaceFont.get_width() * 1.2), int(spaceFont.get_height() * 1.2)),
            )
            layoutRect = layout.get_rect(
                center=(self.resolution // 2, self.resolution // 4)
            )
            spaceRect = spaceFont.get_rect(
                center=[coor // 2 for coor in layoutRect.size]
            )
            layout.blit(spaceFont, spaceRect)

            start = time.time()
            layout.set_alpha(initAlpha)

            if spaceName == "Pyhm World":
                self.musicController.setMusic("openWorld")
            for Hero in self.heroesGroup:
                Hero.currentPlace = self.currentState
                if Hero.currentPlace == "building":
                    if self.isOnline:
                        self.heroesGroup[0].Map.transmitPosInfos()
            while (time.time() - start) < WORLD_TRANS_TIME:

                initAlpha += math.ceil(WORLD_TRANS_ALPHA_SEC / self.refresh_rate)
                layout.set_alpha(initAlpha)

                self.screen.blit(layout, layoutRect)
                self.show()

            self.transitionFlag = False
            self.cursor.set("main")

    # def __getstate__(self):
    #     state = self.__dict__.copy()
    #     screen = state.pop("screen")
    #     WINDOW = state.pop("WINDOW")
    #     state["screen_string"] = (
    #         pygame.image.tostring(screen, "RGB"),
    #         screen.get_size(),
    #     )
    #     state["WINDOW_string"] = (
    #         pygame.image.tostring(WINDOW, "RGB"),
    #         screen.get_size(),
    #     )
    #     return state

    # def __setstate__(self, state):
    #     screen_string, screenSize = state.pop("screen_string")
    #     WINDOW_string, windowSize = state.pop("WINDOW_string")
    #     state["screen"] = pygame.image.fromstring(screen_string, screenSize, "RGB")
    #     state["WINDOW"] = pygame.image.fromstring(WINDOW_string, windowSize, "RGB")
    #     self.__dict__.update(state)


if __name__ == "__main__":

    g = GameController()
    b = pickle.dumps(g)
    t = pickle.loads(b)
