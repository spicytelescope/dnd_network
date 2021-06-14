import pygame
from pygame.locals import *
import sys
import os

def image_loader(path) -> str:
        for i in os.listdir(path):
            image = pygame.image.load(path + i)
            #image.set_colorkey((153,144,136))
            yield (i,image)
def transform_image(dict_image,multi=3,width=0,height=0):
        for x in dict_image:
            dict_image[x] = pygame.transform.scale(dict_image[x],(int(multi*dict_image[x].get_width()+width),int(multi*dict_image[x].get_height()+height)))
            #dict_image[x].set_colorkey((153,144,136))


def basic_checkevent(click):
    click = False
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return False,click
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
    return True,click

def load_map(path,reverse=False):
    f = open(path,'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    map = []
    if not reverse:
        for row in data:
            map.append(list(row))
    else:
        for row in reversed(data):
            map.append(list(row))
    return map

def draw_text(text, font, color, surface, x, y):
    if color=="bl":
        color=BLACK
    if color=="b":
        color=BROWN
    if color=="y":
        color=YELLOW
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
