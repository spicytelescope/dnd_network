import pygame

from HUD.CharBar import CharBar
from Map.envGenerator import EnvGenerator

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
Game.combatLog = CombatLog(Game)
Game.fightMode = FightMode(Game)

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
Game.heroesGroup = [Hero]

Hero.genOrder = 0
Hero.initHUD(LdingMenu)

while True:

    Game.screen.fill((0, 0, 0))

    Hero.createFight(
        [
            Hero,
            Ennemy(
                Game.screen,
                Hero,
                Game,
                None,
                "Skeleton",
                0,
                1,
            ),
        ]
    )
    Game.show()
