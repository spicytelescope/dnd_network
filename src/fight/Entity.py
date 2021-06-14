import pygame


class Entity():

    def __init__(self, img,animation_dict, size=(0, 0), decalage=[0, 0]):
        if size == (0, 0):
            size = (img.get_width(), img.get_height())
        self.img = img
        self.display = pygame.Surface(size).convert_alpha()
        self.display.set_colorkey((0, 0, 0))
        self.display.blit(self.img, (0, 0))
        self.animation_dict = animation_dict
        self.frame = 1
        self.type_animation = "idle"
        self.decalage = decalage
        self.avata = pygame.transform.scale(img, (30, 30))


    def trouver_case(self,liste_case):
        for x in liste_case:
            if x.in_case == self:
                return x
        return liste_case[0]
    def animate_attack(self):
        one_complete = False
        if self.type_animation != "" and self.animation_dict != None:
            animation = self.animation_dict[self.type_animation]
            self.frame += 0.17
            if self.frame > len(animation)+1:
                self.frame = 1
                one_complete=True
            self.refresh_display()
            try:
                self.display.blit(animation[self.type_animation + "_" + str(int(self.frame)) + ".png"], (self.img.get_width()//2-animation[self.type_animation + "_" + str(int(self.frame)) + ".png"].get_width()//2+150-int(
                self.img.get_width()//2)+self.decalage[0], self.img.get_height()-animation[self.type_animation + "_" + str(int(self.frame)) + ".png"].get_height()+300-self.img.get_height()+self.decalage[1]))
            except :
                self.frame= 1
                self.display.blit(animation[self.type_animation + "_" + str(int(self.frame)) + ".png"], (self.img.get_width()//2-animation[self.type_animation + "_" + str(int(self.frame)) + ".png"].get_width()//2+150-int(
                self.img.get_width()//2)+self.decalage[0], self.img.get_height()-animation[self.type_animation + "_" + str(int(self.frame)) + ".png"].get_height()+300-self.img.get_height()+self.decalage[1]))
        else:
            self.display.blit(self.img, (0, 0))
        return one_complete
            #self.display.blit(animation[ self.type_animation + "_" + str(int(self.frame)) + ".png"],(150-animation[ self.type_animation + "_" + str(int(self.frame)) + ".png"].get_width()//2,self.img.get_height()-animation[ self.type_animation + "_" + str(int(self.frame)) + ".png"].get_height()+300-self.img.get_height()+self.decalage_display[1]))
    def animate(self):
        one_complete = False
        if self.type_animation != "" and self.animation_dict != None:
            animation = self.animation_dict[self.type_animation]
            self.frame += 0.08
            if self.frame > len(animation):
                self.frame = 1
                one_complete=True
            self.refresh_display()
            self.display.blit(animation[self.type_animation + "_" + str(int(self.frame)) + ".png"], (0,0))
            #print(f'Taille de l image ({self.img.get_width()},{self.img.get_height()})\n')    

        else:
             
            self.display.blit(self.img, (0, 0))
        
        return one_complete
            #self.display.blit(animation[ self.type_animation + "_" + str(int(self.frame)) + ".png"],(150-animation[ self.type_animation + "_" + str(int(self.frame)) + ".png"].get_width()//2,self.img.get_height()-animation[ self.type_animation + "_" + str(int(self.frame)) + ".png"].get_height()+300-self.img.get_height()+self.decalage_display[1]))
    def refresh_display(self):
        self.display.fill((255, 0, 0))
        #self.display.set_colorkey((1, 1, 1))

    def update_hp_bar(self,surface,x,y,hp,hp_max):
        bar_color=(113,255,51)
        hp_pourcent=(hp/hp_max)*100
        bar_position=(x,y,(hp_pourcent/2 if hp_pourcent>0 else 0),10)
        barmax_color=(255,60,51)
        hp_max_pourcent=hp_max/hp_max*100
        barmax_position=(x,y,hp_max_pourcent/2,10)
        pygame.draw.rect(surface, barmax_color, barmax_position)
        pygame.draw.rect(surface, bar_color, bar_position)
        #s=wblack(ColderWeather,"Level  "+str(self.level))
        #s=pygame.transform.scale(s,(s.get_width()//4, s.get_height()//4))
        #surface.blit(s,(x,y-20))