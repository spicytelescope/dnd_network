import copy
import fnmatch
import os
import random
from os import listdir
from os.path import isfile, join

import config.HUDConf as HUDConf
import config.itemConf as itemConf
import config.mapConf as mapConf
import config.menuConf as menuConf
import config.playerConf as playerConf
import config.spellsConf as spellsConf
import config.textureConf as textureConf
import config.UIConf as UIConf
import pandas
import pygame
from config import NPCConf, ennemyConf, musicConf, openWorldConf
from config.NPCConf import NPC_DIALOGS
from config.openWorldConf import *
from config.textureConf import *
from gameObjects.Item import Item
from Player.Spell import Spell
from saves.savesController import SaveController

from utils.utils import logger

# Module handling the loading of the ressources, whether it is DBs, images or sounds.
# The methods of this class allow to load dynamically ressources so that the game can
# load the menu faster.

# Only the ressources that are meant not be loaded at the first lauch of the program are handled.

NoContact = lambda: None

def loadMusicRessources():

    logger.info("LOADING MUSIC RESSOURCES")
    # musicConf.SOUNDS_BANK = {
    #     songName: pygame.mixer.Sound(songPath)
    #     for songName, songPath in musicConf.SOUNDS_PATH.items()
    # }


def loadItemRessources():
    """
    Specificly load the item DB and the textures for the chest
    """

    logger.info("LOADING ITEM RESSOURCES")

    # Loading spell DB

    CSV_ITEM_DATABASE = pandas.read_csv("./assets/Items/ITEM_DATABASE.csv")

    itemConf.ITEM_DB = {
        ID: Item(
            str(CSV_ITEM_DATABASE["ICON PATH"][ID]),
            [
                CSV_ITEM_DATABASE["ITEM ID"][ID],
                CSV_ITEM_DATABASE["SLOT ID"][ID],
                CSV_ITEM_DATABASE["NAME"][ID],
                CSV_ITEM_DATABASE["RARETY"][ID],
                CSV_ITEM_DATABASE["STATS"][ID],
                CSV_ITEM_DATABASE["DESC"][ID],
                CSV_ITEM_DATABASE["DURABILITY"][ID],
                CSV_ITEM_DATABASE["TYPE ID"][ID],
            ],
            CSV_ITEM_DATABASE["META TYPE"][ID],
            # Concerting the string into a list, then the list into a set and THEN the set into a list
            list(set(str(CSV_ITEM_DATABASE["CLASS RESTRICT"][ID]).split(" "))),
            CSV_ITEM_DATABASE["GOLD VALUE"][ID],
        )
        for ID in CSV_ITEM_DATABASE["ITEM ID"]
    }

    # Loading default item kit into the right classes
    for classCase in playerConf.CLASSES.values():
        classCase["defaultItemKitId"] = []
        for _ in range(playerConf.DEFAULT_NUM_ITEM):
            testId = random.choice(list(itemConf.ITEM_DB.keys()))
            while (
                classCase["name"]
                not in itemConf.ITEM_DB[testId].property["classRestriction"]
            ):
                testId = random.choice(list(itemConf.ITEM_DB.keys()))
            classCase["defaultItemKitId"].append(testId)


