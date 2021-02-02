import pygame
from pygame.constants import KEYDOWN
from HUD.Inventory import Inventory
from config.NPCConf import *

from HUD.QuestController import QuestController

pygame.mixer.init()
from pygame.constants import *
from Map.MapClass import OpenWorldMap
from fight.CombatLog import CombatLog
from fight.FightResume import FightRecap
from gameController import *
from fight.FightMode import *
from utils.RessourceHandler import *

pygame.init()

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
# Game.combatLog = CombatLog(Game)
# Game.fightMode = FightMode(Game)
Hero.QuestJournal = QuestController(Game, Hero)
Hero.Inventory = Inventory(Game, Hero)
# Hero.stats["Money"] = 100
# for _ in range(4):
#     Hero.QuestJournal.addQuest(random.choice(NPC_QUESTS))

while True:

    Game.screen.fill((0, 0, 0))
    # for event in pygame.event.get():
    #     if (
    #         event.type == KEYDOWN
    #         and event.key == Game.KeyBindings["Open quest's Journal"]["value"]
    #     ):
    #         Hero.QuestJournal.show()
    #     if (
    #         event.type == KEYDOWN
    #         and event.key == K_SPACE
    #         and Hero.QuestJournal.quests != []
    #     ):
    #         Hero.QuestJournal.questsEnded.append(Hero.QuestJournal.quests.pop(0))
    #         Hero.QuestJournal.getReward(Hero.QuestJournal.quests[0]["id"])

    Game.show()
