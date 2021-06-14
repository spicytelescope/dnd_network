import pygame
import os
from settings.screen import *
from settings.police import *
from settings.load_img import *
from settings.color import *
from fonction import *
from case import *
from DiceEvent import *
#from monstre import *  # a remplacer plus tard
from personnage import *
from text import *
from settings.load_img import *
from script import list_mooving_entity, list_static_entity
from sorcerer import *
import math
import random
from rogue import Rogue
clock = pygame.time.Clock()
# Message pour Christine: 
#   Pour print sur le log: 
# self.chat_box.write_log(("combat", "You play an attack!"))
# gardes le mot "combat", change le message ("You play an attack")
# Il faut que l'argument soit un tuple
pixel_mask = pygame.mask.from_surface(pixel_red)
souris_surf = pygame.Surface((1, 1))
souris_surf.fill(RED)
souris_surf.set_colorkey(BLACK)
souris_mask = pygame.mask.from_surface(souris_surf)
#pixel_red.set_alpha(0)
pixel_red.set_colorkey(BLACK)

class Combat:

    def __init__(self, game,list_monstre):
        self.game = game
        self.chat_box = self.game.chat_box
        self.perso1 = self.game.player
        self.liste_monstre = list_monstre
        self.player = self.game.player
        self.list_tour = []

        self.map = None
        self.mask = None

        self.select_menu = False
        self.select_attack = False
        self.select_sort = False
        self.select_monster = False
        self.mouvement = False
        self.select_bonus = -1
        self.select_menu_bonus = False
        self.select_spell = -1

        
    def print_battleground(self):
        screen.fill(BLACK)
        screen.blit(pygame.transform.scale(fond,(screen.get_width(),screen.get_height())), (0, 0))
    def affichage(self):
        global list_case
        running = True
        case.set_colorkey(WHITE)
        l = load_map('map2.txt')
        case_select.set_alpha(100)
        list_case = []
        
        transition = pygame.Surface((screen.get_width(), screen.get_height()))
        transition.set_colorkey(BLACK)
        transition.fill((0, 0, 0))
        f = 0
        current_selec = None
        i, j = 0, 0

        for h in l:
            j = 0
            for g in h:
                if l[i][j] == 'w':
                    list_case.append(Case(i, j))
                j += 1
            i += 1

        i = 5
        for x in self.liste_monstre:
            i += randrange(0,4)
            self.list_tour.append(x)
            while list_case[i].in_case != None:
                i += randrange(-4,4)
            list_case[i].in_case = x
            
        if self.game.player.hp > 0:
            list_case[59].in_case = self.game.player
            self.list_tour.append(self.game.player)
            self.player.transform_display_for_combat()
        if self.game.player.crew_mate[1].hp > 0:
            list_case[65].in_case = self.game.player.crew_mate[0]
            self.list_tour.append(self.game.player.crew_mate[0])
            self.player.crew_mate[0].transform_display_for_combat()
        if self.game.player.crew_mate[1].hp > 0:
            list_case[51].in_case = self.game.player.crew_mate[1]
            self.list_tour.append(self.game.player.crew_mate[1])
            self.player.crew_mate[1].transform_display_for_combat()

        #VOIR TOUT LES MONSTRES
        self.nb_monstres= len(self.liste_monstre)
        

        
        self.chat_box.write_log(("combat", "You enter into battle !"))
        self.chat_box.write_log(("info", "Generation des tours :"))



        self.list_tour.sort(key=lambda x:x.DEX,reverse=True)
        
        
        

        self.map = l
        self.mask = souris_mask
        while running:
            #print(self.show_which_one_play().in_case.level)
            mx, my = pygame.mouse.get_pos()
            self.print_battleground()
            # Gestion Tours
            i = 0
            self.show_which_one_play().select(True)
            for x in list_case:
                screen.blit(x.display, x.cordo())
                x.checkIfSelected()
                
                x.print_contains()
                if x.in_case != None:
                    x.in_case.type_animation = "idle"
                    x.in_case.animate()

            for x in self.list_tour:
                trouver_case = x.trouver_case(list_case).cordo()
                coordX = trouver_case[0]+x.img.get_width()//2
                coordY= trouver_case[1] -x.img.get_height()//2
                if(isinstance(x,Perso)):
                    x.display_classe(screen,coordX,coordY)
                #x.display_lvl(screen,x.trouver_case(list_case).cordo()[0]+x.img.get_width()//2,x.trouver_case(list_case).cordo()[1]-x.img.get_height()//2)
                x.update_hp_bar(screen,coordX,coordY)
            if self.mouvement:
                i, j = 0, 0
                for h in l:
                    j = 0
                    for g in h:
                        if l[i][j] == 'w':
                            if pixel_mask.overlap(souris_mask, ((mx-((j-i)*(pixel_red.get_width()+45)//2+screen.get_width()//2-pixel_red.get_width()//2), my-((j+i)*(pixel_red.get_width()+45)//4-100)))):
                                if self.game.click:
                                    for x in list_case:
                                        if x.i == i and x.j == j:
                                            if current_selec != None and current_selec.in_case != None:
                                                if x.is_select and x.in_case == None:
                                                    self.print_anim(current_selec,x,list_case)
                                                    x.in_case = current_selec.in_case
                                                    current_selec.in_case = None
                                                    x.in_case.have_mouve = True
                                                    self.chat_box.write_log(("combat", self.show_which_one_play().in_case.name + " se deplace vers la case " + str(x.numero_case(list_case)) )) 
                                            current_selec = x
                                            self.reset_select(list_case)


                        j += 1
                    i += 1
             
            # FPS
            
            current_selec = self.show_which_one_play()
            
            monster_alive = False
            player_alive = False
            for x in self.list_tour:
                if x.hp <=0:
                    self.list_tour.remove(x)
                    try :
                        self.list_case.remove(x)
                    except:
                        pass
                else:
                    if x.is_player:
                        player_alive = True
                    else:
                        monster_alive = True
            if not player_alive or not monster_alive:
                running = False
            else:
                self.menu_action()
                running, self.game.click = basic_checkevent(self.game.click,self.game)
                
            #update + draw chatbox
            self.game.chat_box.update()
            self.game.chat_box.draw()
            print_turn_batlle(self.list_tour)
            pygame.display.update()
            self.game.clock.tick(64)

            
            # if f != 255:
            #     for x in range(255):
            #         f+=0.008
            #         transition.set_alpha(int(255-f))
            #     screen.blit(transition,(0,0))
    def print_explosion(self,case,which_explosion="dmg"):
        running = True
        complete = False
        i=1
        while running:
            self.print_battleground()
            running,self.game.click=  basic_checkevent(self.game.click)  
            for x in list_case:
                screen.blit(x.display, x.cordo())
                x.checkIfSelected()
                x.print_contains()
                if x.in_case != None:
                    x.in_case.type_animation = "idle"
                    x.in_case.animate()
            if which_explosion == "dmg":
                screen.blit(explosion["explosion_"+str(i)+".png"],(case.cordo()[0]-explosion["explosion_"+str(i)+".png"].get_width()//3,case.cordo()[1]-int(explosion["explosion_"+str(i)+".png"].get_height()//2.5)))
                if i >= 46:
                    running = False
            else:
                if i < 10:
                   screen.blit(explosion_heal["explosion000"+str(i)+".png"],(case.cordo()[0]-explosion_heal["explosion000"+str(i)+".png"].get_width()//3,case.cordo()[1]-int(explosion_heal["explosion000"+str(i)+".png"].get_height()//2.5)))
                
                else:
                    screen.blit(explosion_heal["explosion00"+str(i)+".png"],(case.cordo()[0]-explosion_heal["explosion00"+str(i)+".png"].get_width()//3,case.cordo()[1]-int(explosion_heal["explosion00"+str(i)+".png"].get_height()//2.5)))
                if i >= 60:
                    running = False
            i+=1
            pygame.display.update()
            
            
    def print_anim(self,case1,case2,list_case,anim_type="walk_right",mouvement=True):
        running = True
        i=0
        j=0
        complete = False
        dist = case1.cordo()[0] - case2.cordo()[0]
        dist_2 =  case1.cordo()[1] - case2.cordo()[1]
        self.reset_select(list_case)
        while running:
            
            self.print_battleground()
            for x in list_case:
                
                screen.blit(x.display, x.cordo())
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
                if dist>0: 
                    i+= 5
                    if i > dist:
                        i = dist
                else:
                    i-=5
                    if i < dist:
                        i = dist
                if dist_2>0:
                    j+= 5
                    if j > dist_2:
                        j = dist_2
                else:
                    j-=5
                    if j < dist_2:
                        j = dist_2
            if dist > 0:
                case1.print_contains(x=-i,y=-j)
            else:
                case1.print_contains(flip=False,x=-i,y=-j)
            pygame.display.update()
            if mouvement:
                if abs(i) >= abs(dist) and abs(j) >= abs(dist_2):
                    running = False
                else:
                    running,self.game.click=  basic_checkevent(self.game.click, None)  
            else:
                if complete:
                    running = False
                else:
                    running,self.game.click=  basic_checkevent(self.game.click)  
    def menu_action(self):
        display_erreur = pygame.Surface((screen.get_width(),screen.get_height()))

        if self.list_tour[0].is_player:
            if self.list_tour[0].actionP ==0:
                self.reset_select(list_case)
                self.next_round()

            else:
                current_playable = self.list_tour[0]

                if creation_img_text_click(img_next,"Choose what to do",ColderWeather,WHITE,screen,self.game.click,img_next.get_width(),img_next.get_height()//2):
                    self.select_menu = True
                    self.reset_select(list_case)
                    self.select_menu_bonus = False
                    self.select_attack = False
                    self.mouvement = False
                    self.select_sort = False
                    self.select_spell = -1
                    self.select_bonus = -1
                if self.select_menu:
                    if creation_img_text_click(img_next,"Cancel",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()*3,img_next.get_height()//2+600):
                        self.reset_select(list_case)
                        self.select_menu_bonus = False
                        self.select_attack = False
                        self.mouvement = False
                        self.select_menu = False
                        self.select_sort = False
                        self.select_spell = -1
                        self.select_bonus = -1
                    if creation_img_text_click(img_next,"Mouvement",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()*3,img_next.get_height()//2):
                        self.mouvement = True
                        if current_playable.actionP > 0 and current_playable.have_mouve == False :
                            self.show_which_one_play().select_neighbour(list_case,k=1)
                            self.select_menu = False
                        else:
                            board_error("Pas assez de point d'action")
                    if creation_img_text_click(img_next,"Attack",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()*3,img_next.get_height()//2+150):
                        self.select_attack = True
                        self.mouvement = False
                    if self.select_attack:
                        if creation_img_text_click(img_next,"Basic",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()*4.5,img_next.get_height()//2+150):
                            self.select_monster = True
                            self.select_menu = False
                        if creation_img_text_click(img_next,"Sort",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()*4.5,img_next.get_height()//2+300):
                            self.select_menu = False
                            self.select_attack = False
                            self.select_sort = True
                    if creation_img_text_click(img_next,"Bonus Action",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()*3,img_next.get_height()//2+300):
                        self.select_menu_bonus = True
                        self.select_menu = False
                        self.select_attack = False
                        self.game.click = False
                    
                    if creation_img_text_click(img_next,"Passez",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()*3,img_next.get_height()//2+450):
                        self.mouvement = False
                        self.reset_select(list_case)
                        self.next_round()
                        
                        self.select_menu = False
                
                if self.select_sort:
                    if self.show_which_one_play().in_case.classe != 'rogue':
                        key = self.show_which_one_play().in_case.spell.keys()
                        i=0
                        
                        for x in key:
                            if creation_img_text_click(img_next,x,ColderWeather,WHITE,screen,self.game.click,img_next.get_width()//2+screen.get_width()//2,img_next.get_height()//2+300*i):
                                
                                self.select_sort = False
                                self.select_spell = i
                            i+=1
                        if self.select_spell != -1:
                            self.lunch_spell()
                            self.select_spell = -1
                if self.select_menu_bonus:
                    if self.show_which_one_play().in_case.classe != 'rogue':
                        key = self.show_which_one_play().in_case.bonus.keys()
                        i=0
                        
                        for x in key:
                            if creation_img_text_click(img_next,x,ColderWeather,WHITE,screen,self.game.click,img_next.get_width()//2+screen.get_width()//2+100,img_next.get_height()//2+300*i):
                                self.select_menu_bonus = False
                                self.select_bonus = i
                            i+=1
                if self.select_bonus != -1:
                    if self.show_which_one_play().in_case.select_bonus(self.select_bonus):
                        if self.select_bonus ==0:
                            message = "convert sorcery points"
                        if self.select_bonus == 1:
                            message = "convert spells slots"
                        else:
                            message = "quickspell"
                        self.chat_box.write_log(("info", self.show_which_one_play().in_case.name + " use " + message))
                    self.select_bonus = -1
                    self.select_menu_bonus = False
                
                    """   
                    self.show_which_one_play().select_neighbour(list_case,k=spell_range)
                    list_in_range=[]
                    for x in list_case:
                        if x.in_case != None and x.is_select and not x.in_case.is_player:
                            list_in_range.append(x)
                    self.reset_select(list_case)
                    for x in list_in_range:
                        x.select(True)
                    self.show_which_one_play().select(False)
                    self.select_sort = False
                    """
                    

                    """

                    if creation_img_text_click(img_next,"Magic Missile",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()//2+screen.get_width()//2,img_next.get_height()//2+300):
                        self.show_which_one_play().select_neighbour(list_case,k=4)
                        list_in_range=[]
                        for x in list_case:
                            if x.in_case != None and x.is_select and not x.in_case.is_player:
                                list_in_range.append(x)
                        self.reset_select(list_case)
                        for x in list_in_range:
                            x.select(True)
                        self.show_which_one_play().select(False)
                        self.select_sort = False
                    if creation_img_text_click(img_next,"Fire Bolt",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()//2+screen.get_width()//2,img_next.get_height()//2+600):
                        pass
                    if creation_img_text_click(img_next,"Fire Ball",ColderWeather,WHITE,screen,self.game.click,img_next.get_width()//2+screen.get_width()//2,img_next.get_height()//2+900):
                        pass
                """
                    
                if self.select_monster:
                    what_happen = self.attack(list_case)
                    if what_happen == 0 :
                        self.select_monster = False
                        display_erreur.blit(screen,(0,0))

                        board_error("Erreur attack vide ou aucun monstre selectionner")
                    if what_happen == 1 :
                        pass
                    if what_happen == 2 :
                        pass
                    if what_happen == 3 :
                        return True
        else:
            have_attacked = False
            current_not_playable = self.list_tour[0]
            case_monstre = current_not_playable.trouver_case(list_case)
            case_monstre.select_neighbour(list_case)
            #print(self.player.name)
            if self.game.player.trouver_case(list_case).is_select:
                if self.player.hp > 0:
                    self.lunch_attack(self.player.trouver_case(list_case))
                    have_attacked = True
            for x in self.game.player.crew_mate:
                if x.hp > 0:
                    if x.trouver_case(list_case).is_select:
                        self.lunch_attack(x.trouver_case(list_case))
                        have_attacked = True
            self.reset_select(list_case)
            if not have_attacked:
                #Trouver le joueur le plus pret
                if self.game.player.hp > 0:
                   distance = self.find_distance(self.game.player.trouver_case(list_case),case_monstre)
                   nearest=self.game.player     
                else:
                   distance = 10000
                for x in self.game.player.crew_mate:
                    if x.hp > 0:
                       if self.find_distance(x.trouver_case(list_case),case_monstre) <= distance :
                           distance = self.find_distance(x.trouver_case(list_case),case_monstre)
                           
                           nearest  =x 
                nearest.trouver_case(list_case).select(True)
                #Se deplacer vers lui
                case_monstre.select_neighbour(list_case,k=1)
                distance_case = 15000
                for x in list_case:
                    if x.is_select and x.in_case == None:
                        if self.find_distance(x,nearest.trouver_case(list_case)) < distance_case:
                            distance_case = self.find_distance(x,nearest.trouver_case(list_case))
                            nearest_case = x
                
                
                self.print_anim(case_monstre,nearest_case,list_case,anim_type="walk")
                nearest_case.in_case = current_not_playable
                case_monstre.in_case = None


                self.reset_select(list_case)
                nearest_case.select_neighbour(list_case,k=0)
                if self.game.player.trouver_case(list_case).is_select:
                    self.lunch_attack(self.game.player.trouver_case(list_case))
                    have_attacked = True
                if not have_attacked:
                    for x in self.player.crew_mate:
                        if x.hp > 0:
                            if x.trouver_case(list_case).is_select:
                                self.lunch_attack(x.trouver_case(list_case))
                                have_attacked = True
                self.reset_select(list_case)
                self.next_round()
                #Passer le tour  
    def lunch_attack(self,defenseur):
        attack = self.show_which_one_play().in_case.calcul_attack_score()
        defense =  defenseur.in_case.calcul_armor()
        self.chat_box.write_log(("combat", self.show_which_one_play().in_case.name + " tente d'attaquer " + defenseur.in_case.name))
        self.chat_box.write_log(("combat", "Score d'attack : " + str(attack) + "Score de defense : " + str(defense)))
        if attack > defense:
            self.chat_box.write_log(("combat",self.show_which_one_play().in_case.name+" attack " + self.game.player.name ))
            self.print_anim(self.show_which_one_play(),self.game.player.trouver_case(list_case),list_case,anim_type="attack",mouvement=False)
            damages = self.show_which_one_play().in_case.damage()
            if isinstance(defenseur,Rogue):
                self.chat_box.write_log(("info","Uncanny dodge"))
                self.print_explosion(defenseur,"heal")
                damages = defenseur.uncanny_dodge(damages)
            
            self.chat_box.write_log(("combat", "Dammage : " + str(damages))) 
            self.print_explosion(defenseur)

            defenseur.in_case.hp -= damages
            if defenseur.in_case.hp <= 0:
                self.list_tour.remove(defenseur.in_case)
                defenseur.in_case = None
        self.reset_select(list_case)
        self.next_round()
    def lunch_spell(self):
        running= True
        
        spell = self.show_which_one_play().in_case.select_spell(self.select_spell)
        if spell != None and not isinstance(spell,bool):
            for x in spell:
                running = True
                dmg = x[0]
                is_healing = x[1]
                multi_cible = x[2]
                spell_range = x[4]
                self.show_which_one_play().select_neighbour(list_case,k=spell_range)
                self.show_which_one_play().select(False)
                list_in_range = []
                for x in list_case:
                    if x.is_select:
                        list_in_range.append(x)
                self.reset_select(list_case)
                while running:
                    
                    running,self.game.click = basic_checkevent(self.game.click)
                    mx,my=pygame.mouse.get_pos()
                    self.print_battleground()
                    self.reset_select(list_case)
                    for x in list_case:
                        screen.blit(x.display, x.cordo())
                        x.checkIfSelected()
                        x.print_contains()
                        if x.in_case != None:
                            x.in_case.type_animation = "idle"
                            x.in_case.animate()
                    
                    i, j = 0, 0
                    for h in self.map:
                        j = 0
                        for g in h:
                            if self.map[i][j] == 'w':
                                if pixel_mask.overlap(self.mask, ((mx-((j-i)*(pixel_red.get_width()+45)//2+screen.get_width()//2-pixel_red.get_width()//2), my-((j+i)*(pixel_red.get_width()+45)//4-100)))):
                                    for x in list_case:
                                        if x.i == i and x.j == j:
                                            if list_in_range.__contains__(x):
                                                self.reset_select(list_case)
                                                if multi_cible == 0:
                                                    x.select(True)
                                                else:
                                                    x.select_neighbour(list_case)
                                                
                                                if self.game.click:
                                                    for x in list_case:
                                                        if x.is_select and x.in_case != None:
                                                            if is_healing:
                                                                self.print_explosion(x)
                                                                self.chat_box.write_log(("combat", self.show_which_one_play().in_case.name + " lance sort " + x.in_case.name))
                                                                self.chat_box.write_log(("combat", "Dammage : " + str(dmg)))
                                                                x.in_case.hp -= dmg
                                                                if x.in_case.hp <= 0:
                                                                    self.list_tour.remove(x.in_case)
                                                                    x.in_case = None
                                                            else:
                                                                self.print_explosion(x,'heal')
                                                                self.chat_box.write_log(("combat", self.show_which_one_play().in_case.name + " heal " + x.in_case.name))
                                                                self.chat_box.write_log(("combat", "Heal : " + str(dmg)))
                                                                x.in_case.hp += dmg
                                                                if x.in_case.hp > x.in_case.hp_max:
                                                                    x.in_case.hp = x.in_case.hp_max
                                                            
                                                    self.reset_select(list_case)
                                                    
                                                    running = False
                                                    self.select_sort = False
                                                    self.select_spell = -1
                                                            

                                                

                            j += 1
                        i += 1
                    
                    pygame.display.update()

                
    def find_distance(self,case_1,case_2):
        return math.dist(case_1.cordo(),case_2.cordo())                       
    def next_round(self):
        if self.list_tour[0].is_player:
            self.list_tour[0].actionP = 1
            self.list_tour[0].bonusAction = 1
            self.list_tour[0].have_mouve = False
        self.list_tour.append(self.list_tour[0])
        self.list_tour.remove(self.list_tour[0])
    def show_which_one_play(self):
        current_playable = self.list_tour[0]
        #current_playable.trouver_case(list_case).select(True)
        return current_playable.trouver_case(list_case)
    def reset_select(self,list_case):
        for x in list_case:
            x.select(False)
    def attack(self,list_case):
        mx,my = pygame.mouse.get_pos()
        #GESTION TYPË ARME:
        if self.show_which_one_play().in_case.armor[4] == None:
            anim="attack"
            self.show_which_one_play().select_neighbour(list_case)
            self.show_which_one_play().select(False)
        elif self.show_which_one_play().in_case.armor[4] != None and key[self.show_which_one_play().in_case.armor[4]].wpn_name != 'RANGED':
            anim="attack"
            self.show_which_one_play().select_neighbour(list_case)
            self.show_which_one_play().select(False)
        else:
            anim="ranged"
            self.show_which_one_play().select_neighbour(list_case,k=1)
            self.show_which_one_play().select(False)


        i, j = 0, 0
        for h in self.map:
            j = 0
            for g in h:
                if self.map[i][j] == 'w':
                    if pixel_mask.overlap(self.mask, ((mx-((j-i)*(pixel_red.get_width()+45)//2+screen.get_width()//2-pixel_red.get_width()//2), my-((j+i)*(pixel_red.get_width()+45)//4-100)))):
                        if self.game.click:
                            for x in list_case:
                                if x.i == i and x.j == j:
                                    if x.is_select and x.in_case != None:
                                        self.reset_select(list_case)
                                        self.show_which_one_play().select_neighbour(list_case,k=1)
                                        if x.is_select:
                                            

                                            self.chat_box.write_log(("combat", self.show_which_one_play().in_case.name + " attack " + x.in_case.name))
                                            self.print_anim(self.show_which_one_play(),x,list_case,anim_type=anim,mouvement=False)
                                            self.print_explosion(x)
                                            attack = self.show_which_one_play().in_case.calcul_attack_score()
                                            defense =  x.in_case.calcul_armor()
                                            self.chat_box.write_log(("combat", "Score d'attack : " + str(attack) + "Score de defense : " + str(defense)))
                                            if attack > defense:
                                                if self.show_which_one_play().in_case.classe == 'rogue':
                                                    damages = self.show_which_one_play().in_case.damage(self.check_player_wall(list_case,x))
                                                    if self.check_player_wall(list_case,x):
                                                        self.chat_box.write_log(("combat", "Sneak attack"))
                                                else:
                                                    damages = self.show_which_one_play().in_case.damage()
                                                self.chat_box.write_log(("combat", "Dammage : " + str(damages))) 
                                                x.in_case.hp -= damages
                                            else:
                                                self.chat_box.write_log(("combat", "Attack raté")) 
                                            
                                            if x.in_case.hp <= 0:
                                                self.list_tour.remove(x.in_case)
                                                x.in_case = None
                                                self.liste_monstre.sort(key=lambda x: x.hp,reverse=True)
                                                if self.liste_monstre[0].hp == 0:
                                                    self.chat_box.write_log(("combat", "Fin de combat")) 
                                                    return 3
                                        self.reset_select(list_case)
                                        self.next_round()
                                        self.select_monster = False
                                        return 1
                                    else:
                                        self.reset_select(list_case)
                                        return 0
                                        


                j += 1
            i += 1
        return 2
    def check_player_wall(self,list_case,case_monstre):
        self.reset_select(list_case)
        case_monstre.select_neighbour(list_case)
        i=0
        j=0
        for x in list_case:
            if x.is_select and x.in_case != None and x.in_case.is_player:
                j +=1
                if j ==2:
                    return True
            if x.is_select:
                i+=1
        if i >=9:
            return False
        else:
            return True