def loadHUDRessources():

    logger.info("LOADING HUD RESSOURCES")

    HUDConf.BAR_IMG = pygame.image.load(
        "./assets/UI/health_mana_bar/player/player_icon_bar.png"
    ).convert_alpha()
    HUDConf.NAME_SLOT = pygame.image.load(
        "./assets/UI/PlayerInfo/NameIcon.png"
    ).convert_alpha()

    HUDConf.INVENTORY_SURF = pygame.image.load(
        "./assets/UI/Inventory/Inventory.png"
    ).convert_alpha()

    HUDConf.PLAYER_ICON_SLOT = pygame.image.load(
        "./assets/UI/PlayerInfo/PlayerIcon.png"
    ).convert_alpha()

    HUDConf.ITEM_INFO_ICONS = {
        "sellValue": {
            "center": (265, 349),
            "surf": pygame.image.load("./assets/Items/money.png").convert_alpha(),
        },
        "durability": {
            "center": (355, 349),
            "surf": pygame.image.load("./assets/Items/durability.png").convert_alpha(),
        },
    }
    for icon in HUDConf.ITEM_INFO_ICONS.values():
        icon["rect"] = icon["surf"].get_rect(center=icon["center"])

    NPCConf.UI_SELLER_SURF = pygame.image.load(
        "./assets/UI/SellerInterface/SellerUI.png"
    ).convert_alpha()

    NPCConf.UI_SELLER_INFO_ICONS = {
        "sellValue": {
            "center": (60, 360),
            "surf": pygame.image.load("./assets/Items/money.png").convert_alpha(),
        },
        "durability": {
            "center": (150, 360),
            "surf": pygame.image.load("./assets/Items/durability.png").convert_alpha(),
        },
    }
    for icon in NPCConf.UI_SELLER_INFO_ICONS.values():
        icon["rect"] = icon["surf"].get_rect(center=icon["center"])

    HUDConf.QUEST_JOURNAL_MAIN_SURF = pygame.image.load(
        "./assets/UI/questJournal/mainSurf.png"
    ).convert_alpha()

    HUDConf.QUEST_OPEN_ANIM_FRAMES = [
        pygame.image.load(
            f"{HUDConf.QUEST_ANIM_PATHS['openAnimation']}/{f}"
        ).convert_alpha()
        for f in listdir(HUDConf.QUEST_ANIM_PATHS["openAnimation"])
        if isfile(join(HUDConf.QUEST_ANIM_PATHS["openAnimation"], f))
    ]

    HUDConf.QUEST_CLOSE_ANIM_FRAMES = [
        pygame.image.load(
            f"{HUDConf.QUEST_ANIM_PATHS['closeAnimation']}/{f}"
        ).convert_alpha()
        for f in listdir(HUDConf.QUEST_ANIM_PATHS["closeAnimation"])
        if isfile(join(HUDConf.QUEST_ANIM_PATHS["closeAnimation"], f))
    ]

    HUDConf.QUESTS_BUTTONS = {
        "back": {
            "blitPoint": [125, 512],
            "surf": pygame.image.load(
                "./assets/UI/buttons/select_left.png"
            ).convert_alpha(),
            "surfClicked": pygame.image.load(
                "./assets/UI/buttons/select_left_clicked.png"
            ).convert_alpha(),
        },
        "next": {
            "blitPoint": [900, 512],
            "surf": pygame.image.load("./assets/UI/buttons/select_right.png").convert(),
            "surfClicked": pygame.image.load(
                "./assets/UI/buttons/select_right_clicked.png"
            ).convert(),
        },
    }

    HUDConf.QUEST_PROGRESS_BAR = pygame.image.load(
        "./assets/UI/questJournal/progress.png"
    ).convert_alpha()
    HUDConf.QUEST_COMPLETED_BAR = pygame.image.load(
        "./assets/UI/questJournal/completed.png"
    ).convert_alpha()


def loadMiniMapRessources():

    logger.info("LOADING MINIMAP RESSOURCES")

    mapConf.EXTENDED_MINIMAP_BG = pygame.image.load(
        "./assets/UI/Map/mapScroll.png"
    ).convert_alpha()
    mapConf.EXTENDED_MAP_LAYOUT = pygame.image.load(
        "./assets/UI/Map/mapLayout.png"
    ).convert_alpha()
    mapConf.BAR_MAP_LAYOUT_LOCAL_AREA = pygame.image.load(
        "./assets/UI/Map/LocalAreaSelect.png"
    ).convert_alpha()
    mapConf.BAR_MAP_LAYOUT_WORLD_AREA = pygame.image.load(
        "./assets/UI/Map/WorldMapSelect.png"
    ).convert_alpha()
    HUDConf.PLAYER_ICON_SLOT = pygame.image.load(
        "./assets/UI/PlayerInfo/PlayerIcon.png"
    ).convert_alpha()


