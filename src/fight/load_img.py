import pygame
from fight.jordanask import image_loader,transform_image


collide = pygame.transform.scale(pygame.image.load("./assets/fight/Collide.png"),(100,50))
collide.set_colorkey((255,255,255))
case_select = pygame.transform.scale(pygame.image.load("./assets/fight/case_select.png"),(100,50))
case_select.set_colorkey((255,255,255))
case = pygame.transform.scale(pygame.image.load("./assets/fight/case.png"),(100,50))
case.set_colorkey((255,255,255))

demon_walk = dict(image_loader("./assets/fight/demon_walk/"))
transform_image(demon_walk,4.5)
demon_animation = dict()
demon_animation["walk"] = demon_walk

demon_idle = dict(image_loader("./assets/fight/demon_idle/"))
transform_image(demon_idle,2.5)
demon_animation["idle"] = demon_idle

demon_attack = dict(image_loader("./assets/fight/demon_attack/"))
transform_image(demon_attack,4.5)
demon_animation["attack"] = demon_attack

demon_1_walk = dict(image_loader("./assets/fight/demon_1_walk/"))
transform_image(demon_1_walk,4.5)
demon_1_animation = dict()
demon_1_animation["walk"] = demon_1_walk

demon_1_idle = dict(image_loader("./assets/fight/demon_1_idle/"))
transform_image(demon_1_idle,4.5)
demon_1_animation["idle"] = demon_1_idle

demon_1_attack = dict(image_loader("./assets/fight/demon_1_attack/"))
transform_image(demon_1_attack,4.5)
demon_1_animation["attack"] = demon_1_attack



hunter_walk = dict(image_loader("./assets/fight/perso/Hunter_walk/"))
transform_image(demon_1_walk,4.5)
hunter_animation = dict()
hunter_animation["walk"] = hunter_walk

hunter_idle = dict(image_loader("./assets/fight/perso/Hunter_idle/"))
transform_image(demon_1_idle,4.5)
hunter_animation["idle"] = hunter_idle

Warrior_walk = dict(image_loader("./assets/fight/perso/Warrior_walk/"))
transform_image(demon_1_walk,4.5)
Warrior_animation = dict()
Warrior_animation["walk"] = Warrior_walk

Warrior_idle = dict(image_loader("./assets/fight/perso/Warrior_idle/"))
transform_image(demon_1_idle,4.5)
Warrior_animation["idle"] = Warrior_idle
Wizard_animation = dict()
Wizard_animation = Warrior_animation

explosion = dict(image_loader("./assets/fight/explosion_spell/"))
transform_image(explosion,multi=1)
"""
Wizard_walk = dict(image_loader("./assets/fight/perso/Wizard_walk/"))
transform_image(demon_1_walk,4.5)
Wizard_animation = dict()
Wizard_animation["walk"] = Wizard_walk
"""
"""
Wizard_idle = dict(image_loader("./assets/fight/perso/Wizard_idle/"))
transform_image(demon_1_idle,4.5)
Wizard_animation["idle"] = Wizard_idle

"""