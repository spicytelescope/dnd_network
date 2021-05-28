from Player.Character import Character
from config.mapConf import *
from config.playerConf import TURN_REST
import fight
from gameObjects.Ennemy import Ennemy


class FightHandler:
    def __init__(self, entitylist, fightMode, combatLog):
        i = 0
        while i < len(entitylist) - 1:
            if entitylist[i].stats["DEX"] < entitylist[i + 1].stats["DEX"]:
                entitylist[i], entitylist[i + 1] = entitylist[i + 1], entitylist[i]
                i = 0
            else:
                i += 1

        self._queue = entitylist
        self.fightMode = fightMode
        self.combatLog = combatLog
        self._lastID = 0
        for self._lastID in range(len(entitylist)):
            self._queue[self._lastID].setId(self._lastID)
            self.fightMode.stats[
                self._queue[self._lastID]._fightName
            ] = 0  # Initialising damages dealt

        self._fightended = False  # boolean to know if the fight is on going or is ended
        self._fightresult = None  # 0-> fight lose | 1-> fight win

        self.turn = 0
        self.indexEntity = 0

    # get an entity from his position in the queue
    def getEntityinQueue(self, num_entity):
        return self._queue[num_entity]

    def getFightresult(self):
        return self._fightresult

    # check if there are only monsters or only characters and put _fightongoing to false if it is. return _fightongoing
    def isended(self):
        if all((isinstance(self._queue[k], Ennemy)) for k in range(len(self._queue))):
            self._fightended = True
            self._fightresult = 0
            for k in range(len(self._queue)):
                self._queue[k].setId(None)

        elif all(
            (isinstance(self._queue[k], Character)) for k in range(len(self._queue))
        ):
            self._fightended = True
            self._fightresult = 1
            for k in range(len(self._queue)):
                self._queue[k].setId(None)

        return self._fightended

    # usable when you escape from a fight
    def forceend(self):
        self._fightended = True

    # add an entity at the end of the queue
    def addEntity(self, entity):
        self._queue.append(entity)
        self._lastID += 1
        self._queue[len(self._queue) - 1].setId(self._lastID)

    # remove an entity from the queue
    def removeEntity(self, entityId):
        for k in range(len(self._queue)):
            if self._queue[k]._fightId == entityId:
                self._queue[k].setId(None)
                self._queue.pop(k)
                return

    # call rotation to put first entity in the queue at the end
    def rotation(self):

        hero = None

        self.indexEntity = (self.indexEntity + 1) % len(self._queue)
        self._queue.append(self._queue.pop(0))

        for entity in self._queue:
            if isinstance(entity, Character):
                hero = entity
                logger.debug(
                    f"{entity._fightName}'s turn until rest : {entity.lastedTurnRest}"
                )
                if (entity.lastedTurnRest) >= TURN_REST:
                    entity.lastedTurnRest = 0
                    entity.modifyHP(1)

        if self.indexEntity == 0:
            self.combatLog.addTurn()
            self.turn += 1
            hero.lastedTurnRest += 1

        self.fightMode.update()

    # print the queue
    def printQueue(self):
        for k in range(len(self._queue)):
            print(self._queue[k].name, end=", ")
        print(" ")

    def getLenQueue(self):
        return len(self._queue)
