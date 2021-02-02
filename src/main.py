#!/usr/bin/python3
#!coding:utf-8

import threading
import time
from pickle import load

import pygame
from pygame.locals import *

from config.playerConf import MAX_TEAM_LENGH, TIME_OUT_REST

pygame.init()
pygame.mixer.init()

# Clear console for Xserver wsl2 conflicts
import os
import platform

os.system("cls") if platform.system() == "Windows" else os.system("clear")

import utils.RessourceHandler as RessourceHandler
from config.eventConf import *
from config.mapConf import PLAYER_CONFIG, WORLD_MAP_CONFIG
from fight.CombatLog import CombatLog
from fight.FightMode import FightMode
from gameController import GameController
from Map.MapClass import OpenWorldMap
from Player.Character import Character
from saves.savesController import *
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
Game.heroesGroup += Hero_group


# ------------------- MENUS ----------------------- #

MainMenu = MainMenu(Game, Player_Map)
OptionMenu = OptionMenu(Game, Player_Map, Hero_group)
SelectMenu = SelectMenu(Game, Player_Map, Hero_group)
PauseMenu = PauseMenu(Game, Player_Map, Hero_group, SaveController, Game.heroesGroup)
LoadingMenu = LoadingMenu(Game, Player_Map)

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
        pygame.key.set_repeat()

        Hero = Hero_group[0]

        def loadMap():
            for Hero in Hero_group:
                Hero.initHUD(LoadingMenu)
                Player_Map.loadPlayerdMap(Player_Map.maxChunkGen, Hero)

        loadingThread = threading.Thread(target=loadMap)

        loadingThread.start()

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
        Leader = Hero_group[0]

        Player_Map.show(Leader)

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:

                Player_Map.envGenerator.checkInteractableEntities(event)

                if event.key == K_SPACE:
                    Hero.lvlUp()

                if event.key == Game.KeyBindings["Pick up items"]["value"]:
                    for i, item in enumerate(Player_Map.envGenerator.items):
                        item.lootHandler(Hero, Player_Map.envGenerator, i)

                if event.key == Game.KeyBindings["Pause the game"]["value"]:
                    PauseMenu.captureBackground()
                    PauseMenu.initPauseMenu()
                    PauseMenu.mainLoop()
                    break

                elif (
                    event.key == Game.KeyBindings["Toggle Inventory"]["value"]
                    and Leader.Inventory.open == False
                ):
                    Leader.Inventory.show()
                    break
                elif event.key == Game.KeyBindings["Toggle Spell Book"]["value"]:
                    Hero.SpellBook.show()

                elif event.key == Game.KeyBindings["Open quest's Journal"]["value"]:
                    Hero.QuestJournal.show()

                elif event.key == Game.KeyBindings["Toggle Minimap"]["value"]:
                    Player_Map.miniMap.showExtendedMap()
                elif len(Hero_group) > 1 and event.key == Game.KeyBindings["Switch heroes"]["value"]:
                    Game.heroIndex = (Game.heroIndex + 1) % MAX_TEAM_LENGH

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                Leader.updateClickPoint()

            if event.type == ANIMATE_WATER_EVENT_ID and Player_Map.enableWaterAnimation:
                Player_Map.updateWaterAnimation()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        Leader.handleMovements("openWorld")

        if (
            Game.currentState == "openWorld"
            and not Game.screen.get_locked()
            and not Player_Map.chunkData["mainChunk"].get_locked()
        ):

            Player_Map.envGenerator.showInfoTipElt()
            Player_Map.envGenerator.showNpc()
            Player_Map.envGenerator.showEnnemies()
            Player_Map.envGenerator.showItems()

            Player_Map.miniMap.show()
            Hero.CharBar.show()
            Hero.show()
            Game.show()

            Game.spaceTransition("Pyhm World")

            if (time.time() - Hero.lastTimeoutHealed) > TIME_OUT_REST:
                for H in Hero_group:
                    H.modifyHP(2)
                    logger.info(f"HEALING {H.name} DUE TO REST MECHANICS")
                    H.lastTimeoutHealed = time.time()

        if Game.debug_mode:

            pygame.display.set_caption(
                f"Pyhm World - {str(int(Game_Clock.get_fps()))} fps"
            )
        Game_Clock.tick(Game.refresh_rate)

pygame.quit()
exit()