def loadMenuRessources():

    logger.info("LOADING MENU RESSOURCES")

    menuConf.MAIN_BACKGROUND = pygame.image.load(
        "./assets/menus/backgrounds/backgroundMenu.png"
    ).convert_alpha()
    menuConf.BG_WOOD = pygame.image.load(
        "./assets/menus/backgrounds/wood_background.png"
    ).convert_alpha()

    menuConf.LOADINGS_BG_STATIC = [
        pygame.image.load(
            f"./assets/menus/loading/BackgroundLayers/{fileName}.png"
        ).convert_alpha()
        for fileName in [
            "Layer_0010_1",
            "Layer_0009_2",
            "Layer_0008_3",
            "Layer_0006_4",
            "Layer_0005_5",
        ]
    ]

    menuConf.LOADING_BG_DYNAMIC = [
        pygame.image.load(
            f"./assets/menus/loading/BackgroundLayers/{fileName}.png"
        ).convert_alpha()
        for fileName in [
            "Layer_0003_6",
            "Layer_0002_7",
            "Layer_0001_8",
            "Layer_0000_9",
        ]
    ]

    menuConf.LOADING_LIGHTS = [
        pygame.image.load(
            f"./assets/menus/loading/BackgroundLayers/{fileName}.png"
        ).convert_alpha()
        for fileName in ["Layer_0007_Lights", "Layer_0004_Lights"]
    ]

    menuConf.WALKING_LOADING_GUY = [
        pygame.image.load(
            f"./assets/menus/loading/loadingRunningAnnimation/frame_{i}_delay-0.1s.png"
        ).convert_alpha()
        for i in range(4)
    ]

    menuConf.GAME_SLOTS = [
        {
            "empty": not SaveController().isSaved(i),
            "name": f"GAME SLOT {i}",
            "creationDate": SaveController().getLastModifiedTime(i),
        }
        for i in range(1, 4)
    ]

    menuConf.SCROLL = pygame.image.load(
        "./assets/UI/PlayerInfo/NameIcon.png"
    ).convert_alpha()


def loadPlayerRessources():

    logger.info("LOADING PLAYER RESSOURCES")

    playerConf.CLASSES = {
        i: {
            "name": className,
            "directions": {
                direction: [
                    pygame.transform.scale(
                        pygame.image.load(
                            f"./assets/classes/{className}/{direction}_{i}.png"
                        ).convert_alpha(),
                        (playerConf.PLAYER_SIZE, playerConf.PLAYER_SIZE),
                    )
                    for i in range(1, playerConf.PLAYER_ANIMATION_FRAME_LENGTH + 1)
                ]
                for direction in playerConf.PLAYER_DIRECTIONS
            },
            "icon": pygame.image.load(
                f"./assets/classes/{className}/icon.png"
            ).convert_alpha(),
            "isometricFrame": {
                movement: [
                    pygame.image.load(f"./assets/fight/Character/{className}/{f}")
                    for f in os.listdir(f"./assets/fight/Character/{className}")
                    if fnmatch.fnmatch(f, f"{movement}*")
                ]
                for movement in [
                    "walk_droit",
                    "walk_haut",
                    "walk_bas",
                    "walk_gauche",
                    "neutral",
                ]
            },
        }
        for i, className in enumerate(playerConf.CLASSES_NAMES)
    }


