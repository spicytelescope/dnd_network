import math
import pygame
import random
from pygame.locals import *
from UI.UI_utils_text import Dialog
from config import HUDConf, playerConf, spellsConf, textureConf
from config.fightConf import *
from fight.FightHandler import FightHandler
import sys
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from fight.FightResume import FightRecap

from utils.utils import logger
from gameObjects.Ennemy import Ennemy
from Player.Character import Character
import time


class Tile:
    def __init__(self, centered_x, centered_y, access, num_tile):
        self.coeffa = 15 / 32
        self.coeffbhautgauche = centered_y + 49
        self.coeffbhautdroite = centered_y + 19
        self.coeffbbasgauche = centered_y + 49
        self.coeffbbasdroite = centered_y + 79
        self.access = access
        self.centerx = centered_x
        self.tilecenterx = centered_x + 32
        self.tilecentery = centered_y + 49
        self.num_tile = num_tile
        self.entity = None

    def getTilecenter(self):
        return self.tilecenterx, self.tilecentery

    def getEntity(self):
        return self.entity

    def getAccess(self):
        return self.access

    def getNumtile(self):
        return self.num_tile

    def setAccess(self, access):
        self.access = access

    def setEntity(self, entity):
        self.entity = entity

    def ismouseontile(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x = mouse_x - self.centerx
        if (
            (mouse_y >= -self.coeffa * mouse_x + self.coeffbhautgauche)
            and (mouse_y >= self.coeffa * mouse_x + self.coeffbhautdroite)
            and (mouse_y <= self.coeffa * mouse_x + self.coeffbbasgauche)
            and (mouse_y <= -self.coeffa * mouse_x + self.coeffbbasdroite)
        ):
            return True
        else:
            return False


class Movable_character(pygame.sprite.Sprite):
    def __init__(self, entity, tilebegin, ID, Fight):
        super().__init__()
        self.entity = entity
        self._fightId = ID

        self.fight = Fight
        self.asset_path = "./assets/fight"
        self.MOVE_LIMIT = 15
        self.MOVE_AMPLITUDE = 5

        # self.position_x, self.position_y = tilebegin.getTilecenter()
        self._numtilepos = tilebegin.getNumtile()
        if isinstance(self.entity, Ennemy):
            self.neutral = [
                pygame.transform.scale2x(frame) if self.entity.isBoss else frame
                for frame in textureConf.WORLD_ELEMENTS["Ennemy"][self.entity.name][
                    "frames"
                ]["neutral"]
            ][0]
            self.image_walk_right = [
                pygame.transform.scale2x(frame) if self.entity.isBoss else frame
                for frame in textureConf.WORLD_ELEMENTS["Ennemy"][self.entity.name][
                    "frames"
                ]["walk_droit"]
            ]
            self.image_walk_bot = [
                pygame.transform.scale2x(frame) if self.entity.isBoss else frame
                for frame in textureConf.WORLD_ELEMENTS["Ennemy"][self.entity.name][
                    "frames"
                ]["walk_bas"]
            ]
            self.image_walk_left = [
                pygame.transform.scale2x(frame) if self.entity.isBoss else frame
                for frame in textureConf.WORLD_ELEMENTS["Ennemy"][self.entity.name][
                    "frames"
                ]["walk_gauche"]
            ]
            self.image_walk_top = [
                pygame.transform.scale2x(frame) if self.entity.isBoss else frame
                for frame in textureConf.WORLD_ELEMENTS["Ennemy"][self.entity.name][
                    "frames"
                ]["walk_haut"]
            ]

        if isinstance(self.entity, Character):
            self.neutral = playerConf.CLASSES[self.entity.classId]["isometricFrame"][
                "neutral"
            ][0]
            self.image_walk_right = playerConf.CLASSES[self.entity.classId][
                "isometricFrame"
            ]["walk_droit"]
            self.image_walk_bot = playerConf.CLASSES[self.entity.classId][
                "isometricFrame"
            ]["walk_bas"]
            self.image_walk_left = playerConf.CLASSES[self.entity.classId][
                "isometricFrame"
            ]["walk_gauche"]
            self.image_walk_top = playerConf.CLASSES[self.entity.classId][
                "isometricFrame"
            ]["walk_haut"]

        self.index = 0
        self.image = self.neutral
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tilebegin.getTilecenter()
        self.rect.x += -19
        self.rect.y += -73
        x, y = self._numtilepos
        self.fight.setEntityonTile(self._numtilepos, self.entity)

        tilebegin.setAccess(False)

        # self.map_pathfinding[x][y] = 0

    def pathfinding(self, matrix, start, end, isdiagonalmovement):
        grid = Grid(matrix=matrix)
        start = grid.node(start[1], start[0])
        end = grid.node(end[1], end[0])
        if isdiagonalmovement:
            finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        else:
            finder = AStarFinder()

        path, runs = finder.find_path(start, end, grid)

        logger.debug(f"operations: {runs}, path length: {len(path)}")
        print(grid.grid_str(path=path, start=start, end=end))
        return path

    def move(self, endtile):

        path = self.pathfinding(
            self.fight.map_pathfinding, self._numtilepos, endtile.getNumtile(), False
        )
        if len(path) <= self.MOVE_LIMIT:
            # xtile,ytile=self._numtilepos
            self.fight.setEntityonTile(self._numtilepos, None)
            self.fight.setEntityonTile(endtile.getNumtile(), self.entity)
            # self.map_tile[xtile][ytile].setAccess(True)
            # self.map_tile[xtile][ytile].setEntity(None)
            # xtile,ytile=endtile.getNumtile()
            # self.map_tile[xtile][ytile].setAccess(False)
            # self.map_tile[xtile][ytile].setEntity(self.entity)

            for k in range(len(path) - 1):
                y, x = list(path[k + 1])
                # self.rect.x, self.rect.y = self.map_tile[x][y].getTilecenter()
                endtile_x, endtile_y = self.fight.map_tile[x][y].getTilecenter()
                endtile_x += -19
                endtile_y += -73
                m = ((endtile_y) - self.rect.y) / ((endtile_x) - self.rect.x)
                p = self.rect.y - m * self.rect.x
                while (self.rect.x != endtile_x) and (self.rect.y != endtile_y):
                    # deplacement droite
                    if (self.rect.x < endtile_x) and (self.rect.y < endtile_y):
                        if ((self.rect.x + self.MOVE_AMPLITUDE) > endtile_x) or (
                            (m * self.rect.x + p) > endtile_y
                        ):
                            self.rect.x = endtile_x
                            self.rect.y = endtile_y
                        else:
                            self.rect.x += self.MOVE_AMPLITUDE
                            self.rect.y = m * self.rect.x + p
                        self.image = self.image_walk_right[self.index]
                        self.index += 1
                        if self.index >= len(self.image_walk_right):
                            self.index = 0
                    # deplacement bas
                    if (self.rect.x > endtile_x) and (self.rect.y < endtile_y):
                        if ((self.rect.x - self.MOVE_AMPLITUDE) < endtile_x) or (
                            (m * self.rect.x + p) > endtile_y
                        ):
                            self.rect.x = endtile_x
                            self.rect.y = endtile_y
                        else:
                            self.rect.x -= self.MOVE_AMPLITUDE
                            self.rect.y = m * self.rect.x + p
                        self.image = self.image_walk_bot[self.index]
                        self.index += 1
                        if self.index >= len(self.image_walk_bot):
                            self.index = 0
                    # deplacement gauche
                    if (self.rect.x > endtile_x) and (self.rect.y > endtile_y):
                        if ((self.rect.x - self.MOVE_AMPLITUDE) < endtile_x) or (
                            (m * self.rect.x + p) < endtile_y
                        ):
                            self.rect.x = endtile_x
                            self.rect.y = endtile_y
                        else:
                            self.rect.x -= self.MOVE_AMPLITUDE
                            self.rect.y = m * self.rect.x + p
                        self.image = self.image_walk_left[self.index]
                        self.index += 1
                        if self.index >= len(self.image_walk_left):
                            self.index = 0
                    # deplacement haut
                    if (self.rect.x < endtile_x) and (self.rect.y > endtile_y):
                        if ((self.rect.x + self.MOVE_AMPLITUDE) > endtile_x) or (
                            (m * self.rect.x + p) < endtile_y
                        ):
                            self.rect.x = endtile_x
                            self.rect.y = endtile_y
                        else:
                            self.rect.x += self.MOVE_AMPLITUDE
                            self.rect.y = m * self.rect.x + p
                        self.image = self.image_walk_top[self.index]
                        self.index += 1
                        if self.index >= len(self.image_walk_top):
                            self.index = 0

                    self.fight.update()
                # self.rect.x += -19
                # self.rect.y += -73
                self.index = 0
                self._numtilepos = endtile.getNumtile()

            self.image = self.neutral
        else:
            self.fight.Game.combatLog.addText(
                f"{self.entity._fightName} tried a too large move and lost his turn !"
            )

    def getId(self):
        return self._fightId

    def getNumtilepos(self):
        return self._numtilepos

    def getEntity(self):
        return self.entity


class FightMode:
    def __init__(self, gameController) -> None:

        self.Game = gameController
        self.Heroes = []
        self.open = False

        self.turn_based_fight = None
        self.sprite_list = []
        self.asset_path = "./assets/fight"
        self.fightResume = None

        self.MAP_SIZE = 12
        self.n_rocks = 3

        self.map_data = [
            [-1 if i == 0 else 3 for i in range(self.MAP_SIZE)]
            for j in range(self.MAP_SIZE)
        ]
        self.map_data[0] = [-1 if i == 0 else -2 for i in range(self.MAP_SIZE)]
        for _ in range(self.n_rocks):
            i = random.randrange(self.MAP_SIZE)
            j = random.randrange(self.MAP_SIZE)
            while self.map_data[j][i] != 3:
                i = random.randrange(self.MAP_SIZE)
                j = random.randrange(self.MAP_SIZE)

            self.map_data[j][i] = 0

        self.stats = {}
        self.initalEntityList = []

        # self.map_data = [
        #     [-1, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 0, 3, 3, 3, 3, 0, 3, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 3, 0, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 0, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        #     [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        # ]  # the data for the map expressed as [row[tile]].

        self.map_tile = [x[:] for x in self.map_data]
        self.map_pathfinding = [x[:] for x in self.map_data]
        self.highlightedTiles = []
        self.centerTileOnMouse = None

        self.background = None
        self.wall_g = pygame.image.load(
            f"{self.asset_path}/wall_gauche.png"
        )  # load fi{self.asset_path}
        self.wall_d = pygame.image.load(f"{self.asset_path}/wall_droit.png")
        self.grass = pygame.image.load(f"{self.asset_path}/grass_1.png")
        self.rock = pygame.image.load(f"{self.asset_path}/rock.png")
        self.highlightsprite = pygame.image.load(
            f"{self.asset_path}/grass_highlight.png"
        )

        self.TILEWIDTH = 64  # holds the tile width and height
        self.TILEHEIGHT = 64
        self.TILEHEIGHT_HALF = self.TILEHEIGHT / 2
        self.TILEWIDTH_HALF = self.TILEWIDTH / 2

        self.firstOpen = True

    def transition(self):

        alpha_value = 0
        delta = TRANSITION_DURATION / (255 // TRANSITION_FACTOR)
        black_screen = pygame.Surface(
            (self.Game.resolution, self.Game.resolution), SRCALPHA
        )
        for _ in range(255 // TRANSITION_FACTOR):
            alpha_value += TRANSITION_FACTOR
            black_screen.fill((0, 0, 0, alpha_value))
            self.Game.screen.blit(black_screen, (0, 0))
            self.Game.show()
            time.sleep(delta)

    def create_map(self):

        for row_nb, row in enumerate(self.map_data):  # for every row of the map...
            for col_nb, tile_value in enumerate(row):
                if tile_value == 5:
                    tileImage = self.highlightsprite
                elif tile_value == 3:
                    tileImage = self.grass
                elif tile_value == -2:
                    tileImage = self.wall_d
                elif tile_value == -1:
                    tileImage = self.wall_g
                elif tile_value == 0:
                    tileImage = self.rock
                else:
                    tileImage = None

                cart_x = col_nb * self.TILEWIDTH_HALF
                cart_y = row_nb * self.TILEHEIGHT_HALF
                iso_x = cart_x - cart_y
                iso_y = (cart_x + cart_y) / 2
                centered_x = self.Game.screen.get_rect().centerx + iso_x
                centered_y = self.Game.screen.get_rect().centery / 2 + iso_y

                if tileImage == self.grass:
                    self.Game.screen.blit(tileImage, (centered_x, centered_y))
                    if self.firstOpen:
                        self.map_tile[row_nb][col_nb] = Tile(
                            centered_x, centered_y, True, [row_nb, col_nb]
                        )
                        self.map_pathfinding[row_nb][col_nb] = 1
                    # grid
                    pygame.draw.line(
                        self.Game.screen,
                        (0, 0, 0),
                        (centered_x, centered_y + 49 - 2),
                        (centered_x + 31, centered_y + 65 - 3),
                    )
                    pygame.draw.line(
                        self.Game.screen,
                        (0, 0, 0),
                        (centered_x + 64, centered_y + 49 - 2),
                        (centered_x + 32, centered_y + 65 - 3),
                    )

                elif tileImage == self.highlightsprite:
                    self.Game.screen.blit(
                        self.highlightsprite, (centered_x, centered_y)
                    )
                    self.map_data[row_nb][col_nb] = 3

                elif tileImage != None:
                    self.Game.screen.blit(self.grass, (centered_x, centered_y))
                    self.Game.screen.blit(
                        tileImage, (centered_x, centered_y)
                    )  # display the actual tile
                    if self.firstOpen:
                        tile = Tile(centered_x, centered_y, False, [row_nb, col_nb])
                        self.map_tile[row_nb][col_nb] = tile
                        self.map_pathfinding[row_nb][col_nb] = 0

        self.firstOpen = False

    def initFight(self, entityList):

        self.Game.musicController.setMusic("fight")
        self.Game.cursor.hide()
        self.transition()

        self.initalEntityList = entityList[::]
        for entity in entityList:
            if isinstance(entity, Character):
                self.Heroes.append(entity)
                break

        self.background = pygame.transform.scale(
            pygame.image.load(
                f"{self.asset_path}/{self.Heroes[0].currentPlace}_bg.png"
            ).convert(),
            (self.Game.resolution, self.Game.resolution),
        )
        self.create_map()
        self.turn_based_fight = FightHandler(entityList, self, self.Game.combatLog)
        self.fightResume = FightRecap(self.Game, self)
        self.fightResume.initLootSurf(entityList)

        self.sprite_list = []
        for k in range(self.turn_based_fight.getLenQueue()):
            i, j = random.randint(0, 11), random.randint(0, 11)
            while self.map_tile[i][j].getAccess() == False:
                i, j = random.randint(0, 11), random.randint(0, 11)
            self.sprite_list.append(
                Movable_character(
                    self.turn_based_fight.getEntityinQueue(k),
                    self.map_tile[i][j],
                    self.turn_based_fight.getEntityinQueue(k)._fightId,
                    self,
                )
            )

        self.open = True
        self.mainLoop()

    def resetFight(self):
        self.Game.combatLog.reset()
        self.__init__(self.Game)

    def setEntityonTile(self, numtile, entity):
        x, y = numtile
        self.map_tile[x][y].setEntity(entity)
        if entity != None:
            self.map_pathfinding[x][y] = 0
            self.map_tile[x][y].setAccess(False)
        else:
            self.map_pathfinding[x][y] = 1
            self.map_tile[x][y].setAccess(True)

    def update(self, spellFrameInfo=()):

        self.Game.screen.blit(
            self.background,
            (0, 0),
        )

        # ------------ MAP DRAWING ----------------- #
        self.create_map()

        # -------------- ENNEMY DRAWING ---------- #
        for tilerow_nb, tilerow in enumerate(self.map_tile):
            for tilecol_nb, x in enumerate(tilerow):
                tile_destination = self.map_tile[tilerow_nb][tilecol_nb]
                if tile_destination.getEntity() != None:
                    for k in range(len(self.sprite_list)):
                        if (
                            self.sprite_list[k]._fightId
                            == tile_destination.getEntity()._fightId
                        ):
                            self.sprite_list.append(self.sprite_list.pop(k))

        for k in range(len(self.sprite_list)):
            self.Game.screen.blit(self.sprite_list[k].image, self.sprite_list[k].rect)

        # ------------ SPELL UPDATING ------------------ #
        if spellFrameInfo != ():
            self.Game.screen.blit(*spellFrameInfo)

        # --------------- TURN UPDATING ------------------ #
        text = "{}'s turn".format(self.turn_based_fight.getEntityinQueue(0)._fightName)
        turnFont = pygame.font.SysFont("Arial", 40).render(text, True, (0, 0, 0))
        turnLayout = pygame.transform.scale(
            HUDConf.NAME_SLOT,
            (int(turnFont.get_width() * 1.5), int(turnFont.get_height() * 1.5)),
        )

        turnLayout.blit(
            turnFont,
            turnFont.get_rect(
                center=(turnLayout.get_width() // 2, turnLayout.get_height() // 2)
            ),
        )
        self.Game.screen.blit(
            turnLayout,
            turnLayout.get_rect(
                center=(self.Game.resolution // 2, int(self.Game.resolution * 0.75))
            ),
        )

        if isinstance(self.turn_based_fight.getEntityinQueue(0), Character):
            self.turn_based_fight.getEntityinQueue(0).CharBar.show()
        self.Game.show(combatMode=True)

    def spellhighlight(
        self, spell_type="square", spell_range=1
    ):  # spell_type = 0 -> line  / spell_type = 1 -> square / spell_type = 2 -> diagonal

        self.highlightedTiles = []
        for tilerow_nb, tilerow in enumerate(self.map_tile):
            for tilecol_nb, x in enumerate(tilerow):
                tile_destination = self.map_tile[tilerow_nb][tilecol_nb]
                if tile_destination.ismouseontile():
                    self.centerTileOnMouse = tile_destination
                    if spell_type == "line":
                        x, y = tile_destination.getNumtile()
                        for k in range(len(self.sprite_list)):
                            if (
                                self.sprite_list[k]._fightId
                                == self.turn_based_fight.getEntityinQueue(0)._fightId
                            ):
                                start = self.sprite_list[k].getNumtilepos()
                                xstart, ystart = start
                                break

                        if (
                            (-spell_range <= xstart - x <= spell_range)
                            and (ystart - y == 0)
                        ) or (
                            (-spell_range <= ystart - y <= spell_range)
                            and (xstart - x == 0)
                        ):
                            if xstart - x == 0:
                                for k in range(
                                    min(ystart, y) + 1
                                    if (y > ystart)
                                    else min(ystart, y),
                                    max(ystart, y) + 1
                                    if (y > ystart)
                                    else max(ystart, y),
                                ):
                                    if 0 <= y <= self.MAP_SIZE:

                                        self.highlightedTiles.append([x, k])
                                        if self.map_data[x][k] == 3:
                                            self.map_data[x][k] = 5
                                        else:
                                            break
                            elif ystart - y == 0:
                                for k in range(
                                    min(xstart, x) + 1
                                    if (x > xstart)
                                    else min(xstart, x),
                                    max(xstart, x) + 1
                                    if (x > xstart)
                                    else max(xstart, x),
                                ):
                                    if 0 <= x <= self.MAP_SIZE:
                                        self.highlightedTiles.append([k, y])
                                        if self.map_data[k][y] == 3:
                                            self.map_data[k][y] = 5
                                        else:
                                            break
                        # tile_tab = pathfinding(map_data,start,tile_destination.getNumtile(),True)
                        # for k in range(len(tile_tab)):
                        #    y,x = tile_tab[k]
                        #    tile_tab[k] = [x,y]
                        #    map_data[x][y] = 5

                    if spell_type == "square":
                        x, y = tile_destination.getNumtile()
                        if spell_range == 0:
                            self.highlightedTiles.append([x, y])
                            if self.map_data[x][y] == 3:
                                self.map_data[x][y] = 5
                        else:
                            for i in range(x - spell_range, x + spell_range + 1):
                                for j in range(y - spell_range, y + spell_range + 1):
                                    if (0 <= i < self.MAP_SIZE) and (
                                        0 <= j < self.MAP_SIZE
                                    ):
                                        self.highlightedTiles.append([i, j])
                                        if self.map_data[i][j] == 3:
                                            self.map_data[i][j] = 5

    def makeSpell(
        self, spell, autoattack=False, monster={}
    ):  # spell_type = 0 -> line  / spell_type = 1 -> square
        wait = 1
        # tile_touched = []
        # tile_dest = None

        spell_type = spell.type
        spell_range = spell.dmgRange
        spell_dmg = spell.dmg
        spell_size = (
            [(spell_range + 2) * 64 for _ in range(2)]
            if spell_type == "square"
            else (64, spell_range * 64)
        )
        targetsTouched = False

        while wait:
            pygame.event.clear()

            if (
                monster != {}
            ):  # Coor are passed in, the monster is in range of the player and hits him
                p1 = self.turn_based_fight.getEntityinQueue(0)
                wait = 0
                spell.loadTextures()
                spell.show(
                    self.map_tile[monster["playerCoor"][0]][
                        monster["playerCoor"][1]
                    ].getTilecenter(),
                    spell_size,
                    self.update,
                )

                for (x, y) in [
                    (monster["monsterCoor"][0] + k, monster["monsterCoor"][1] + l)
                    for k in range(-1, 2)
                    for l in range(-1, 2)
                    if 0 <= monster["monsterCoor"][0] + k < len(self.map_tile)
                    if 0 <= monster["monsterCoor"][1] + l < len(self.map_tile)
                ]:
                    if isinstance(self.map_tile[x][y].getEntity(), Character):
                        p2 = self.map_tile[x][y].getEntity()
                        actualDmg = int(
                            p1.stats["ATK"] // 2
                            + p1.stats["ATK"] * random.randint(1, 5) / 5
                        )
                        self.Game.combatLog.rollDice(5, actionName="DMG")
                        if actualDmg >= 1.25 * p1.stats["ATK"]:
                            self.Game.combatLog.addText(
                                f"{p1._fightName} did a critical shot !"
                            )
                        self.Game.combatLog.addText(
                            f"{p1._fightName} touched {p2._fightName} with a {spell.name}, doing {actualDmg} damages !"
                        )
                        p2.modifyHP(-actualDmg)
                        self.stats[p1._fightName] += actualDmg

                        # delete the entity if HP == 0
                        if p2.stats["HP"] <= 0:
                            for k in range(len(self.sprite_list)):
                                if p2._fightId == self.sprite_list[k]._fightId:
                                    self.sprite_list.pop(k)
                                    break
                            self.Game.combatLog.addText(f"{p2._fightName} died !")
                            self.turn_based_fight.removeEntity(p2._fightId)
                            self.setEntityonTile(self.map_tile[x][y].getNumtile(), None)
                            if self.turn_based_fight.isended():
                                if self.turn_based_fight.getFightresult():
                                    self.Game.combatLog.addText("Fight won")
                                else:
                                    self.Game.combatLog.addText("Fight lose")
                                    self.fightResume.mainLoop()
                continue

            for event in pygame.event.get():
                if event.type == MOUSEMOTION:
                    self.spellhighlight(spell_type, spell_range)
                    self.update()

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.centerTileOnMouse != None
                    and self.highlightedTiles != []
                ):
                    wait = 0
                    p1 = self.turn_based_fight.getEntityinQueue(0)
                    spell.show(
                        self.centerTileOnMouse.getTilecenter(),
                        spell_size,
                        self.update,
                    )
                    for k in range(len(self.highlightedTiles)):
                        x, y = self.highlightedTiles[k]
                        if isinstance(
                            self.map_tile[x][y].getEntity(), Ennemy
                        ) or isinstance(self.map_tile[x][y].getEntity(), Character):
                            targetsTouched = True
                            p2 = self.map_tile[x][y].getEntity()
                            if not autoattack:
                                actualDmg = int(
                                    spell_dmg // 2
                                    + spell_dmg
                                    * random.randint(p1.stats["STR"], 100)
                                    / 100
                                )
                                self.Game.combatLog.rollDice(100, actionName="SPELL")
                                if actualDmg >= 1.25 * spell_dmg:
                                    self.Game.combatLog.addText(
                                        f"{p1._fightName} did a critical shot !"
                                    )
                                self.Game.combatLog.addText(
                                    f"{p1._fightName} cast the spell {spell.name} on {p2._fightName}, doing {actualDmg} damages !"
                                )
                                p2.modifyHP(-actualDmg)
                                self.stats[p1._fightName] += actualDmg
                            else:
                                actualDmg = int(
                                    p1.stats["ATK"] // 2
                                    + p1.stats["ATK"] * random.randint(1, 5) / 5
                                )
                                self.Game.combatLog.rollDice(5, actionName="DMG")
                                if actualDmg >= 1.25 * p1.stats["ATK"]:
                                    self.Game.combatLog.addText(
                                        f"{p1._fightName} did a critical shot !"
                                    )
                                self.Game.combatLog.addText(
                                    f"{p1._fightName} touched {p2._fightName} with a {spell.name}, doing {actualDmg} damages !"
                                )
                                p2.modifyHP(-actualDmg)
                                self.stats[p1._fightName] += actualDmg
                            # If the player is taking / doing damages, rest mechanics is reseted
                            if isinstance(p2, Character):
                                p2.lastedTurnRest = 1
                            elif isinstance(p1, Character):
                                p1.lastedTurnRest = 1

                            # delete the entity if HP == 0
                            if p2.stats["HP"] <= 0:
                                for k in range(len(self.sprite_list)):
                                    if p2._fightId == self.sprite_list[k]._fightId:
                                        self.sprite_list.pop(k)
                                        break
                                self.Game.combatLog.addText(f"{p2._fightName} died !")
                                self.turn_based_fight.removeEntity(p2._fightId)
                                self.setEntityonTile(
                                    self.map_tile[x][y].getNumtile(), None
                                )
                                if self.turn_based_fight.isended():
                                    if self.turn_based_fight.getFightresult():
                                        self.Game.combatLog.addText("Fight won")
                                    else:
                                        self.Game.combatLog.addText("Fight lose")
                                    self.fightResume.mainLoop()

                    pygame.event.clear()
                    if not targetsTouched:
                        self.Game.combatLog.addText(
                            f"{p1._fightName}'s attack missed !"
                        )

    def endFight(self):
        self.open = False

        # TODO : loot items onto player's inventory
        for entity in self.initalEntityList:
            if isinstance(entity, Ennemy):
                for Hero in self.Heroes:
                    Hero.stats["Money"] += entity.goldValue
                    # Get a bonus XP for each mob if the player is the MVP
                    if self.stats[Hero._fightName] == max([self.stats.values()]):
                        logger.info(
                            f"{Hero._fightName} gains a special amount of XP because he is the MVP !"
                        )
                        Hero.addExp(2 * entity.XP)
                    else:
                        Hero.addExp(entity.XP)

                    itemPlaced = False
                    for j in range(HUDConf.INVENTORY_STORAGE_HEIGHT):
                        for i in range(HUDConf.INVENTORY_STORAGE_WIDTH):
                            if (
                                Hero.Inventory.storage["tab"][j][i] == None
                                and not itemPlaced
                            ):
                                Hero.Inventory.storage["tab"][j][i] = entity.loot
                                Hero.Inventory.storage["tab"][j][i].setCoor(
                                    (
                                        Hero.Inventory.storage["initPoint"][0]
                                        + i * Hero.Inventory.storage["offset"][0],
                                        Hero.Inventory.storage["initPoint"][1]
                                        + j * Hero.Inventory.storage["offset"][1],
                                    )
                                )
                                itemPlaced = True

                    logger.info(
                        f"Added : {entity.loot.property['name']}, {entity.goldValue} golds and {entity.XP} xp to the Hero !"
                    )

                    if not itemPlaced:

                        Dialog(
                            "You've got not enough money to buy this item.",
                            (self.Game.resolution // 2, self.Game.resolution // 2),
                            self.Game.screen,
                            (255, 0, 0),
                            self.Game,
                            error=True,
                            charLimit=100,
                        ).mainShow()

                self.stats = {}
                self.initalEntityList = []

    def mainLoop(self):

        self.update()
        while self.open:

            # --------- Monster behaviour ----------- #
            if isinstance(self.turn_based_fight.getEntityinQueue(0), Ennemy):
                ennemyInstance = None
                for movable_sprite in self.sprite_list:
                    if (
                        self.turn_based_fight.getEntityinQueue(0)._fightId
                        == movable_sprite._fightId
                    ):
                        ennemyInstance = movable_sprite

                        char_tab = []
                        # Fetching Character
                        for movable_sprite in self.sprite_list:

                            if isinstance(movable_sprite.entity, Character):
                                char_tab.append(movable_sprite)

                        selectedChar = random.choice(char_tab)
                        if (
                            math.sqrt(
                                sum(
                                    [
                                        (coor1 - coor2) ** 2
                                        for coor1, coor2 in zip(
                                            selectedChar._numtilepos,
                                            ennemyInstance._numtilepos,
                                        )
                                    ],
                                )
                            )
                            <= 1
                        ):
                            # Simulate an autoattack
                            self.makeSpell(
                                spellsConf.SPELL_DB[0],
                                autoattack=True,
                                monster={
                                    "monsterCoor": ennemyInstance._numtilepos,
                                    "playerCoor": selectedChar._numtilepos,
                                },
                            )
                        elif (
                            math.sqrt(
                                sum(
                                    [
                                        (coor1 - coor2) ** 2
                                        for coor1, coor2 in zip(
                                            selectedChar._numtilepos,
                                            ennemyInstance._numtilepos,
                                        )
                                    ],
                                )
                            )
                            <= selectedChar.MOVE_LIMIT
                        ):
                            rand_pos = [
                                elt + randomCoor
                                if 0 <= elt + randomCoor < self.MAP_SIZE
                                else elt
                                for elt, randomCoor in zip(
                                    selectedChar._numtilepos,
                                    random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)]),
                                )
                            ]
                            while not self.map_tile[rand_pos[0]][
                                rand_pos[1]
                            ].getAccess():
                                rand_pos = [
                                    elt + randomCoor
                                    if 0 <= elt + randomCoor < self.MAP_SIZE
                                    else elt
                                    for elt, randomCoor in zip(
                                        selectedChar._numtilepos,
                                        random.choice(
                                            [(0, 1), (1, 0), (-1, 0), (0, -1)]
                                        ),
                                    )
                                ]
                            ennemyInstance.move(self.map_tile[rand_pos[0]][rand_pos[1]])
                        else:  # Player is too far away
                            x, y = (
                                random.randint(1, self.MAP_SIZE),
                                random.randint(1, self.MAP_SIZE),
                            )
                            while not self.map_tile[x][y].getAccess():
                                x, y = (
                                    random.randint(1, self.MAP_SIZE),
                                    random.randint(1, self.MAP_SIZE),
                                )
                            ennemyInstance.move(self.map_tile[x][y])

                        self.turn_based_fight.rotation()
                        break
                continue

            for event in pygame.event.get():

                # deplacement
                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button in [4, 5]:
                        self.Game.combatLog.update(event)
                        self.update()
                    if event.button == 1:
                        for tilerow_nb, tilerow in enumerate(
                            self.map_tile
                        ):  # for every row of the map...
                            for tilecol_nb, x in enumerate(tilerow):
                                tile_destination = self.map_tile[tilerow_nb][tilecol_nb]

                                if tile_destination.ismouseontile() and (
                                    not tile_destination.getAccess()
                                ):
                                    self.Game.combatLog.addText(
                                        f"Something is blocking the way ... {self.turn_based_fight.getEntityinQueue(0)._fightName}'s move is canceled !"
                                    )
                                    self.turn_based_fight.rotation()
                                elif tile_destination.ismouseontile():

                                    id_turn = self.turn_based_fight.getEntityinQueue(
                                        0
                                    )._fightId
                                    for k in range(len(self.sprite_list)):
                                        if self.sprite_list[k]._fightId == id_turn:
                                            self.sprite_list[k].move(tile_destination)
                                            self.turn_based_fight.rotation()
                                            break

                if event.type == KEYDOWN:

                    if event.key == self.Game.KeyBindings["Toggle Spell Book"]["value"]:
                        self.turn_based_fight.getEntityinQueue(0).SpellBook.show(
                            combatMode=True
                        )
                        self.turn_based_fight.rotation()
                    if event.key == K_a:
                        self.Game.combatLog.reset()

                # quit
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

        self.transition()
        if self.Game.heroesGroup[0].currentPlace == "building":
            self.Game.musicController.setMusic("dungeon")
        elif self.Game.heroesGroup[0].currentPlace == "openWorld":
            self.Game.musicController.setMusic("openWorld")
        self.resetFight()
        self.Game.cursor.show()
