import pygame

from HUD.CharBar import CharBar
from Map.envGenerator import EnvGenerator
from network.NetworkController import NetworkController
from network.chat import GameChat

pygame.init()

from pygame.constants import *
from pygame.constants import KEYDOWN

from config.NPCConf import *
from fight.CombatLog import CombatLog
from fight.FightMode import *
from fight.FightResume import FightRecap
from gameController import *
from HUD.Inventory import Inventory
from HUD.QuestController import QuestController
from Map.MapClass import OpenWorldMap
from UI.ContextMenu import NonBlockingPopupMenu
from UI.menuClass import LoadingMenu
from utils.RessourceHandler import *


# CREATING BASED FEATURES
Game = GameController()
# Game.combatLog = CombatLog(Game)
# Game.fightMode = FightMode(Game)

# LOADING RESSOURCES
loadPlayerRessources()
loadMenuRessources()
# loadLandscapeRessources()
loadItemRessources()
loadOpenWorldRessources(debug=True)
loadHUDRessources()
loadSpellRessources()

# CREATING CORE FEATURES
Player_Map = OpenWorldMap(PLAYER_CONFIG, Game, debug=True)
LdingMenu = LoadingMenu(Game, Player_Map)
Hero = Character(Game, Player_Map)
Hero.genOrder = 0
Hero2 = Character(Game, Player_Map)
Game.heroesGroup = [Hero, Hero2]
Hero.initHUD(LdingMenu)
Hero2.initHUD(LdingMenu)

ContextMenu = NonBlockingPopupMenu(POP_UP_ACTIONS, Game)
NetworkController = NetworkController(Game, Player_Map, Hero, ContextMenu)
Game.NetworkController = NetworkController
ContextMenu.bind(Hero, Hero2)



# ContextMenu.tradeUI.waitingFlag = True
ContextMenu.tradeUI.waitChrono = time.time()
ContextMenu.tradeUI.confirmRecvFlag = True
ContextMenu.tradeUI._show = True

while True:

    Game.screen.fill((255, 255, 255))
    for event in pygame.event.get():
        ContextMenu.tradeUI.checkActions(event)

    ContextMenu.tradeUI.draw()
    Game.show()