def loadSpellRessources():

    logger.info("LOADING SPELL RESSOURCES")

    spellsConf.SPELLBOOK_BUTTONS = {
        "back": {
            "blitPoint": [88, 512],
            "surf": pygame.image.load(
                "./assets/UI/buttons/select_left.png"
            ).convert_alpha(),
            "surfClicked": pygame.image.load(
                "./assets/UI/buttons/select_left_clicked.png"
            ).convert_alpha(),
        },
        "next": {
            "blitPoint": [945, 512],
            "surf": pygame.image.load("./assets/UI/buttons/select_right.png").convert(),
            "surfClicked": pygame.image.load(
                "./assets/UI/buttons/select_right_clicked.png"
            ).convert(),
        },
    }

    spellsConf.SPELLBOOK_MAIN_SURF = pygame.image.load(
        "./assets/UI/spellBook/mainSurf.png"
    ).convert_alpha()

    spellsConf.OPEN_ANIM_FRAMES = [
        pygame.image.load(
            f"{spellsConf.ANIM_PATHS['openAnimation']}/{f}"
        ).convert_alpha()
        for f in listdir(spellsConf.ANIM_PATHS["openAnimation"])
        if isfile(join(spellsConf.ANIM_PATHS["openAnimation"], f))
    ]

    spellsConf.CLOSE_ANIM_FRAMES = [
        pygame.image.load(
            f"{spellsConf.ANIM_PATHS['closeAnimation']}/{f}"
        ).convert_alpha()
        for f in listdir(spellsConf.ANIM_PATHS["closeAnimation"])
        if isfile(join(spellsConf.ANIM_PATHS["closeAnimation"], f))
    ]

    spellsConf.NEXT_ANIM_FRAMES = [
        pygame.image.load(
            f"{spellsConf.ANIM_PATHS['nextAnimation']}/{f}"
        ).convert_alpha()
        for f in listdir(spellsConf.ANIM_PATHS["nextAnimation"])
        if isfile(join(spellsConf.ANIM_PATHS["nextAnimation"], f))
    ]

    spellsConf.BACK_ANIM_FRAMES = [
        pygame.image.load(
            f"{spellsConf.ANIM_PATHS['backAnimation']}/{f}"
        ).convert_alpha()
        for f in listdir(spellsConf.ANIM_PATHS["backAnimation"])
        if isfile(join(spellsConf.ANIM_PATHS["backAnimation"], f))
    ]

    spellsConf.DMG_ICON = pygame.image.load(
        "./assets/UI/spellBook/spellIcons/dmgIcon.png"
    ).convert_alpha()
    spellsConf.DMGRANGE_ICON = pygame.image.load(
        "./assets/UI/spellBook/spellIcons/dmgRangeIcon.png"
    ).convert_alpha()

    # Loading spell DB

    CSV_SPELL_DATABASE = pandas.read_csv("./assets/Spells/SPELL_DATABASE.csv")

    spellsConf.SPELL_DB = {
        ID: Spell(
            CSV_SPELL_DATABASE["SPELL ID"][ID],
            CSV_SPELL_DATABASE["NAME"][ID],
            CSV_SPELL_DATABASE["DESC"][ID],
            CSV_SPELL_DATABASE["LVL"][ID],
            CSV_SPELL_DATABASE["EFFECTS"][ID],
            CSV_SPELL_DATABASE["DMG"][ID],
            CSV_SPELL_DATABASE["TYPE"][ID],
            CSV_SPELL_DATABASE["DMGRANGE"][ID],
            CSV_SPELL_DATABASE["WEAPONS"][ID],
            CSV_SPELL_DATABASE["ANIM TIME"][ID],
            str(CSV_SPELL_DATABASE["ANIM DIR PATH"][ID]),
            str(CSV_SPELL_DATABASE["ICON PATH"][ID]),
            CSV_SPELL_DATABASE["CLASS"][ID],
        )
        for ID in CSV_SPELL_DATABASE["SPELL ID"]
    }

    # Loading class spells IDs into the right classes
    # for className, classCase in playerConf.CLASSES.items():
    #     classCase["spellsId"] = [
    #         Id
    #         for Id in spellsConf.SPELL_DB.keys()
    #         if spellsConf.SPELL_DB[Id].className == className and spellsConf.SPELL_DB[Id].lvl == 1
    #     ]


