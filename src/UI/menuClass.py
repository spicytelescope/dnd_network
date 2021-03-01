from UI.UI_utils_text import Dialog, SelectPopUp, TextBoxControl
import os
import platform
import random
from tkinter import Button as tkButton, Canvas, Scrollbar
from tkinter import (
    Checkbutton,
    Frame,
    IntVar,
    Label,
    Scale,
    Spinbox,
    StringVar,
    Tk,
    messagebox,
)
from tkinter.constants import BOTTOM, CENTER, HORIZONTAL, NSEW, RIGHT, Y

from pygame.mouse import *
from pygame.event import *
from pygame.constants import *
from config import HUDConf, playerConf
from config import menuConf
from config.eventConf import CHARAC_SELECT_ANIM_EVENT_ID
from config.mapConf import *
from config.menuConf import *
from config.playerConf import *
from config.UIConf import *

from utils.utils import logger, openDoc

from UI.UI_utils_buttons import *
import time
import string


class MainMenu:
    def __init__(self, GameController, Map):

        self.Game = GameController
        self.Map = Map
        self.Id = 0

        # ---------- BUTTONS  -------- #

        self.buttonNames = MAIN_BUTTONS_NAMES

        self.calculatesPositionning()

        # Adding at first doc and version buttons
        self.defaultButtons = [
            Button(
                self.Game.resolution * 0.15,
                self.Game.resolution * 0.95,
                ("v1.0.0", "dejavusansmono", (255, 255, 255), BUTTON_FONT_SIZE),
                False,
            ),
            Button(
                self.Game.resolution * 0.85,
                self.Game.resolution * 0.95,
                ("Documentation", "dejavusansmono", (255, 255, 255), BUTTON_FONT_SIZE),
                # action=lambda: openDoc(),
            ),
        ]
        self.mainbuttons = [
            Button(
                self.initButtonPos[0],
                self.initButtonPos[1] + (i * self.buttonSpacing),
                (
                    self.buttonNames[i],
                    BUTTON_FONT_NAME,
                    (255, 255, 255),
                    BUTTON_FONT_SIZE,
                ),
            )
            for i in range(len(self.buttonNames))
        ]

        self.buttons = self.mainbuttons + self.defaultButtons
        self.selecters = []
        self.upButtons = []

        # --------- MENU ACTIONS ----------------- #

        self.buttons[0].action = self.Game.selectGame
        self.buttons[1].action = self.Game.showOptions
        self.buttons[2].action = self.Game.quitGame

    def resetChanges(self):
        self.Game.changesMadeChecker[self.Id] = False

    def calculatesPositionning(self):
        # self.Game.resolution*0.54 is relative to the background (ratio for good rendering)
        self.initButtonPos = [
            self.Game.resolution // 2,
            int(self.Game.resolution * 0.54),
        ]
        # we use len(MENU_BUTTONS)+1 as we need some space around the buttons, so the +1 is needed to get smaller spacing
        self.buttonSpacing = (self.Game.resolution - self.initButtonPos[1]) // (
            len(self.buttonNames) + 1
        )

    def checkActions(self):
        for event in pygame.event.get():
            mousePos = pygame.mouse.get_pos()
            # We need to scale down the mouse to get on with the real
            mousePos = [i * self.Game.resolutionFactor for i in mousePos]

            for button in self.buttons:
                if button.clickable and button.rect.collidepoint(mousePos):
                    if button in self.upButtons:
                        button.surf = (
                            UP_BUTTONS[3] if button.direction == "up" else UP_BUTTONS[2]
                        )

                    elif button in self.selecters:
                        button.surf = (
                            SELECT_BUTTONS[3]
                            if button.direction == "right"
                            else SELECT_BUTTONS[2]
                        )

                    else:
                        button.surf = BUTTON_SURFS[1]

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button.action != None:
                            button.action()
                else:
                    if button in self.upButtons:
                        button.surf = (
                            UP_BUTTONS[1] if button.direction == "up" else UP_BUTTONS[0]
                        )

                    elif button in self.selecters:
                        button.surf = (
                            SELECT_BUTTONS[1]
                            if button.direction == "right"
                            else SELECT_BUTTONS[0]
                        )

                    else:
                        button.surf = BUTTON_SURFS[0]

            if self.Id == 2:
                if event.type == CHARAC_SELECT_ANIM_EVENT_ID:
                    self.updateAnimation()
                self.textBox.checkEvent(event)

            if self.Id == 3 and (
                event.type == pygame.KEYDOWN
                and event.key == self.Game.KeyBindings["Pause the game"]["value"]
            ):
                self.open = False

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def show(self):

        # for indicator in self.Game.changesMadeChecker.items():
        #     # indicator[0] is the id and indicator[1] is the flag to mark that changes has been made
        #     if indicator[0] == self.Id and indicator[1]:
        #         self.__init__(self.Game, self.Map) if self.Id not in [
        #             1,
        #             2,
        #             3,
        #         ] else self.__init__(
        #             self.Game, self.Map, self.HeroesGroup
        #         ) if self.Id != 3 else self.__init__(
        #             self.Game, self.Map, self.Hero, self.saveController
        #         )
        #         self.resetChanges()

        # Reseting surfaces
        if self.Id != 3:

            self.mainSurface = pygame.transform.scale(
                menuConf.MAIN_BACKGROUND, (self.Game.resolution, self.Game.resolution)
            ).copy()

        if self.Id == 2 and self.stepsCursor == 1:
            self.mainSurface.blit(self.charImage, self.charImageRect)
            fontText = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE + 20).render(
                f"Choose the class for champion number {self.HeroIndex+1}",
                True,
                (0, 0, 0),
            )
            layout = pygame.transform.scale(
                menuConf.SCROLL,
                (int(fontText.get_width() * 1.25), int(fontText.get_height() * 1.5)),
            )
            layout.blit(
                fontText,
                fontText.get_rect(
                    center=(layout.get_width() // 2, layout.get_height() // 2)
                ),
            )
            self.mainSurface.blit(
                layout,
                layout.get_rect(
                    center=(self.Game.resolution // 2, int(self.Game.resolution // 2))
                ),
            )
            self.textBox.show(self.mainSurface)

        if self.Id == 3:
            # rescale it to the right
            self.mainSurface = pygame.transform.scale(
                self.mainSurface, (self.Game.resolution, self.Game.resolution)
            ).copy()
            self.mainSurface.blit(self.menuSurface, self.menuRect)
        for button in self.buttons:
            button.blit(self.mainSurface)

        self.Game.screen.blit(self.mainSurface, (0, 0))
        self.Game.show()

    # def __getstate__(self):

    #     state = self.__dict__.copy()
    #     for attrName in ["defaultButtons", "mainbuttons", "buttons"]:
    #         state.pop(attrName)

    #     return state


class OptionMenu(MainMenu):
    def __init__(self, GameController, Map, HeroesGroup):

        super().__init__(GameController, Map)
        self.Id = 1
        self.heroesGroup = HeroesGroup

        # --------------------------- BUTTONS  ------------------------- #

        self.buttonNames = OPTION_BUTTONS_NAMES

        self.optionButtons = [
            Button(
                self.initButtonPos[0],
                self.initButtonPos[1] + (i * self.buttonSpacing),
                (
                    self.buttonNames[i],
                    BUTTON_FONT_NAME,
                    (255, 255, 255),
                    BUTTON_FONT_SIZE,
                ),
            )
            for i in range(len(self.buttonNames))
        ]

        self.buttons = self.optionButtons + self.defaultButtons

        # --------- MENU ACTIONS ----------------- #

        self.buttons[0].action = self.showVideoSettings
        self.buttons[1].action = self.showControlSettings
        self.buttons[2].action = self.Game.backToMainMenu

    def showVideoSettings(self):

        # ---------------------- MENU GUI SETTINGS ----------------- #
        self.root = Tk(className="Video settings")
        self.root.minsize(MIN_SIZE_FRAME[0], MIN_SIZE_FRAME[1])
        self.root.geometry(f"{MIN_SIZE_FRAME[0]}x{MIN_SIZE_FRAME[1]}")

        self.widgetFrame = Frame(self.root)

        # ---------------------- VIDEO WIDGETTS -------------------- #

        self.selectedResolution = StringVar(self.root)
        self.selectedRefreshRate = IntVar(self.root, self.Game.refresh_rate)
        self.selectedRenderDistance = IntVar(self.root, self.Map.renderDistance)
        self.enableWaterAnimation = IntVar(self.root, self.Map.enableWaterAnimation)
        self.selectedLDO = IntVar(self.root, self.Map.lod)
        self.enableDebugMode = IntVar(self.root, self.Game.debug_mode)
        self.enableSound = IntVar(self.root, self.Game.enableSound)

        self.videoWidgets = [
            # Spinbox(
            #     self.widgetFrame,
            #     justify=CENTER,
            #     values=[
            #         f"{i}x{i}" for i in range(512, self.Game.MAX_RESOLUTION + 1, 32 * 2)
            #     ],
            #     textvariable=self.selectedResolution,
            #     validate="key",
            # ),
            Scale(
                self.widgetFrame,
                from_=1,
                to=self.Game.MAX_REFRESH_RATE,
                orient=HORIZONTAL,
                variable=self.selectedRefreshRate,
            ),
            Scale(
                self.widgetFrame,
                from_=1,
                to=MAX_RENDER_DISTANCE,
                orient=HORIZONTAL,
                variable=self.selectedRenderDistance,
            ),
            # Scale(
            #     self.widgetFrame,
            #     from_=0,
            #     to=self.Map.MAX_LDO,
            #     resolution=1,
            #     orient=HORIZONTAL,
            #     variable=self.selectedLDO,
            # ),
            Checkbutton(self.widgetFrame, variable=self.enableWaterAnimation),
            Checkbutton(self.widgetFrame, variable=self.enableDebugMode),
            Checkbutton(self.widgetFrame, variable=self.enableSound),
        ]

        # To get the intial resolution, need to be set up AFTER widget creation
        self.selectedResolution.set(f"{self.Game.resolution}x{self.Game.resolution}")

        # -------------------------   BLITTING WIDGETS  ---------------------- #

        # Displaying widgets/labels
        for i, elt in enumerate(OPTION_LABELS):
            Label(self.widgetFrame, text=elt).grid(column=0, row=i)
            self.videoWidgets[i].grid(column=1, row=i)
        tkButton(
            self.root, text="Save changes", command=self.applyVideoSettingsChanges
        ).pack(side=BOTTOM)

        self.widgetFrame.pack()
        self.root.mainloop()

    def applyVideoSettingsChanges(self):

        if messagebox.askokcancel(
            "Change Warning",
            f"{'WARNING - THE MAP MAY NEED TO BE REGENERATED !' if self.Id == 3 else ''} Confirm changes ?",
        ):

            # Changing GameController Settings
            self.Game.resolution = int(self.selectedResolution.get().split("x")[0])
            self.Game.refresh_rate = self.selectedRefreshRate.get()

            self.Game.screen = pygame.Surface(
                (self.Game.resolution, self.Game.resolution)
            )
            self.Game.resolutionFactor = self.Game.resolution / min(
                self.Game.WINDOW_SIZE
            )
            self.Game.debug_mode = self.enableDebugMode.get()

            # Changing Map Settings

            self.Map.renderDistance = self.selectedRenderDistance.get()
            self.Map.maxChunkGen = (self.Map.renderDistance + 2) ** 2
            self.Map.enableWaterAnimation = self.enableWaterAnimation.get()

            # Changing Hero Settings

            for Hero in self.heroesGroup:
                Hero.charRect = Hero.imageState["image"].get_rect(
                    center=(self.Game.resolution // 2, self.Game.resolution // 2)
                )

            # Music
            self.Game.enableSound = self.enableSound.get()
            if self.Game.enableSound:
                self.Game.musicController.mainChannel.set_volume(0.3)
            elif self.Game.enableSound == 0:
                self.Game.musicController.mainChannel.set_volume(0)

            # if (
            #     self.Id == 3 or self.Id == 1
            # ) and self.Map.lod != self.selectedLDO.get():

            #     # the step generation is the opposite of the level of detail
            #     # the higher the level of detail, the lower the step generation is
            #     self.Map.lod = self.selectedLDO.get()
            #     self.Map.stepGeneration = int(2 ** (self.Map.MAX_LDO - self.Map.lod))
            #     PLAYER_CONFIG["STEP_GENERATION"] = int(
            #         2 ** (self.Map.MAX_LDO - self.Map.lod)
            #     )
            #     PLAYER_CONFIG["LOD"] = self.Map.lod

            #     self.Map.resetChunks()
            #     if self.Id == 3:  # We only re generate on the pause menu
            #         self.Map.generateMainChunk(self.Map.maxChunkGen)

            messagebox.showinfo("Video Settings", "Changes applied !")

            self.root.destroy()

            # Reseting the menu classes to handle changes
            for i in range(len(self.Game.changesMadeChecker.keys())):
                # WARNING : changesMade is a dict behaving as an array !
                self.Game.changesMadeChecker[i] = True

    def showControlSettings(self):

        # ---------------------- MENU GUI SETTINGS ----------------- #

        self.root = Tk(className="Control settings")
        self.root.minsize(MIN_SIZE_FRAME[0], MIN_SIZE_FRAME[1])
        self.root.geometry(f"{MIN_SIZE_FRAME[0]}x{MIN_SIZE_FRAME[1]}")

        # bg_image = PhotoImage("./assets/menus/wood_background.png")
        # canvas = Canvas(
        #     self.root, width=MIN_SIZE_FRAME[0], height=MIN_SIZE_FRAME[1])
        # canvas.create_image(0,0,anchor=NW, image=bg_image)
        # canvas.pack()

        # ------------------ VARIABLES ---------------- #

        bindVarNames = [
            StringVar(self.root, bind["key"]) for bind in self.Game.KeyBindings.values()
        ]

        # ------- CONTROL WIDGETS -------------- #

        self.selectedIndexBind = None

        def keydown(e):

            if self.selectedIndexBind != None:

                bindVarNames[self.selectedIndexBind].set(e.char.upper())
                for i, bindDesc in enumerate(self.Game.KeyBindings.keys()):
                    if self.Game.KeyBindings[bindDesc]["value"] == None:
                        continue

                    self.controlWidgets[i]["state"] = "normal"

                self.selectedIndexBind = None

        def changeBind(bindIndex):
            self.selectedIndexBind = bindIndex
            for i in range(len(self.controlWidgets)):
                self.controlWidgets[i]["state"] = "disabled"

        self.widgetFrame = Frame(self.root)
        self.widgetFrame.bind("<KeyPress>", keydown)
        self.widgetFrame.focus_set()

        def ext_func(i):
            def inner_func():
                changeBind(i)

            return inner_func

        self.controlWidgets = [
            tkButton(
                self.widgetFrame,
                anchor="center",
                textvariable=bindVarNames[k],
                command=ext_func(k),
                state=f"{'disabled' if self.Game.KeyBindings[bindDesc]['value'] == None else 'normal'}",
            )
            for k, bindDesc in enumerate(self.Game.KeyBindings.keys())
        ]

        for i, bindDesc in enumerate(self.Game.KeyBindings.keys()):

            Label(self.widgetFrame, text=bindDesc).grid(column=0, row=i)
            self.controlWidgets[i].grid(column=1, row=i)

        Label(
            self.root, text="Only litteral keys (a-z) will be bind.", bd=2, fg="#ff0000"
        ).pack(side=BOTTOM, anchor=CENTER)

        # vsb = Scrollbar(self.widgetFrame, orient="vertical", command=canvas.yview)
        # vsb.grid(row=0, column=1, sticky='ns')
        # canvas.configure(yscrollcommand=vsb.set)

        tkButton(
            self.root,
            text="Save changes",
            command=lambda: self.applyControlSettingsChanges(bindVarNames),
        ).pack(side=BOTTOM)

        self.widgetFrame.pack()
        self.root.mainloop()

    def applyControlSettingsChanges(self, bindVarNames):

        if messagebox.askokcancel(
            "Change Warning",
            "Confirm changes ?",
        ):
            for i, var in enumerate(bindVarNames):
                if (
                    list(self.Game.KeyBindings.values())[i]["value"] != None
                    and var.get().lower() in string.ascii_lowercase
                ):
                    logger.debug(f"value : {var.get().lower()}")
                    list(self.Game.KeyBindings.values())[i][
                        "value"
                    ] = pygame.key.key_code(var.get().lower())
                    list(self.Game.KeyBindings.values())[i]["key"] = var.get()

            messagebox.showinfo("Control Settings", "Changes applied !")
            self.root.destroy()

    # def __getstate__(self):

    #     state = self.__dict__.copy()
    #     for attrName in ["optionButtons", "buttons"]:
    #         state.pop(attrName)

    #     return state


class SelectMenu(MainMenu):
    def __init__(self, GameController, Map, HeroesGroup):

        super().__init__(GameController, Map)

        self.HeroesGroup = HeroesGroup
        self.HeroIndex = 0
        self.Id = 2
        self.envGenerator = self.Map.envGenerator

        # --------------------------- BUTTONS  ------------------------- #

        self.slots = None

        self.gameSlots = None

        # Back and create game button
        self.utilitiesButton = [
            Button(
                self.initButtonPos[0],
                self.initButtonPos[1]
                - 100
                + ((len(menuConf.GAME_SLOTS) + 1) * self.buttonSpacing),
                ("BACK", BUTTON_FONT_NAME, (255, 255, 255), BUTTON_FONT_SIZE),
                action=self.Game.backToMainMenu,
            ),
            Button(
                self.initButtonPos[0],
                self.initButtonPos[1] - (self.Game.resolution * 0.2),
                (
                    "CREATE A NEW GAME",
                    "dejavusansmono",
                    (255, 255, 255),
                    BUTTON_FONT_SIZE * 2,
                ),
                action=self.nextStep,
            ),
        ]

        for i in range(len(menuConf.GAME_SLOTS)):
            self.buttons[i].surf = pygame.transform.scale(
                self.buttons[i].surf,
                (
                    self.buttons[i].surf.get_width() * 2,
                    self.buttons[i].surf.get_height(),
                ),
            )

        # --------------------------- GAME CREATION STEPS --------------- #

        self.steps = [
            "NoInit",
            "Character Selection",
            "Generation Selection",
            "Difficult Selection",
        ]
        self.stepsCursor = 0
        self.currentStep = self.steps[self.stepsCursor]
        self.stepTitle = Button(
            self.initButtonPos[0],
            self.initButtonPos[1] - 200,
            [self.currentStep, BUTTON_FONT_NAME, (255, 255, 255), BUTTON_FONT_SIZE * 2],
            clickable=False,
        )

        # BACK / NEXT buttons

        self.stepsNavButtons = [
            Button(
                self.initButtonPos[0] + i * self.Game.resolution * 0.33,
                self.initButtonPos[1]
                + ((len(menuConf.GAME_SLOTS) + 1) * self.buttonSpacing - 100),
                (text, BUTTON_FONT_NAME, (255, 255, 255), BUTTON_FONT_SIZE),
                action=action,
            )
            for i, text, action in zip(
                [-1, 1], ["BACK", "NEXT"], [self.backStep, self.nextStep]
            )
        ]

        # CHARAC SELECTION

        self.characSelecCursor = 0
        self.animationCharCount = 0

        self.selecters = [
            Select(
                self.initButtonPos[0] + i * self.Game.resolution * 0.33,
                self.initButtonPos[1] + self.buttonSpacing,
                direction,
                action=action,
            )
            for action, direction, i in zip(
                [
                    lambda: self.decreaseCount(
                        self.characSelecCursor, len(playerConf.CLASSES)
                    ),
                    lambda: self.increaseCount(
                        self.characSelecCursor, len(playerConf.CLASSES)
                    ),
                ],
                ["left", "right"],
                [-1, 1],
            )
        ]

        self.selectedClassName = Button(
            self.initButtonPos[0],
            self.initButtonPos[1] + self.buttonSpacing * 2,
            [
                playerConf.CLASSES[self.characSelecCursor]["name"],
                BUTTON_FONT_NAME,
                (255, 255, 255),
                BUTTON_FONT_SIZE * 2,
            ],
            clickable=False,
        )

        self.charImage = pygame.transform.scale(
            playerConf.CLASSES[self.characSelecCursor]["directions"]["down"][0],
            (PLAYER_SIZE * 4, PLAYER_SIZE * 4),
        )
        self.charImageRect = self.charImage.get_rect(
            center=(self.initButtonPos[0], self.selecters[0].y)
        )

        pygame.time.set_timer(CHARAC_SELECT_ANIM_EVENT_ID, CHAR_ANIMATION_TIME)

        self.textBox = TextBoxControl(
            (self.Game.resolution // 2, int(self.Game.resolution * 0.9)),
        )

        # Gen settings

        self.genParams = [
            self.Map.mapSeed,
            self.Map.octaves,
            self.envGenerator.envStates[self.envGenerator.envGenerationIndicator],
        ]

        self.genButtons = [
            Button(
                self.initButtonPos[0] - self.Game.resolution * 0.2,
                self.initButtonPos[1] + (i * self.buttonSpacing),
                (
                    GEN_MAP_PARAM_NAMES[i] + f" : {self.genParams[i]}",
                    BUTTON_FONT_NAME,
                    (255, 255, 255),
                    BUTTON_FONT_SIZE,
                ),
                clickable=False,
            )
            for i in range(len(GEN_MAP_PARAM_NAMES))
        ]

        self.upButtons = [
            UpButton(
                self.initButtonPos[0]
                + self.Game.resolution * 0.2
                + 50 * (direction == "up"),
                self.initButtonPos[1] + (i * self.buttonSpacing),
                direction,
            )
            for i in range(len(self.genButtons))
            for direction in ["down", "up"]
        ]

        self.upButtons[0].action = lambda: self.Map.updateMapSeed(
            self.upButtons[0].direction
        )
        self.upButtons[1].action = lambda: self.Map.updateMapSeed(
            self.upButtons[1].direction
        )
        self.upButtons[2].action = lambda: self.Map.setLenBiomes(
            self.upButtons[2].direction
        )
        self.upButtons[3].action = lambda: self.Map.setLenBiomes(
            self.upButtons[3].direction
        )
        self.upButtons[4].action = lambda: self.envGenerator.updateGenerationSettings(
            self.upButtons[4].direction
        )
        self.upButtons[5].action = lambda: self.envGenerator.updateGenerationSettings(
            self.upButtons[5].direction
        )

        # DIFFICULTY SELECTION

        self.difficultyButton = Button(
            self.initButtonPos[0],
            self.initButtonPos[1] + self.buttonSpacing // 2,
            [
                self.Game.difficulty,
                BUTTON_FONT_NAME,
                (255, 255, 255),
                BUTTON_FONT_SIZE * 2,
            ],
            clickable=False,
        )

        self.createGameButton = Button(
            self.initButtonPos[0],
            self.initButtonPos[1] + self.buttonSpacing * 2,
            ["LAUNCH GAME", BUTTON_FONT_NAME, (255, 215, 0), BUTTON_FONT_SIZE * 2],
            action=self.loadGame,
        )

        # ------------ SAVE ----------------- #
        def loadSave(i):
            def inner_func():
                self.Game.loadGame(i)

            return inner_func

        self.slots = menuConf.GAME_SLOTS

        self.gameSlots = [
            Button(
                self.initButtonPos[0],
                self.initButtonPos[1] + (i * self.buttonSpacing),
                (
                    self.slots[i]["name"]
                    + f" {'(EMPTY)' if self.slots[i]['empty'] else ''} - {self.slots[i]['creationDate']  if not self.slots[i]['empty'] else ''}",
                    BUTTON_FONT_NAME,
                    (255, 255, 255),
                    BUTTON_FONT_SIZE,
                ),
                clickable=not self.slots[i]["empty"],
                action=loadSave(i + 1),
            )
            for i in range(len(self.buttonNames))
        ]

    def loadGame(self):
        self.stepsCursor = 0
        self.Game.loadNewGame()

    def increaseCount(self):
        self.characSelecCursor = (self.characSelecCursor + 1) % len(playerConf.CLASSES)
        self.updateAnimation()
        self.HeroesGroup[self.HeroIndex].classId = self.characSelecCursor
        self.HeroesGroup[self.HeroIndex].imageState["image"] = playerConf.CLASSES[
            self.HeroesGroup[self.HeroIndex].classId
        ]["directions"]["down"][0]

    def decreaseCount(self):
        self.characSelecCursor = (self.characSelecCursor - 1) % len(playerConf.CLASSES)
        self.updateAnimation()
        self.HeroesGroup[self.HeroIndex].classId = self.characSelecCursor
        self.HeroesGroup[self.HeroIndex].imageState["image"] = playerConf.CLASSES[
            self.HeroesGroup[self.HeroIndex].classId
        ]["directions"]["down"][0]

    def nextStep(self):
        # logger.debug(f"{self.stepsCursor} and {self.HeroIndex}")
        if self.stepsCursor == 1 and self.HeroIndex < len(self.HeroesGroup) - 1:
            if (
                playerConf.MAX_NAME_LENGTH
                >= len(self.HeroesGroup[self.HeroIndex].name)
                > 0
            ):
                self.HeroIndex += 1
            else:
                Dialog(
                    f"Please enter a name with a length between 1 and {playerConf.MAX_NAME_LENGTH}",
                    (self.Game.resolution // 2, self.Game.resolution // 2),
                    self.Game.screen,
                    (0, 0, 0),
                    self.Game,
                    error=True,
                ).mainShow()
            self.textBox.reset()
        else:
            self.stepsCursor = (self.stepsCursor + 1) % len(self.steps)
            self.currentStep = self.steps[self.stepsCursor]
            self.stepTitle.text = self.currentStep

    def backStep(self):

        if self.stepsCursor == 1 and self.HeroIndex > 0:
            self.HeroIndex -= 1
            self.textBox.reset()
        else:
            self.stepsCursor = (self.stepsCursor - 1) % len(self.steps)
            self.currentStep = self.steps[self.stepsCursor]
            self.stepTitle.text = self.currentStep

    def updateAnimation(self):

        self.animationCharCount = (
            self.animationCharCount + 1
        ) % PLAYER_ANIMATION_FRAME_LENGTH

        self.selectedClassName = Button(
            self.initButtonPos[0],
            self.initButtonPos[1] + self.buttonSpacing * 2,
            [
                playerConf.CLASSES[self.characSelecCursor]["name"],
                BUTTON_FONT_NAME,
                (255, 255, 255),
                BUTTON_FONT_SIZE * 2,
            ],
            clickable=False,
        )

        self.charImage = pygame.transform.scale(
            playerConf.CLASSES[self.HeroesGroup[self.HeroIndex].classId]["directions"][
                "down"
            ][self.animationCharCount],
            (PLAYER_SIZE * 4, PLAYER_SIZE * 4),
        )
        self.charImageRect = self.charImage.get_rect(
            center=(
                (self.selecters[0].x + self.selecters[1].x) // 2,
                self.selecters[0].y,
            )
        )

    def stepController(self):

        if self.stepsCursor == 0:
            self.selecters = [
                Select(
                    self.initButtonPos[0] + i * self.Game.resolution * 0.33,
                    self.initButtonPos[1] + self.buttonSpacing,
                    direction,
                    action=action,
                )
                for action, direction, i in zip(
                    [self.decreaseCount, self.increaseCount], ["left", "right"], [-1, 1]
                )
            ]

            self.buttons = self.gameSlots + self.defaultButtons + self.utilitiesButton

        if self.stepsCursor == 1:

            self.HeroesGroup[self.HeroIndex].classId = self.characSelecCursor
            self.buttons = (
                [self.stepTitle]
                + [self.selectedClassName]
                + self.stepsNavButtons
                + self.selecters
            )
            self.HeroesGroup[self.HeroIndex].name = self.textBox.name

        if self.stepsCursor == 2:
            self.genParams = [
                self.Map.mapSeed,
                self.Map.octaves,
                self.envGenerator.envStates[self.envGenerator.envGenerationIndicator],
            ]

            for i, button in enumerate(self.genButtons):
                button.text = GEN_MAP_PARAM_NAMES[i] + f" : {self.genParams[i]}"
            self.buttons = (
                [self.stepTitle]
                + self.stepsNavButtons
                + self.genButtons
                + self.upButtons
            )

        if self.stepsCursor == 3:
            self.difficultyButton.text = self.Game.difficulty
            self.selecters = [
                Select(
                    self.initButtonPos[0] + i * self.Game.resolution * 0.33,
                    self.initButtonPos[1] + self.buttonSpacing // 2,
                    direction,
                    action=action,
                )
                for action, direction, i in zip(
                    [self.Game.decreaseDifficulty, self.Game.increaseDifficulty],
                    ["left", "right"],
                    [-1, 1],
                )
            ]
            self.buttons = (
                [self.stepTitle]
                + [self.stepsNavButtons[0]]
                + self.selecters
                + [self.difficultyButton]
                + [self.createGameButton]
            )


class PauseMenu(OptionMenu):
    def __init__(
        self,
        gameController,
        Map,
        Hero,
        SaveController,
        HeroesGroup,
        NetworkController=None,
    ):

        self.Game = gameController
        self.Map = Map
        self.Hero = Hero
        self.isPaused = False
        self.Id = 3
        self.open = False
        self.saveController = SaveController
        self.heroesGroup = HeroesGroup
        self.NetworkController = NetworkController

        # In order to use the checkActions method, we need to declare
        # these variable even though it won't likely to be used
        self.upButtons = []
        self.selecters = []

        # --------------- MENU SURFACE  ------------- #

        self.menuSurface = pygame.transform.scale(
            menuConf.BG_WOOD, (self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.menuRect = self.menuSurface.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )

        # --------------- BUTTONS ---------------- #

        self.initButtonPos = [
            self.Game.resolution // 2,
            self.menuRect.topleft[1] * 1.05,
        ]
        self.buttonSpacing = self.menuRect.height // len(PAUSE_BUTTON_NAMES)

        self.buttons = [
            Button(
                self.initButtonPos[0],
                self.initButtonPos[1] + self.buttonSpacing * i,
                (
                    PAUSE_BUTTON_NAMES[i],
                    BUTTON_FONT_NAME,
                    (255, 255, 255),
                    BUTTON_FONT_SIZE,
                ),
            )
            for i in range(len(PAUSE_BUTTON_NAMES))
        ]

        # --------------------- MENU SURFACE -------------- #

        self.buttons[0].fontSize = BUTTON_FONT_SIZE * 2
        self.buttons[0].clickable = False
        self.buttons[1].action = self.showVideoSettings
        self.buttons[2].action = self.showControlSettings
        self.buttons[3].action = self.resumeGame
        self.buttons[4].action = self.openToLan
        self.buttons[5].action = self.backToMenu

    def openToLan(self):

        self.NetworkController.createTestConnection()
        self.open = False

    def showSaves(self):

        Dialog(
            "Select a save to overwrite : ",
            (self.Game.resolution // 2, self.Game.resolution // 2),
            self.Game.screen,
            (0, 0, 0),
            self.Game,
        ).mainShow()

        def saveSlot(id):
            def inner_func():
                self.saveController.SaveData(id)
                self.backToMenu()

            return inner_func

        SelectPopUp(
            {f"Game slot {i}": saveSlot(i) for i in range(1, 4)},
            self.Game.screen,
            self.Game,
            (self.Game.resolution // 2, self.Game.resolution // 2),
        ).show()

    def backToMenu(self):
        self.Game.backToMainMenu()
        self.resumeGame()

    def captureBackground(self):
        self.background = self.Game.screen.copy().convert_alpha()

    def resumeGame(self):

        self.open = False

    def initPauseMenu(self):

        self.open = True
        self.mainSurface = self.background.copy()
        self.alpha_surface = pygame.Surface(
            self.mainSurface.get_size(), pygame.SRCALPHA
        )
        self.alpha_surface.fill((255, 255, 255, 127))

        self.mainSurface.blit(self.alpha_surface, (0, 0))

    def mainLoop(self):

        while self.open:
            self.checkActions()
            self.show()


class LoadingMenu:
    def __init__(self, gameController, Map):

        self.Game = gameController
        self.Player_Map = Map
        self.Player_Map.loadingMenu = self

        self.loadingPourcentage = 0
        self.open = False
        self.flagDebug = False

        # ------------ TEXTURES --------------  #

        self.backgrounds = {
            "static": [
                pygame.transform.scale(
                    img, (self.Game.resolution, self.Game.resolution)
                )
                for img in menuConf.LOADINGS_BG_STATIC
            ],
            "dynamic": [
                pygame.transform.scale(
                    img, (self.Game.resolution, self.Game.resolution)
                )
                for img in menuConf.LOADING_BG_DYNAMIC
            ],
            "light": [
                pygame.transform.scale(
                    img, (self.Game.resolution, self.Game.resolution)
                )
                for img in menuConf.LOADING_LIGHTS
            ],
        }

        self.dynamicOffsets = [
            x + 1 for x in range(1, len(self.backgrounds["dynamic"]) + 1)
        ]  # Offset of each layers in pixel

        # [x,y,x1,y1] for the 5 layers
        self.coordonnates = [
            [self.Game.resolution, 0, 0, 0]
            for _ in range(len(self.backgrounds["dynamic"]))
        ]

        self.surfLoadDesc = FONT_LOAD.render(
            f"Loading the game ... {self.loadingPourcentage}",
            True,
            (255, 255, 255),
        )
        self.rectLoadDesc = self.surfLoadDesc.get_rect(
            center=(self.Game.resolution // 2, 50)
        )

        self.currentDesc = ""

        # -------------- ANIMATION ----------- #

        self.flyingDragon = [
            pygame.transform.scale(
                img, (self.Game.resolution // 5, self.Game.resolution // 5)
            )
            for img in menuConf.WALKING_LOADING_GUY
        ]
        self.walkingGuyIndex = 0
        self.walkingGuyRect = self.flyingDragon[0].get_rect(
            topleft=(0, self.Game.resolution // 12)
        )

        self.walkingGuyDeltaTime = WALKING_LOADIN_GUY_ANIM_TIME / (
            len(menuConf.WALKING_LOADING_GUY)
        )  # s
        self.WalkingGuylastRenderedTime = time.time()

        self.totalWidth = (
            self.Game.resolution - self.flyingDragon[0].get_width()
        )  # Loading bar size

        # ------------ LOADING HANDLING ------------ #

        self.openWorldFlags = OPEN_WORLD_FLAGS
        self.openWorldFlags.update(
            {
                "map": {
                    "subflags": {
                        f"chunk_{i}": {
                            "desc": f"Generating chunk n°{i} ...",
                            "weight": round(
                                OPEN_WORLD_FLAGS_WEIGHTS["MAP"]
                                / ((1 + self.Player_Map.renderDistance * 2) ** 2),
                                2,
                            ),
                            "checked": False,
                        }
                        for i in range(
                            1, ((1 + self.Player_Map.renderDistance * 2) ** 2) + 1
                        )
                    },
                    "weight": OPEN_WORLD_FLAGS_WEIGHTS["MAP"],
                    "checked": False,
                }
            }
        )
        self.prevWeight = 0

    def _updateBackgrounds(self):

        # Scrolling backgrounds
        for offset, coordonates in zip(self.dynamicOffsets, self.coordonnates):
            coordonates[0] -= offset
            coordonates[2] -= offset

        for layer in self.backgrounds["static"]:
            self.Game.screen.blit(layer, (0, 0))

        self.Game.screen.blit(random.choice(self.backgrounds["light"]), (0, 0))

        for i, layer in enumerate(self.backgrounds["dynamic"]):

            self.Game.screen.blit(
                layer, (self.coordonnates[i][0], self.coordonnates[i][1])
            )
            self.Game.screen.blit(
                layer, (self.coordonnates[i][2], self.coordonnates[i][3])
            )

        for coordonates in self.coordonnates:
            if coordonates[0] <= -self.Game.resolution:
                coordonates[0] = self.Game.resolution
            if coordonates[2] <= -self.Game.resolution:
                coordonates[2] = self.Game.resolution

    def _updateAnimation(self):

        reachPoint = (self.loadingPourcentage / 100) * self.totalWidth
        realVelocity = (
            self.totalWidth // self.Game.refresh_rate
        ) * 3  # (total_width_in_pixe)/s * 3
        if reachPoint >= self.walkingGuyRect.topleft[0]:
            self.walkingGuyRect.topleft = (
                self.walkingGuyRect.topleft[0] + realVelocity,
                self.walkingGuyRect.topleft[1],
            )

        if (time.time() - self.WalkingGuylastRenderedTime) > self.walkingGuyDeltaTime:

            self.WalkingGuylastRenderedTime = time.time()
            self.walkingGuyIndex = (self.walkingGuyIndex + 1) % len(
                menuConf.WALKING_LOADING_GUY
            )

    def updateProgressBar(self, flagName: str, parentFlagName: str = "") -> None:
        """
        Update the progress bar status by passing in a flagName which is an entry of a dict returning the corresponding description of the loading action, and the weight in the loading pourcentage.

        Parameters:
        ---

        + flagName (str) : the name of the loading action, considered as a flag to get an update on the game's loading
        + parentFlagName (str) [default = ""] : if this value is not an empty string, then the flagName refers to a subflag, which is a subaction of a general loading action.

        """
        if self.Game.currentState == "loadingNewGame":
            # Checking if the flagName is a subflag
            if not parentFlagName == "":
                flag = self.openWorldFlags[parentFlagName]["subflags"][flagName]
            else:
                flag = self.openWorldFlags[flagName]
            self.currentDesc = flag["desc"]

    def confirmLoading(self, flagName: str, parentFlagName: str = "") -> None:
        """
        Update the "checked" attribute of a flagname to True and thus the weight on the loading Menu.
        If the flagName is a subflag, update the "checked" attribute of the parent if needed.

        Parameters:
        ---
        + flagName (str) : the name of the loading action, considered as a flag to get an update on the game's loading
        + parentFlagName (str) [default = ""] : if this value is not an empty string, then the flagName refers to a subflag, which is a subaction of a general loading action.

        """

        if not parentFlagName == "":
            flag = self.openWorldFlags[parentFlagName]["subflags"][flagName]
            flag["checked"] = True
            if all(
                [
                    subflag["checked"]
                    for subflag in self.openWorldFlags[parentFlagName][
                        "subflags"
                    ].values()
                ]
            ):
                self.openWorldFlags[parentFlagName]["checked"] = True
        else:
            flag = self.openWorldFlags[flagName]
            flag["checked"] = True

        # Updating weights
        logger.debug(f"ADDING to {flagName} : {flag['weight']} ")
        self.loadingPourcentage += flag["weight"]
        self.loadingPourcentage = round(self.loadingPourcentage, 2)
        debugCheckStr = "\n{\n"
        for i, flag in enumerate(self.openWorldFlags.values()):
            if flag["checked"]:
                debugCheckStr += f"\t👉 {list(self.openWorldFlags.keys())[i]} : ✅\n"
            else:
                debugCheckStr += f"\t👉 {list(self.openWorldFlags.keys())[i]} : ⌛\n"
        debugCheckStr += "}\n"

        if self.Game.debug_mode and self.flagDebug:
            os.system("cls") if platform.system() == "Windows" else os.system(
                "clear"
            )
            print(debugCheckStr)

    def resetFlags(self) -> None:
        """
        Reset the flags
        """

        self.openWorldFlags = OPEN_WORLD_FLAGS
        self.openWorldFlags.update(
            {
                "map": {
                    "subflags": {
                        f"chunk_{i}": {
                            "desc": f"Generating chunk n°{i} ...",
                            "weight": round(
                                OPEN_WORLD_FLAGS_WEIGHTS["MAP"]
                                / ((1 + self.Player_Map.renderDistance * 2) ** 2),
                                2,
                            ),
                            "checked": False,
                        }
                        for i in range(
                            1, ((1 + self.Player_Map.renderDistance * 2) ** 2) + 1
                        )
                    },
                    "weight": OPEN_WORLD_FLAGS_WEIGHTS["MAP"],
                    "checked": False,
                }
            }
        )
        self.loadingPourcentage = 0

    def show(self):

        # --------------- BACKGROUND BLITTING --------------- #

        self._updateBackgrounds()
        self._updateAnimation()

        # ------------------ DESC TITLE ------------------ #

        self.surfLoadDesc = FONT_LOAD.render(
            f"{self.currentDesc} ({self.loadingPourcentage}%)",
            True,
            (255, 255, 255),
        )

        self.rectLoadDesc = self.surfLoadDesc.get_rect(
            center=(self.Game.resolution // 2, 50)
        )

        self.Game.screen.blit(self.surfLoadDesc, self.rectLoadDesc)

        # ---------------- ANIMATION HANDLING ------------- #

        self.Game.screen.blit(
            self.flyingDragon[self.walkingGuyIndex], self.walkingGuyRect
        )
        self.Game.show()

        if all([flag["checked"] for flag in self.openWorldFlags.values()]):

            self.resetFlags()
            self.Game.goToOpenWorld()

    def blitLoadingIcon(self, Hero):

        blank_bg = self.Game.screen.copy()
        while Hero.reGenChunkFlag:

            self.Game.screen.blit(blank_bg, (0, 0))
            if (
                time.time() - self.WalkingGuylastRenderedTime
            ) > self.walkingGuyDeltaTime:

                self.WalkingGuylastRenderedTime = time.time()
                self.walkingGuyIndex = (self.walkingGuyIndex + 1) % len(
                    menuConf.WALKING_LOADING_GUY
                )

            loadingIcon = pygame.transform.scale(
                self.flyingDragon[self.walkingGuyIndex],
                (self.Game.resolution // 8, self.Game.resolution // 8),
            )

            self.Game.screen.blit(
                loadingIcon, (self.Game.resolution * 0.8, self.Game.resolution * 0.8)
            )
            self.Game.show()

    # def __getstate__(self):

    #     state = self.__dict__.copy()
    #     for attrName in ["backgrounds", "surfLoadDesc", "flyingDragon"]:
    #         state.pop(attrName)

    #     return state
