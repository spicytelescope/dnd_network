#!/usr/bin/python3
#!coding:utf-8

import threading
import time
import random

import pygame
from pygame.locals import *

pygame.init()
# pygame.mixer.init()

# Clear console for Xserver wsl2 conflicts
import os
import platform

os.system("cls") if platform.system() == "Windows" else os.system("clear")


import utils.RessourceHandler as RessourceHandler
from config.eventConf import *
from config.mapConf import PLAYER_CONFIG, WORLD_MAP_CONFIG
from config.playerConf import MAX_TEAM_LENGH, TIME_OUT_REST
from config.UIConf import POP_UP_ACTIONS
from fight.CombatLog import CombatLog
from fight.FightMode import FightMode
from gameController import GameController
from Map.MapClass import OpenWorldMap
from network.NetworkController import NetworkController
from Player.Character import Character
from saves.savesController import *
from UI.ContextMenu import NonBlockingPopupMenu
from UI.menuClass import LoadingMenu, MainMenu, OptionMenu, PauseMenu, SelectMenu

RessourceHandler.loadMusicRessources()

Game = GameController()
Game.combatLog = CombatLog(Game)
Game.fightMode = FightMode(Game)

Game_Clock = pygame.time.Clock()
SaveController = SaveController()

RessourceHandler.loadPlayerRessources()
RessourceHandler.loadMenuRessources()
RessourceHandler.loadLandscapeRessources()

# ---------------- CORE FEATURES -------------------- #

Player_Map = OpenWorldMap(PLAYER_CONFIG, Game)
World_Map = OpenWorldMap(WORLD_MAP_CONFIG, Game)
Hero_group = [Character(Game, Player_Map, genOrder=i) for i in range(MAX_TEAM_LENGH)]
Leader = Hero_group[0]  # The one with self.genOrder set to 0
Game.heroesGroup += Hero_group

# ------------------ NETWORKING -------------- #

ContextMenu = NonBlockingPopupMenu(POP_UP_ACTIONS, Game)
NetworkController = NetworkController(Game, Player_Map, Hero_group[0], ContextMenu)
Game.NetworkController = NetworkController

# ------------------- MENUS -------------------- #

MainMenu = MainMenu(Game, Player_Map)
OptionMenu = OptionMenu(Game, Player_Map, Hero_group)
SelectMenu = SelectMenu(Game, Player_Map, Hero_group)
PauseMenu = PauseMenu(
    Game, Player_Map, Hero_group, SaveController, Game.heroesGroup, NetworkController
)
LoadingMenu = LoadingMenu(Game, Player_Map)
NetworkController.LoadingMenu = LoadingMenu

# ------------------ SAVES -------------------- #

SaveController.gameClasses = [
    # Game,
    Player_Map,
    World_Map,
    Hero_group[0],
    # MainMenu,
    # OptionMenu,
    # SelectMenu,
    # PauseMenu,
    # LoadingMenu,
]


