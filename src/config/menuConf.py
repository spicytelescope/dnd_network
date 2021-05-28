import datetime
from os import listdir
from os.path import isfile, join

import pygame
from config.playerConf import MAX_TEAM_LENGH
from gameController import *
from utils.utils import logger

from config.mapConf import *
from config.UIConf import BUTTON_FONT_NAME

logger.info("Loading menuConf")

pygame.font.init()

# ------------ MAIN MENU SETTINGS ------------ #

global MAIN_BACKGROUND

TITLE_FONT_SIZE = 100
TITLE_FONT = pygame.font.SysFont("Dungeon", TITLE_FONT_SIZE)
FONT_COLOR = (255, 14, 14)
MAIN_BUTTONS_NAMES = ["PLAY", "OPTIONS", "QUIT"]

# ------------ OPTION MENU SETTINGS ------------ #

OPTION_BUTTONS_NAMES = ["VIDEO & SOUNDS", "KEYBOARD", "BACK"]
DEFAULT_FRAME_SIZE = 400
OPTION_LABELS = [
    # "Resolution",
    "Refresh Rate",
    "Render Distance",
    # "Level of detail (step generation)",
    "Enable Water Animations",
    "Debug Mode",
    "Enable sound",
]
MIN_SIZE_FRAME = (len(OPTION_LABELS) * 50 * 2, len(OPTION_LABELS) * 50)

# -------------- GAME MENU -------------------- #


global GAME_SLOTS

# -------------- GAME SLOT CREATION MENU ----------- #

# CHARACTER MENU

CHAR_ANIMATION_TIME = 500  # ms

# GEN MAP MENU

GEN_MAP_PARAM_NAMES = ["SEED", "BIOMES", "WORLD ELEMENTS GENERATION"]

# -------------- IN GAME MENUS -------------- #

# PAUSE MENU

global BG_WOOD

PAUSE_BUTTON_NAMES = ["PAUSE MENU"] + OPTION_BUTTONS_NAMES + ["OPEN TO LAN", "RETURN TO MENU"]


# -------------- LOADING MENU ---------------- #

FONT_LOAD = pygame.font.Font(DUNGEON_FONT, 60)

global LOADINGS_BG_STATIC

global LOADING_BG_DYNAMIC

global LOADING_LIGHTS

global WALKING_LOADING_GUY

WALKING_LOADIN_GUY_ANIM_TIME = 0.5  # s

DUNGEON_LOADING_FLAGS = (
    {}
)  # Static loading for the dungeon, doesn't depends of the render distance

# Weights in pourcentage

OPEN_WORLD_FLAGS_WEIGHTS = {
    "MAP": 15,
    "ELEMENTS_TEXTURES": 15,
    "BIOME_TEXTURES": 10,
    "HUD_LOADING": 20,
    "GAME_OBJECT_LOADING": 40,
}

OPEN_WORLD_FLAGS = {
    "biomeTextures": {
        "desc": "Loading biomes textures ...",
        "weight": OPEN_WORLD_FLAGS_WEIGHTS["BIOME_TEXTURES"],
        "subflags": None,
        "checked": False,
    },
    "worldElements": {
        "desc": "Generating world elements and updating MiniMap ...",
        "weight": OPEN_WORLD_FLAGS_WEIGHTS["ELEMENTS_TEXTURES"],
        "subflags": None,
        "checked": False,
    },
    "HUDLoading": {
        "desc": "Generating Player HUD ...",
        "weight": OPEN_WORLD_FLAGS_WEIGHTS["HUD_LOADING"],  # Divided by 3 as there is 3 players
        "checked": False,
        "subflags": None,
    },
    "gameObjectLoading": {
        "subflags": {
            "spellDBLoading": {
                "desc": "Loading spell DB ...",
                "weight": int(OPEN_WORLD_FLAGS_WEIGHTS["GAME_OBJECT_LOADING"] * 0.5),
                "checked": False,
            },
            "ItemDBLoading": {
                "desc": "Loading item DB ...",
                "weight": int(OPEN_WORLD_FLAGS_WEIGHTS["GAME_OBJECT_LOADING"] * 0.5),
                "checked": False,
            },
        },
        "weight": OPEN_WORLD_FLAGS_WEIGHTS["GAME_OBJECT_LOADING"],
        "checked": False,
    },
}

assert (
    sum([weight for weight in OPEN_WORLD_FLAGS_WEIGHTS.values()]) == 100
), "<ERROR> : the sum of the weights in the loading flags aren't doing 100"