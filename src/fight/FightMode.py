import math
import os
from numpy.lib.arraysetops import isin
import pygame
import random
from math import floor, hypot
from pygame.locals import *
import sys
from fight.jordanask import basic_checkevent, load_map, draw_text
from fight.Case import Case
from fight.load_img import collide, case_select,explosion
from gameObjects.Ennemy import Ennemy
from Player.Character import Character
from gameController import GameController
import time
import json


class FightMode:
    def __init__(self, gameController) -> None:
        self.Game = gameController
        self.l = load_map("./fight/map2.txt")
        self.asset_path = "./assets/fight"
        self.battleground = pygame.transform.scale(
            pygame.image.load(f"{self.asset_path}/wine-wang-sunshineforest-1.jpg"),
            (self.Game.screen.get_width(), self.Game.screen.get_height()),
        )
        self.list_case = []
        self.list_tour = []
        self.mask_collide = pygame.mask.from_surface(collide)
        self.online_fight = False
        souris_surf = pygame.Surface((1, 1))
        souris_surf.fill((5, 5, 5))
        souris_surf.set_colorkey((0, 0, 0))
        #   pixel_red.set_alpha(0)
        self.souris_mask = pygame.mask.from_surface(souris_surf)

        self.list_player = []
        self.list_monster = []

    def create_map(self):
        self.Game.screen.fill((0, 0, 0))
        self.Game.screen.blit(self.battleground, (0, 0))

    def display_battle(self):
        self.create_map()
        # Gestion Tours
        self.current_player().select(True)
        for x in self.list_case:
            self.Game.screen.blit(x.display, x.cordo())
           
            x.checkIfSelected()

            x.print_contains()
            if x.in_case != None:
                x.in_case.type_animation = "idle"
                x.in_case.animate()
                x.in_case.update_hp_bar(
                    self.Game.screen,
                    x.cordo()[0] + 25,
                    x.cordo()[1] - x.in_case.img.get_height() // 2,
                    x.in_case.stats["HP"],
                    x.in_case.stats["HP_max"],
                )
        # for x in self.list_tour:
        # trouver_case = x.trouver_case(self.list_case).cordo()
        # coordX = trouver_case[0]+x.img.get_width()//2
        # coordY= trouver_case[1] -x.img.get_height()//2
        # if(isinstance(x,Character)):
        #    x.display_classe(self.Game.screen,coordX,coordY)
        # x.display_lvl(screen,x.trouver_case(self.list_case).cordo()[0]+x.img.get_width()//2,x.trouver_case(self.list_case).cordo()[1]-x.img.get_height()//2)

        self.Game.chat_box.update()
        self.Game.chat_box.draw()

    def initFight(self, entityList):
        # pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        # pygame.mouse.set_visible(True)
        running = True
        click = False
        i, j = 0, 0

        for h in self.l:
            j = 0
            for g in h:
                if self.l[i][j] == "w":
                    self.list_case.append(Case(i, j, self.Game))
                j += 1
            i += 1
        for case in self.list_case:
            case.in_case = None
        self.list_tour = entityList[::]
        i = 0
        for entity in entityList:
            self.list_case[i].in_case = entity
            if isinstance(entity, Character):
                self.list_player.append(entity)
                if entity.is_playable == False:
                    self.online_fight = True
            i += 1

        i = 0
        case_select.set_alpha(50)
        combat = True
        while combat:
            if isinstance(self.list_tour[0], Character):
                if self.list_tour[0].is_playable:
                    self.mouvement_turn()
                    self.action_turn()
                else:
                    self.other_player_turn()
                self.next_round()
            else:
                self.IA_action()
        # PIECCE A REPRENDRE
        """
        self.initalEntityList = entityList[::]
        for entity in entityList:
            if isinstance(entity, Character):
                self.Heroes.append(entity)
                break
            if isinstance(entity, Enemy):
                self.
                """

    def mouvement_turn(self):
        current_selec = self.current_player()
        current_selec.select_neighbour(self.list_case, k=1)

        self.Game.chat_box.write_log(
            ("white", "Mouvement turn of " + current_selec.in_case.name)
        )
        running = True
        click = False
        taille = 2
        while running:

            self.display_battle()
            if taille < 100:
                Font = pygame.font.Font(
                    "./assets/fonts/Elvish/Dungeons.ttf", int(taille)
                )
                size_x, size_y = Font.size("Mouvement turn")
                taille += 0.7
                draw_text(
                    "Mouvement turn",
                    Font,
                    (255, 255, 255),
                    self.Game.screen,
                    self.Game.screen.get_width() // 2 - size_x // 2,
                    self.Game.screen.get_height() // 2 - size_y,
                )
            else:
                Font = pygame.font.Font("./assets/fonts/Elvish/Dungeons.ttf", 40)
                size_x, size_y = Font.size("Mouvement turn")
                draw_text(
                    "Mouvement turn", Font, (255, 255, 255), self.Game.screen, 0, size_y
                )

            running, click = basic_checkevent(click)
            mx, my = pygame.mouse.get_pos()
            i, j = 0, 0
            for h in self.l:
                j = 0
                for g in h:
                    if self.l[i][j] == "w":
                        if self.mask_collide.overlap(
                            self.souris_mask,
                            (
                                (
                                    mx
                                    - (
                                        (j - i) * (collide.get_width() + 45) // 2
                                        + self.Game.screen.get_width() // 2
                                        - collide.get_width() // 2
                                    ),
                                    my
                                    - ((j + i) * (collide.get_width() + 45) // 4 + 150),
                                )
                            ),
                        ):
                            if click:
                                for x in self.list_case:
                                    if x.i == i and x.j == j:
                                        if (
                                            current_selec != None
                                            and current_selec.in_case != None
                                        ):
                                            if x.is_select and x.in_case == None:
                                                self.print_anim(
                                                    current_selec, x, self.list_case
                                                )
                                                x.in_case = current_selec.in_case
                                                current_selec.in_case = None
                                                if self.online_fight:
                                                    self.broadcast_info(
                                                        [
                                                            i._fightId
                                                            for i in self.list_player
                                                        ],
                                                        "MOUVEMENT",
                                                    )
                                            current_selec = x
                                            self.reset_select()
                                            running = False
                    j += 1
                i += 1

            self.Game.show()
        self.reset_select()

    def action_turn(self):
        running = True
        click = False
        current_selec = self.current_player()
        self.Game.chat_box.write_log(
            ("white", "Action turn of " + current_selec.in_case.name)
        )
        self.current_player().select_neighbour(self.list_case)
        taille = 0
        while running:
            self.display_battle()
            if taille < 100:
                Font = pygame.font.Font(
                    "./assets/fonts/Elvish/Dungeons.ttf", int(taille)
                )
                size_x, size_y = Font.size("Action turn")
                taille += 0.7
                draw_text(
                    "Action turn",
                    Font,
                    (255, 255, 255),
                    self.Game.screen,
                    self.Game.screen.get_width() // 2 - size_x // 2,
                    self.Game.screen.get_height() // 2 - size_y,
                )
            else:
                Font = pygame.font.Font("./assets/fonts/Elvish/Dungeons.ttf", 40)
                size_x, size_y = Font.size("Action turn")
                draw_text(
                    "Action turn", Font, (255, 255, 255), self.Game.screen, 0, size_y
                )

            
            running, click = basic_checkevent(click)
            mx, my = pygame.mouse.get_pos()
            i, j = 0, 0
            for h in self.l:
                j = 0
                for g in h:
                    if self.l[i][j] == "w":
                        if self.mask_collide.overlap(
                            self.souris_mask,
                            (
                                (
                                    mx
                                    - (
                                        (j - i) * (collide.get_width() + 45) // 2
                                        + self.Game.screen.get_width() // 2
                                        - collide.get_width() // 2
                                    ),
                                    my
                                    - ((j + i) * (collide.get_width() + 45) // 4 + 150),
                                )
                            ),
                        ):
                            if click:
                                for x in self.list_case:
                                    if x.i == i and x.j == j:
                                        if (
                                            current_selec != None
                                            and current_selec.in_case != None
                                        ):
                                            if x.is_select and x.in_case != None:
                                                self.lunch_attack(x)
                                                if self.online_fight:
                                                    self.broadcast_info(
                                                        [
                                                            x.in_case._fightId
                                                        ],
                                                        "ATTACK",
                                                    )
                                                
                                            current_selec = x
                                            self.reset_select()
                                            

                                            running = False
                                
                    j += 1
                i += 1
            self.Game.show()
        
        self.reset_select()
        

    # FIN COMBAT :
    """
        self.transition()
        if self.Game.heroesGroup[0].currentPlace == "building":
            self.Game.musicController.setMusic("dungeon")
        elif self.Game.heroesGroup[0].currentPlace == "openWorld":
            self.Game.musicController.setMusic("openWorld")
        self.resetFight()
        self.Game.cursor.show()
"""

    def print_anim(self, case1, case2, list_case, anim_type="walk", mouvement=True):
        running = True
        i = 0
        j = 0
        complete = False
        dist = case1.cordo()[0] - case2.cordo()[0]
        dist_2 = case1.cordo()[1] - case2.cordo()[1]
        running = True
        click = False
        self.reset_select()
        while running:
            self.create_map()
            for x in list_case:
                self.Game.screen.blit(x.display, x.cordo())
                x.checkIfSelected()
                if x != case1:
                    x.print_contains()
                    if x.in_case != None:
                        x.in_case.type_animation = "idle"
                        x.in_case.animate()
            case1.in_case.type_animation = anim_type
            if anim_type == "ranged" or anim_type == "attack":
                complete = case1.in_case.animate_attack()
            else:
                complete = case1.in_case.animate()
            if mouvement:
                if dist > 0:
                    i += 5
                    if i > dist:
                        i = dist
                else:
                    i -= 5
                    if i < dist:
                        i = dist
                if dist_2 > 0:
                    j += 5
                    if j > dist_2:
                        j = dist_2
                else:
                    j -= 5
                    if j < dist_2:
                        j = dist_2
            if dist > 0:
                case1.print_contains(x=-i, y=-j)
            else:
                case1.print_contains(flip=False, x=-i, y=-j)
            self.Game.show()
            if mouvement:
                if abs(i) >= abs(dist) and abs(j) >= abs(dist_2):
                    running = False
                else:
                    running, click = basic_checkevent(click)
            else:
                if complete:
                    running = False
                else:
                    running, click = basic_checkevent(click)

    def next_round(self):
        self.list_tour.append(self.list_tour[0])
        self.list_tour.remove(self.list_tour[0])

    def reset_select(self):
        for x in self.list_case:
            x.select(False)

    def current_player(self):
        for x in self.list_case:
            if x.in_case == self.list_tour[0]:
                return x
        return None

    def IA_action(self):
        have_attacked = False
        current_not_playable = self.list_tour[0]
        case_monstre = current_not_playable.trouver_case(self.list_case)
        case_monstre.select_neighbour(self.list_case)
        for player in self.list_player:
            if player.trouver_case(self.list_case).is_select:
                self.lunch_attack(player.trouver_case(self.list_case))
                have_attacked = True
                break
        self.reset_select()

        if not have_attacked:
            # Trouver le joueur le plus pret
            if self.game.player.hp > 0:
                distance = self.find_distance(
                    self.game.player.trouver_case(self.list_case), case_monstre
                )
                nearest = self.game.player
            else:
                distance = 10000
            for x in self.game.player.crew_mate:
                if x.hp > 0:
                    if (
                        self.find_distance(x.trouver_case(self.list_case), case_monstre)
                        <= distance
                    ):
                        distance = self.find_distance(
                            x.trouver_case(self.list_case), case_monstre
                        )

                        nearest = x
            nearest.trouver_case(self.list_case).select(True)
            # Se deplacer vers lui
            case_monstre.select_neighbour(self.list_case, k=1)
            distance_case = 15000
            for x in self.list_case:
                if x.is_select and x.in_case == None:
                    if (
                        self.find_distance(x, nearest.trouver_case(self.list_case))
                        < distance_case
                    ):
                        distance_case = self.find_distance(
                            x, nearest.trouver_case(self.list_case)
                        )
                        nearest_case = x

            self.print_anim(case_monstre, nearest_case, anim_type="walk")
            nearest_case.in_case = current_not_playable
            case_monstre.in_case = None

            self.reset_select()
            nearest_case.select_neighbour(self.list_case, k=0)
            if self.game.player.trouver_case(self.list_case).is_select:
                self.lunch_attack(self.game.player.trouver_case(self.list_case))
                have_attacked = True
            if not have_attacked:
                for x in self.player.crew_mate:
                    if x.hp > 0:
                        if x.trouver_case(self.list_case).is_select:
                            self.lunch_attack(x.trouver_case(self.list_case))
                            have_attacked = True
            self.reset_select()
            

    def other_player_turn(self):
        running = True
        Font = pygame.font.Font("./assets/fonts/Elvish/Dungeons.ttf", 40)
        size_x, size_y = Font.size("Wait for the other player.")
        pending = 0
        click = False
        time_line = 0
        while running:
            self.display_battle()
            running, click = basic_checkevent(click)

            if int(pending) == 0:
                draw_text(
                    "Wait for the other player.",
                    Font,
                    (255, 255, 255),
                    self.Game.screen,
                    self.Game.screen.get_width() // 2 - size_x // 2,
                    self.Game.screen.get_height() // 2 - size_y,
                )
            if int(pending) == 1:
                draw_text(
                    "Wait for the other player..",
                    Font,
                    (255, 255, 255),
                    self.Game.screen,
                    self.Game.screen.get_width() // 2 - size_x // 2,
                    self.Game.screen.get_height() // 2 - size_y,
                )
            if int(pending) == 2:
                draw_text(
                    "Wait for the other player...",
                    Font,
                    (255, 255, 255),
                    self.Game.screen,
                    self.Game.screen.get_width() // 2 - size_x // 2,
                    self.Game.screen.get_height() // 2 - size_y,
                )
            pending += 0.01
            pending = pending % 3
            datas = json.load(open("datas.json"))
            combat = json.load(open("combat.json"))
            if (
                datas["player"][str(self.list_tour[0]._fightId)]["action_type"]
                == "MOUVEMENT"
            ):
                if datas["player"][str(self.list_tour[0]._fightId)][
                    "dest"
                ] != self.list_tour[0].trouver_case(self.list_case).numero_case(
                    self.list_case
                ):
                    self.print_anim(
                        self.list_tour[0].trouver_case(self.list_case),
                        self.list_case[
                            datas["player"][str(self.list_tour[0]._fightId)]["dest"]
                        ],
                        self.list_case,
                    )
                    self.list_case[
                        datas["player"][str(self.list_tour[0]._fightId)]["dest"]
                    ].in_case = self.list_tour[0]
                    self.list_tour[0].trouver_case(self.list_case).in_case = None
                    running = False
            
            # for x in combat["player"]:
            #     self.lunch_attack(self.list_case[int(x["dest"])])
            self.Game.show()

    def lunch_attack(self, defenseur):
        self.Game.chat_box.write_log(
            (
                "red",
                self.current_player().in_case.name
                + " attack "
                + defenseur.in_case.name,
            )
        )
        # self.print_anim(
        #     self.current_player(),
        #     defenseur,
        #     self.list_case,
        #     anim_type="attack",
        #     mouvement=False,
        # )
        damages = 1
        self.Game.chat_box.write_log(("red", "Dammage : " + str(damages)))
        self.print_explosion(defenseur,"dmg")

        defenseur.in_case.stats["HP"] -= damages
        if defenseur.in_case.stats["HP"] <= 0:
            self.list_tour.remove(defenseur.in_case)
            defenseur.in_case = None
        self.broadcast_info([defenseur.in_case._fightId],"ATTACK")
        self.reset_select()

    def print_explosion(self, case, which_explosion="dmg"):
        running = True
        click = False
        complete = False
        i = 1
        while running:
            self.display_battle()
            running, click = basic_checkevent(click)
            if which_explosion == "dmg":
                self.Game.screen.blit(
                    explosion["explosion_" + str(i) + ".png"],
                    (
                       
                        case.cordo()[0]
                        - explosion["explosion_" + str(i) + ".png"].get_width() // 3,
                        case.cordo()[1]
                        - int(
                            explosion["explosion_" + str(i) + ".png"].get_height()
                            // 2.5
                        ),
                    ),
                )
                if i >= 46:
                    running=False
                i += 1
            self.Game.show()
            # else:
            #     if i < 10:
            #         screen.blit(
            #             explosion_heal["explosion000" + str(i) + ".png"],
            #             (
            #                 case.cordo()[0]
            #                 - explosion_heal[
            #                     "explosion000" + str(i) + ".png"
            #                 ].get_width()
            #                 // 3,
            #                 case.cordo()[1]
            #                 - int(
            #                     explosion_heal[
            #                         "explosion000" + str(i) + ".png"
            #                     ].get_height()
            #                     // 2.5
            #                 ),
            #             ),
            #         )

            #     else:
            #         screen.blit(
            #             explosion_heal["explosion00" + str(i) + ".png"],
            #             (
            #                 case.cordo()[0]
            #                 - explosion_heal[
            #                     "explosion00" + str(i) + ".png"
            #                 ].get_width()
            #                 // 3,
            #                 case.cordo()[1]
            #                 - int(
            #                     explosion_heal[
            #                         "explosion00" + str(i) + ".png"
            #                     ].get_height()
            #                     // 2.5
            #                 ),
            #             ),
            #         )
            #     if i >= 60:
            #         running = False
            
            

    def broadcast_info(self, player_id, action_type, award=None):
        send_dict = dict()
        send_dict["player"] = dict()
        if action_type == "MOUVEMENT":
            for _id in player_id:
                for x in self.list_player:
                    if x._fightId == _id:
                        dest = x.trouver_case(self.list_case).numero_case(
                            self.list_case
                        )

                send_dict["player"][_id] = {
                    "action_type": action_type,
                    "dest": dest,
                }
            with open("./datas.json", "w") as f:
                json.dump(send_dict, f)
        if action_type == "ATTACK":
            for _id in player_id:
                for x in self.list_tour:
                    if x._fightId == _id:
                        dest = x.trouver_case(self.list_case).numero_case(
                            self.list_case
                        )

                send_dict["player"][_id] = {
                    "action_type": action_type,
                    "dest": dest,
                }
            with open("./combat.json", "w") as f:
                json.dump(send_dict, f)
            """ AJOUTER UPDATE CARACT"""
        if action_type == "SPELL":
            pass
            """ AJOUTER UPDATE CARACT POUR TOUT LES JOUEURS ID"""

        



# test_2.initFight([])