while Game.currentState != "quit":

    while Game.currentState == "mainMenu":

        MainMenu.checkActions()
        MainMenu.show()

    while Game.currentState == "selectGame":

        SelectMenu.stepController()
        SelectMenu.checkActions()
        SelectMenu.show()

    while Game.currentState == "mainMenu_options":

        OptionMenu.checkActions()
        OptionMenu.show()

    if Game.currentState == "loadingNewGame":
        pygame.key.set_repeat()  # To reset the name's choice
        Hero = Hero_group[0]

        def loadMap():
            for Hero in Hero_group:
                Hero.initHUD(LoadingMenu)
                Player_Map.loadPlayerdMap(Player_Map.maxChunkGen, Hero)

        loadingThread = threading.Thread(target=loadMap)
        loadingThread.start()
        # loadingProcess = multiprocessing.Process(target=loadMap)
        # loadingProcess.start()
        # loadingProcess.join()

        while Game.currentState == "loadingNewGame":
            LoadingMenu.show()
        Player_Map.miniMap.WorldMap = World_Map
        Player_Map.miniMap.WorldMap.mapSeed = Player_Map.mapSeed

    if Game.currentState == "loading":
        pygame.key.set_repeat()

        RessourceHandler.loadGameRessources()
        (
            # Game,
            Player_Map,
            World_Map,
            Hero,
            # OptionMenu
        ) = SaveController.LoadData(Game.id)
        Player_Map.Game = Game
        World_Map.Game = Game
        Hero.Game = Game
        Game.goToOpenWorld()
    
    while Game.currentState == "openWorld":
            Hero = Hero_group[Game.heroIndex]

            # ----------------- REST MECHANIC -------------------- #
            if (time.time() - Hero.lastTimeoutHealed) > TIME_OUT_REST:
                for H in Hero_group:
                    H.modifyHP(2)
                    logger.info(f"HEALING {H.name} DUE TO REST MECHANICS")
                    H.lastTimeoutHealed = time.time()

            for event in pygame.event.get():

                # ------------------- NETWORK HANDLING ----------------- #
                if Game.isOnline and NetworkController.players != {}:
                    # NetworkController.handleInteractions(event)
                    pass

                # ------------------ HUD Handling --------------------- #

                if Hero.Inventory._show:
                    Hero.Inventory.checkActions(event)
                if Hero.QuestJournal._show:
                    Hero.QuestJournal.checkActions(event)
                if Hero.SpellBook._show:
                    Hero.SpellBook.checkActions(event)
                if Player_Map.miniMap._show:
                    Player_Map.miniMap.checkActions(event)

                # -------------------- KEY BINDING HANDLING ----------- #
                if event.type == pygame.KEYDOWN:

                    Player_Map.envGenerator.checkInteractableEntities(event)

                    if event.key == Game.KeyBindings["Pick up items"]["value"]:
                        for i, item in enumerate(Player_Map.envGenerator.items):
                            item.lootHandler(Hero, Player_Map.envGenerator, i)

                    elif event.key == Game.KeyBindings["Pause the game"]["value"]:
                        PauseMenu.captureBackground()
                        PauseMenu.initPauseMenu()
                        PauseMenu.mainLoop()
                        break

                    elif (
                        event.key == Game.KeyBindings["Toggle Inventory"]["value"]
                        and not Hero.Inventory._show
                        and not Hero.Inventory.open
                    ):
                        Hero.Inventory.open = True
                        break

                    elif (
                        event.key == Game.KeyBindings["Toggle Spell Book"]["value"]
                        and not Hero.SpellBook._show
                        and not Hero.SpellBook.open
                    ):
                        Hero.SpellBook.open = True
                        break

                    elif (
                        event.key == Game.KeyBindings["Open quest's Journal"]["value"]
                        and not Hero.QuestJournal._show
                        and not Hero.QuestJournal.open
                    ):
                        Hero.QuestJournal.open = True

                    elif event.key == Game.KeyBindings["Toggle Minimap"]["value"]:
                        Player_Map.miniMap._show = not Player_Map.miniMap._show

                    elif (
                        event.key
                        == Game.KeyBindings["Show the connected player (Online mode only)"][
                            "value"
                        ]
                        and Game.isOnline
                    ):
                        NetworkController._show = not NetworkController._show

                    elif (
                        len(Hero_group) > 1
                        and event.key == Game.KeyBindings["Switch heroes"]["value"]
                    ):
                        Game.heroIndex = (Game.heroIndex + 1) % MAX_TEAM_LENGH

                    if event.key == K_SPACE:
                        Hero.lvlUp()

                # ------------------ MOVEMENTS --------------- #
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 3
                    and not ContextMenu._show
                ):
                    Leader.updateClickPoint()

                # ---------------- WATER ANIM ------------------- #
                if event.type == ANIMATE_WATER_EVENT_ID and Player_Map.enableWaterAnimation:
                    Player_Map.updateWaterAnimation()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            Leader.handleMovements("openWorld")

            # ------------------------------ DRAWING ------------------------------- #
            if (
                Game.currentState == "openWorld"
                and not Game.screen.get_locked()
                and not Player_Map.chunkData["mainChunk"].get_locked()
            ):
                # -------------- MAP HANDLING ------------- #

                Player_Map.show(Leader)
                Player_Map.envGenerator.showInfoTipElt()
                Player_Map.envGenerator.showNpc()
                Player_Map.envGenerator.showEnnemies()
                Player_Map.envGenerator.showItems()

                # -------------- PLAYERS HANDLING ----------- #
                Hero.show()

                # ------------------- HUD HANDLING ----------- #

                Hero.CharBar.show()
                # Player_Map.miniMap.show()
                Hero.Inventory.draw()
                Hero.QuestJournal.draw()
                Hero.SpellBook.draw()
                Player_Map.miniMap.drawExtendedMap()
                if Game.isOnline:
                    # NetworkController.handleConnectedPlayers()
                    # threading.Thread(target=NetworkController.handleConnectedPlayers).start()
                    NetworkController.drawPannel()
                    NetworkController.updateGraphics()
                    if ContextMenu.tradeUI != None:
                        ContextMenu.tradeUI.draw()
                    ContextMenu.draw()

                Game.show()
                Game.spaceTransition("Pyhm World")

            if Game.debug_mode:

                pygame.display.set_caption(
                    f"Pyhm World - {str(int(Game_Clock.get_fps()))} fps"
                )

            Game_Clock.tick(Game.refresh_rate)

