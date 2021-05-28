import pygame

# ---------------- INVENTORY SETTINGS -------------- #

INVENTORY_SURF_RATIO = 1.345  # width = self.surfRatio * height

global INVENTORY_SURF

INVENTORY_ANIMATION_TIME = 750  # ms

ITEM_ICON_DIM = [46, 45]
ITEM_INFO_ICON_DIM = [70, 70]

# STORAGE

INVENTORY_STORAGE_INIT_POS = [503, 115]
INVENTORY_STORAGE_OFFSET = [55, 55]

INVENTORY_STORAGE_WIDTH = 3
INVENTORY_STORAGE_HEIGHT = 7

# INVENTORY ITEM INFORMATION

ITEM_INFO_RAW_POS_ICON = [343, 143]

ITEM_DESC_SURF_DIM = [200, 35]

ITEM_INFO_POS = {
    "slotId": ["customWidth", 200],  # center
    "typeId": ["customWidth", 200 + 30],  # center
    "durability": [408, 350],  # center
    "sellValue": [302, 350],  # center
    "name": ["customWidth", 92],  # center
    "stats": ["customWidth", 188 + 17 + 40 * 2],  # center
    "classRestriction": ["customWidth", 188 + 17 + 35 * 3],  # center
}

global ITEM_INFO_ICONS

ITEM_PROPERY_ICON_DIM = [27, 27]

# EQUIPMENT INFORMATION

EQUIPMENT_TEMPLATE = {
    0: {
        "name": "Helmet",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[135, 115]),
    },
    1: {
        "name": "RingLeft",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[80, 172]),
    },
    2: {
        "name": "Necklace",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[135, 172]),
    },
    3: {
        "name": "RingRight",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[191, 172]),
    },
    4: {
        "name": "leftHand",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[80, 226]),
    },
    5: {
        "name": "plate",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[135, 226]),
    },
    6: {
        "name": "rightHand",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[191, 226]),
    },
    7: {
        "name": "potion1",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[80, 281]),
    },
    8: {
        "name": "potion2",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[135, 281]),
    },
    9: {
        "name": "potion3",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[191, 281]),
    },
    10: {
        "name": "relic",
        "item": None,
        "slotRect": pygame.Surface(ITEM_ICON_DIM).get_rect(center=[135, 335]),
    },
}

# STAT INFORMATION
STAT_BLIT_POINTS = {
    "STR": [88, 411],
    "DEX": [88, 451],
    "CON": [150, 411],
    "INT": [212, 411],
    "WIS": [150, 451],
    "CHA": [212, 451],
    "HP": [274 + 25, 411],
    "Mana": [274 + 25, 451],
    "Money": [274 + 95, 411],
    "DEF": [274 + 95, 451],
    "ATK": [274 + 2 * 60 + 30, (451 + 411) // 2],
}

# HUD SETTINGS

HEALTH_BAR = {"color": (208, 2, 2), "initPoint": [0, 250]}

MANA_BAR = {"color": (2, 23, 127), "initPoint": [0, 310]}

EXP_BAR = {"color": (255, 247, 32), "initPoint": [0, 370]}


BAR_CONTENT_DIM = [196, 32]
BAR_CONTENT_BLITPOINT = [30, 16]
global BAR_IMG
global PLAYER_ICON_SLOT
global NAME_SLOT

# QUEST JOURNAL


global QUEST_JOURNAL_MAIN_SURF
global QUEST_OPEN_ANIM_FRAMES
global QUEST_CLOSE_ANIM_FRAMES
global QUEST_PROGRESS_BAR
global QUEST_COMPLETED_BAR


QUEST_ANIM_PATHS = {
    nameDir: f"./assets/UI/questJournal/{nameDir}"
    for nameDir in ["openAnimation", "closeAnimation"]
}

QUEST_OPEN_ANIM_TIME = 1  # s
QUEST_CLOSE_ANIM_TIME = 1  # s