def loadLandscapeRessources(stepGeneration: int = PLAYER_CONFIG["STEP_GENERATION"]):
    # Adding landscape elements according to the biomes for more personnalisation
    #  For now, they will have the same spawnRange and spawnTreshold

    textureConf.WORLD_ELEMENTS = {"Landscape": {}}

    for biomeName in BIOME_NAMES:
        biomePath = f"./assets/world_textures/{biomeName}_biome/"
        for biomeElt in BIOME_LANDSCAPE_NAME:
            defaultConf = {
                "rect": None,
                "surf": [],
                "spawnRange": None,
                "spawnTreshold": None,
                "placeholder": {"type": "alone", "flag": False},
                "spawnTileCode": None,
                "onContact": NoContact,
                "entity": None,
            }

            if biomeElt == "tree":
                defaultConf["spawnRange"] = 4
                defaultConf["spawnTreshold"] = 3
                defaultConf["spawnTileCode"] = BIOME_COLORS[biomeName]

            elif biomeElt == "rock":
                defaultConf["spawnRange"] = 4
                defaultConf["spawnTreshold"] = 3
                defaultConf["spawnTileCode"] = BIOME_COLORS[biomeName]

            elif biomeElt == "random_wood":
                defaultConf["spawnRange"] = 5
                defaultConf["spawnTreshold"] = 24
                defaultConf["spawnTileCode"] = BIOME_COLORS[biomeName]

            elif biomeElt == "flower":
                defaultConf["spawnRange"] = 3
                defaultConf["spawnTreshold"] = 7
                defaultConf["spawnTileCode"] = BIOME_COLORS[biomeName]

            #  Creating Landscape element entry
            elementEntry = f"{biomeName[0].upper() + biomeName[1:]}_{biomeElt}"
            textureConf.WORLD_ELEMENTS["Landscape"][elementEntry] = copy.deepcopy(
                defaultConf
            )
            logger.debug(f"Loading ressource for : {elementEntry}")

            for file in os.listdir(biomePath):
                if fnmatch.fnmatch(file, f"{biomeElt}*"):
                    textureConf.WORLD_ELEMENTS["Landscape"][elementEntry][
                        "surf"
                    ].append(
                        pygame.transform.scale(
                            pygame.image.load(f"{biomePath}/{file}").convert_alpha(),
                            (
                                stepGeneration,
                                stepGeneration,
                            ),
                        )
                    )


