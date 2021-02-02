from os import listdir
from utils.utils import logger

logger.info("Loading itemConf")

# ------------- ITEMS SETTINGS ---------- #

ITEM_ANIM_TIME = 2 # Seconds
ITEM_ANIM_OFFSET = 15 # Pixels
# set the range where the items falls from the player pos
ITEM_LOOT_RANGE = 32 # Pixels
ITEM_TIMEOUT_LOOT = 2

ITEM_SLOT_TYPES = {
    0: "Head",
    1: "RingLeft",
    2: "Necklace",
    3: "RingRight",
    4: "LeftHand",
    5: "Chest",
    6: "RightHand",
    7: "Potion 1",
    8: "Foot",
    9: "Potion 2",
    10: "Relic",
}

ITEM_TYPES = {
    0: "Staff",  # 2 Hand
    1: "Helmet",
    2: "Gloves",
    3: "Plate",
    4: "Boots",
    5: "Relic",
    6: "Potion",
    7: "Bow",  # 2 Hand
    8: "Shield",
    9: "Dagger",
    10: "Sword",
    11: "DoubleSword",  # 2 Hand
    12: "Hammer",  # 2 Hand
    13: "Wand",
    14: "Axe",  # 1 Hand
    15: "Mace",  #  1 Hand
    16: "Small Hammer",
    17: "DoubleAxe",  # 2 Hand
    18: "Double Mace",  #  2 Hand
}

WEAPON_2_HAND_IDS = [0, 7, 11, 12, 14, 17, 18]

global ITEM_DB

RARETY_TYPES = {
    "common": {"color": (255, 255, 255), "itemWorthMultiplier": 1.5},
    "legendary": {"color": (230, 132, 39), "itemWorthMultiplier": 2},
    "mythic": {"color": (180, 56, 175), "itemWorthMultiplier": 2.5},
    "rare": {"color": (50, 94, 170), "itemWorthMultiplier": 3},
    "uncommon": {"color": (87, 202, 42), "itemWorthMultiplier": 3.5},
}

# ----------------- CHEST --------------------- #

# STORAGE

CHEST_STORAGE_INIT_POS = [503, 115]
CHEST_STORAGE_OFFSET = [56, 55]

CHEST_STORAGE_WIDTH = 7
CHEST_STORAGE_HEIGHT = 7

DEFAULT_NUM_CHEST_MIN = 2
DEFAULT_NUM_CHEST_MAX = 8

if __name__ == "__main__":
    assetPath = "../assets/Items/Transparent/"

    dirNames = [f for name in ITEM_TYPES.values() for f in listdir(assetPath + name)]
