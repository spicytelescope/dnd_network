import pygame
pygame.init()

from pygame.constants import KEYDOWN
from HUD.Inventory import Inventory
from UI.ContextMenu import NonBlockingPopupMenu
from config.NPCConf import *

from HUD.QuestController import QuestController

from pygame.constants import *
from Map.MapClass import OpenWorldMap
from fight.CombatLog import CombatLog
from fight.FightResume import FightRecap
from gameController import *
from fight.FightMode import *
from utils.RessourceHandler import *


loadMusicRessources()

Game = GameController()

loadPlayerRessources()
loadMenuRessources()
loadLandscapeRessources()
loadItemRessources()
loadOpenWorldRessources()
loadHUDRessources()
loadSpellRessources()

Player_Map = OpenWorldMap(PLAYER_CONFIG, Game)
Hero = Character(Game, Player_Map)
Hero._Level = 1
Hero.QuestJournal = QuestController(Game, Hero)
Hero.Inventory = Inventory(Game, Hero)
ContextMenu = NonBlockingPopupMenu(POP_UP_ACTIONS, Game, Hero, Hero)

while True:

    Game.screen.fill((0, 0, 0))

    ContextMenu.draw()

    # Pass them through the menu. If the menu is visible it will consume mouse
    # events and return any unhandled events; else it will return them all.
    # Process the unhandled events returned by the menu. Function handle_menu()
    # processes only events posted by the menu.
    for e in ContextMenu.handle_events(pygame.event.get()):
        ContextMenu.checkEvents(e)

    Game.show()