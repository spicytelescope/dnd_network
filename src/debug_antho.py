import pygame
import utils.RessourceHandler as RessourceHandler
pygame.mixer.init()
RessourceHandler.loadMusicRessources()

from gameController import GameController
from fight.FightMode import FightMode

test_1 = GameController()
test_2 = FightMode(test_1)

RessourceHandler.loadPlayerRessources()
RessourceHandler.loadMenuRessources()
RessourceHandler.loadLandscapeRessources()
RessourceHandler.loadItemRessources()

RessourceHandler.loadOpenWorldRessources(64)
from Player.Character import Character
from gameObjects.Ennemy import Ennemy


perso_1 = Character(test_2.Game)
perso_2 = Character(test_2.Game)
perso_1._Level = 1
enemy_1 = Ennemy(test_1.screen, perso_1, test_1, None, "Goblin", 0, 5)
perso_2.is_playable = False
perso_1._fightId = 1
perso_2._fightId = 2
print(perso_1.classId)
test_2.initFight([perso_1, perso_2])