def loadOpenWorldRessources(stepGeneration: int = PLAYER_CONFIG["STEP_GENERATION"]):

    logger.info("LOADING OPEN WORLD RESSOURCES")

    textureConf.DUNGEON_PORTAL_OPEN = [
        pygame.image.load(f"./assets/world_textures/buildings/dungeon/portal/open/{f}")
        for f in listdir("./assets/world_textures/buildings/dungeon/portal/open/")
        if isfile(join("./assets/world_textures/buildings/dungeon/portal/open/", f))
    ]

    textureConf.DUNGEON_PORTAL_IDLE = [
        pygame.transform.scale(pygame.image.load(f"./assets/world_textures/buildings/dungeon/portal/idle/{f}"), (stepGeneration, stepGeneration)).convert_alpha()
        for f in listdir("./assets/world_textures/buildings/dungeon/portal/idle/")
        if isfile(join("./assets/world_textures/buildings/dungeon/portal/idle/", f))
    ]

    textureConf.WORLD_TEXTURES = {
        "WATER_ANIMATIONS": [
            pygame.transform.scale(
                pygame.image.load(
                    f"./assets/world_textures/water/water{i}.png"
                ).convert_alpha(),
                (stepGeneration, stepGeneration),
            )
            for i in range(3)
        ]
    }

    for biomeName in BIOME_NAMES:
        biome_path = f"./assets/world_textures/{biomeName}_biome/"
        textureConf.WORLD_TEXTURES[biomeName.upper() + "_" + "SPRITES"] = [
            pygame.transform.scale(
                pygame.image.load(f"{biome_path}/{file}").convert_alpha(),
                (
                    stepGeneration,
                    stepGeneration,
                ),
            )
            for file in os.listdir(biome_path)
            if fnmatch.fnmatch(file, f"default*")
        ]

    textureConf.BUILDING_ANIM_OPEN = [
        pygame.transform.scale(
            pygame.image.load(
                f"./assets/world_textures/buildings/house/transition/{f}"
            ).convert_alpha(),
            (512, 512),
        )
        for f in listdir("./assets/world_textures/buildings/house/transition/")
        if isfile(join("./assets/world_textures/buildings/house/transition/", f))
    ]
    textureConf.BUILDING_ANIM_CLOSE = [
        pygame.transform.scale(
            pygame.image.load(
                f"./assets/world_textures/buildings/house/transition/{f}"
            ).convert_alpha(),
            (512, 512),
        )
        for f in listdir("./assets/world_textures/buildings/house/transition/")[::-1]
        if isfile(join("./assets/world_textures/buildings/house/transition/", f))
    ]

    textureConf.DUNGEON_ANIM_OPEN = [
        pygame.transform.scale(
            pygame.image.load(
                f"./assets/world_textures/buildings/dungeon/transition/{f}"
            ).convert_alpha(),
            (512, 512),
        )
        for f in listdir("./assets/world_textures/buildings/dungeon/transition/")
        if isfile(join("./assets/world_textures/buildings/dungeon/transition/", f))
    ]
    textureConf.DUNGEON_ANIM_CLOSE = [
        pygame.transform.scale(
            pygame.image.load(
                f"./assets/world_textures/buildings/dungeon/transition/{f}"
            ).convert_alpha(),
            (512, 512),
        )
        for f in listdir("./assets/world_textures/buildings/dungeon/transition/")[::-1]
        if isfile(join("./assets/world_textures/buildings/dungeon/transition/", f))
    ]

    textureConf.WORLD_ELEMENTS = {
        **textureConf.WORLD_ELEMENTS,  # Adding landscapes
        "Building": {
            # Means that the house must spawn on a 4x4 green AND must occupy all this place (placeholder valuem)
            "PNJHouse": {
                "rect": None,
                "surf": pygame.transform.scale(
                    pygame.image.load(
                        "./assets/world_textures/buildings/house/PNJHouse001/PNJHouse001.png"
                    ).convert_alpha(),
                    (
                        3 * stepGeneration,
                        3 * stepGeneration,
                    ),
                ),
                "placeholder": {"type": "all", "flag": False},
                "spawnRange": 3,
                "spawnTreshold": 9,
                "spawnTileCode": GREEN,
                "onContact": NoContact,
                "entity": None,
                "mapSurfPath": "./assets/world_textures/buildings/house/PNJHouse001/PNJHouse001_interior.png",
                "mapLayerPath": [
                    f"./assets/world_textures/buildings/house/PNJHouse001/PNJHouse1_Tile Layer {i}.csv"
                    for i in range(1, 4)
                ],
                "enterPoints": [[15, 7]],  # topleft of the tile entrance
                "NPC": {},
            },
            "Shop": {
                "rect": None,
                "surf": pygame.transform.scale(
                    pygame.image.load(
                        "./assets/world_textures/buildings/shop/Shop.png"
                    ).convert_alpha(),
                    (3 * stepGeneration, 3 * stepGeneration),
                ),
                "placeholder": {"type": "all", "flag": False},
                "spawnRange": 3,
                "spawnTreshold": 9,
                "spawnTileCode": GREEN,
                "onContact": NoContact,
                "entity": None,
                "mapLayerPath": [
                    f"./assets/world_textures/buildings/shop/Seller_Tile Layer {i}.csv"
                    for i in range(1, 4)
                ],
                "mapSurfPath": "./assets/world_textures/buildings/shop/Shop_interior.png",
                "enterPoints": [[14, 17], [15, 17]],
                "NPC": {"14;14": "Seller"},
            },
            "Temple": {
                "rect": None,
                "surf": pygame.transform.scale(
                    pygame.image.load(
                        "./assets/world_textures/buildings/temple/Temple001.png"
                    ).convert_alpha(),
                    (3 * stepGeneration, 3 * stepGeneration),
                ),
                "placeholder": {"type": "all", "flag": False},
                "spawnRange": 3,
                "spawnTreshold": 9,
                "spawnTileCode": GREEN,
                "onContact": NoContact,
                "entity": None,
                "NPC": {},
            },
        },
        "Dungeon": {
            "Death's Dungeon": {
                "surf": pygame.transform.scale(
                    pygame.image.load(
                        "./assets/world_textures/buildings/dungeon/Death_Dungeon.png"
                    ).convert_alpha(),
                    (3 * stepGeneration, 3 * stepGeneration),
                ),
                "rect": None,
                "placeholder": {"type": "all", "flag": False},
                "spawnRange": 3,
                "spawnTreshold": 9,
                "spawnTileCode": GREEN,
                "onContact": NoContact,
                "entity": None,
                "composition": {
                    "ennemy": ["Skeleton", "Flying_eye"],
                    "miniBoss": "",
                    "boss": "",
                },
                "tileset": {
                    "entrance": pygame.transform.scale(
                        pygame.image.load(
                            f"./assets/world_textures/buildings/dungeon/entrance.png"
                        ).convert_alpha(),
                        (64, 64),
                    ),
                    "lower_wall": pygame.transform.scale(
                        pygame.image.load(
                            f"./assets/world_textures/buildings/dungeon/lower_wall.png"
                        ).convert(),
                        (64, 64),
                    ),
                    "upper_wall": pygame.transform.scale(
                        pygame.image.load(
                            f"./assets/world_textures/buildings/dungeon/upper_wall.png"
                        ).convert(),
                        (64, 64),
                    ),
                    "ceil": pygame.transform.scale(
                        pygame.image.load(
                            f"./assets/world_textures/buildings/dungeon/ceil.png"
                        ).convert(),
                        (64, 64),
                    ),
                    "floors": [
                        pygame.transform.scale(
                            pygame.image.load(
                                f"./assets/world_textures/buildings/dungeon/floor_{i}.png"
                            ).convert(),
                            (64, 64),
                        )
                        for i in range(1, 4)
                    ],
                    "torchs": [
                        pygame.transform.scale(
                            pygame.image.load(
                                f"./assets/world_textures/buildings/dungeon/torch/torch_0{i}.png"
                            ).convert_alpha(),
                            (int(64 * 0.5), int(64 * 0.75)),
                        )
                        for i in range(1, 4)
                    ],
                    "door": pygame.transform.scale(
                        pygame.image.load(
                            "./assets/world_textures/buildings/dungeon/transition/frame_0_delay-0.2s.png"
                        ),
                        (64, 64 * 2),
                    ),
                },
            }
        },
        "Ennemy": {
            ennemyName: {
                "rect": None,
                "surf": None,
                "spawnRange": 4,
                "spawnTreshold": 4,
                "placeholder": {"type": "alone", "flag": False},
                "spawnTileCode": GREEN,
                "onContact": NoContact,
                "entity": None,
                "defaultGoldValue": ennemyConf.ENNEMY_DEFAULT_GOLD_VALUE[ennemyName],
                "frames": {
                    movement: [
                        pygame.image.load(
                            f"./assets/fight/Monster/{ennemyName}/{f}"
                        ).convert_alpha()
                        for f in os.listdir(f"./assets/fight/Monster/{ennemyName}")
                        if fnmatch.fnmatch(f, f"{movement}*")
                    ]
                    for movement in [
                        "walk_droit",
                        "walk_haut",
                        "walk_bas",
                        "walk_gauche",
                        "neutral",
                    ]
                },
            }
            for ennemyName in listdir("./assets/world_textures/ennemy")
            if ennemyName != "stateBubble"
        },
        "GameObject": {
            "Chest": {
                "rect": None,
                "surf": pygame.transform.scale(
                    pygame.image.load(f"./assets/UI/chest/001.png").convert_alpha(),
                    (playerConf.PLAYER_SIZE, playerConf.PLAYER_SIZE),
                ),
                "spawnRange": 6,
                "spawnTreshold": 3,
                "placeholder": {"type": "alone", "flag": False},
                "spawnTileCode": GREEN,
                "onContact": NoContact,
                "entity": None,
                "CHEST_ANIM_OPEN": [
                    pygame.transform.scale(
                        pygame.image.load(
                            f"./assets/UI/chest/00{i}.png"
                        ).convert_alpha(),
                        (512, 512),
                    )
                    for i in range(1, 6)
                ],
                "CHEST_ANIM_CLOSE": [
                    pygame.transform.scale(
                        pygame.image.load(
                            f"./assets/UI/chest/00{i}.png"
                        ).convert_alpha(),
                        (512, 512),
                    )
                    for i in range(4, 1, -1)
                ],
                "CHEST_SURF": pygame.image.load(
                    "./assets/UI/chest/chest.png"
                ).convert_alpha(),
                "transitionTime": 1,  # s
            }
        },
        "StructureElements": {
            "Fence": {
                "surf": None,
                "rect": None,
                "placeholder": {"type": "alone", "flag": False},
                "onContact": NoContact,
                "entity": None,
            }
        },
        "NPC": {
            professionName: {
                "rect": None,
                "surf": None,
                "spawnRange": 6,
                "spawnTreshold": 3,
                "placeholder": {"type": "alone", "flag": False},
                "spawnTileCode": GREEN,
                "onContact": NoContact,
                "entity": None,
            }
            for professionName in listdir("./assets/world_textures/NPC/")
            if professionName != "stateBubble"
        },
    }

    ennemyList = listdir("./assets/world_textures/ennemy")
    ennemyList.remove("stateBubble")
    for i, ennemyName in enumerate(ennemyList):
        textureConf.WORLD_ELEMENTS["Ennemy"][ennemyName]["loots"] = [itemConf.ITEM_DB[134 + i]]

    textureConf.WORLD_ELEMENTS_STRUCTURE = {
        "Village": {
            "spawnRange": [15, 15],
            "spawnTreshold": int(15 * 15 * 0.9),  # Need 90% of green
            "spawnTileCode": openWorldConf.GREEN,
            "numberOfEntry": 4,
            "composition": {  # by order of priority
                "Building": {"PNJHouse": 1, "Shop": 1},
                "Dungeon": {"Death's Dungeon": 1},
                "NPC": {"Seller": 1, "Villager": 4},
                "Ennemy": {"Skeleton": 1},
                "Landscape": {
                    "Plains_tree": 5,  # -1 means no limit
                    "Plains_flower": 7,
                },
                "GameObject": {"Chest": 1},
            },
            "surf": pygame.transform.scale(
                pygame.image.load("./assets/world_textures/village_town/Village.png"),
                (stepGeneration, stepGeneration),
            ),
            "borderSurf": pygame.transform.scale(
                pygame.image.load(
                    "./assets/world_textures/village_town/VillageFence.png"
                ).convert_alpha(),
                (stepGeneration, stepGeneration),
            ),
        },
    }


def loadGameRessources():

    loadItemRessources()
    loadHUDRessources()
    loadMiniMapRessources()
    loadMenuRessources()
    loadPlayerRessources()
    loadSpellRessources()
    loadLandscapeRessources()
    loadOpenWorldRessources()
