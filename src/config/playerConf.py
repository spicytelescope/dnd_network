from utils.utils import logger
import random
logger.info("Loading playerConf")

# ------------ TEAM SETTINGS ---------------- #
MAX_TEAM_LENGH = 3
MAX_NAME_LENGTH = 20

# ----------- PLAYER SETTINGS  --------------- #

PLAYER_SIZE = 32  # Pixels
PLAYER_ANIMATION_FRAME_LENGTH = 4
PLAYER_ANIMATION_DURATION = 1  # Seconds
PLAYER_DIRECTIONS = ["left", "right", "up", "down"]
CLASSES_NAMES = ["Warrior", "Wizard", "Hunter"]
BASE_HITBOX = PLAYER_SIZE
BASE_HITBOX_ZOOMED = 60
DEFAULT_NUM_ITEM = 5

ITEM_PICK_UP_RANGE = 40 # pixels

global CLASSES
CLASSES_DEFAULT_STATS = {
    "Warrior": {
        "STR": random.randint(13, 19),
        "DEX": random.randint(10, 15),
        "CON": random.randint(13, 19),
        "INT": random.randint(8, 13),
        "WIS": random.randint(13, 19),
        "CHA": random.randint(15, 16),
        "HP": 15,
        "HP_max": 15,
        "Mana": 10,
        "Mana_max": 10,
        "Money": random.choice(range(15, 30)),
        "DEF": random.choice(range(1, 5)),
        "ATK": random.choice(range(1, 5)),
    },
    "Wizard": {
        "STR": random.randint(7, 12),
        "DEX": random.randint(10, 15),
        "CON": random.randint(13, 19),
        "INT": random.randint(13, 19),
        "WIS": random.randint(13, 19),
        "CHA": random.randint(13, 16),
        "HP": 10,
        "HP_max": 10,
        "Mana": 15,
        "Mana_max": 15,
        "Money": random.choice(range(15, 30)),
        "DEF": random.choice(range(1, 5)),
        "ATK": random.choice(range(1, 5)),
    },
    "Hunter" : {
            "STR": random.randint(10,15),
            "DEX": random.randint(13,19),
            "CON": random.randint(13,19),
            "INT": random.randint(13,19),
            "WIS": random.randint(13,19),
            "CHA": random.randint(13,19),
            "HP": 10,
            "HP_max": 10,
            "Mana": 15,
            "Mana_max": 15,
            "Money": random.choice(range(15, 30)),
            "DEF": random.choice(range(1, 5)),
            "ATK": random.choice(range(1, 5)),
        },
}

# Setting afterwards the HP/MANA :

for className in CLASSES_NAMES:
    if className == "Warrior":
        CLASSES_DEFAULT_STATS[className]["HP"] = (
            CLASSES_DEFAULT_STATS[className]["CON"] + 2
        )
        CLASSES_DEFAULT_STATS[className]["Mana"] = CLASSES_DEFAULT_STATS[className][
            "WIS"
        ]

    elif className == "Wizard":
        CLASSES_DEFAULT_STATS[className]["HP"] = CLASSES_DEFAULT_STATS[className]["CON"]
        CLASSES_DEFAULT_STATS[className]["Mana"] = (
            CLASSES_DEFAULT_STATS[className]["WIS"] + 5
        )

    elif className == "Hunter":
        CLASSES_DEFAULT_STATS[className]["HP"] = CLASSES_DEFAULT_STATS[className]["CON"]
        CLASSES_DEFAULT_STATS[className]["Mana"] = CLASSES_DEFAULT_STATS[className][
            "WIS"
        ]

    CLASSES_DEFAULT_STATS[className]["HP_max"] = CLASSES_DEFAULT_STATS[className]["HP"]
    CLASSES_DEFAULT_STATS[className]["Mana_max"] = CLASSES_DEFAULT_STATS[className]["Mana"]

# Hero Inventory Storage

INVENTORY_STORAGE_INIT_POS_CHEST = [65, 115]

# ----------------------- RESTING MECHANICSS -------------------- #

TURN_REST = 3 # Number of turns without taking damage/attacking before the player gains 1 hp
TIME_OUT_REST = 60*2 # seconds before the player gains 2 hps
