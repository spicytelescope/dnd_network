import random

# NPC Settings

NPC_STATES = ["Quest", "Interactable", "Talk-only"]
NPC_ANIM_TIME = 1  # s
NPC_BUBBLE_ANIM_TIME = 1  # s


# Dialogs

NPC_DIALOGS = {
    "Seller": [
        "Hello there, lil' adventurer ! What brings you here ma boi ? I heard there were plenty of things to do around here, but I guess you need some nice material, guess what ? It's your lucky day ! Wanna see what I've got ?"
    ],
    "Villager": [
        "Well, I saw a huge dungeon not far apart the dungeon, how are we gonna do ????",
        "Hey there, the sun is pretty good to bear right now !",
    ],
}

# UI Seller

global UI_SELLER_SURF

SELLER_STORAGE_INIT_POS = [64, 446]
SELLER_STORAGE_OFFSET = [57, 60]

SELLER_STORAGE_WIDTH = 3
SELLER_STORAGE_HEIGHT = 6

MIN_SELLER_NUM_ITEM = 5
MAX_SELLER_NUM_ITEM = 15

# SELLER ITEM INFORMATION

SELLER_INFO_RAW_POS_ICON = [120, 160]
GOLD_AMOUNT_BLIT_POS = [134, 795]
SELLER_ITEM_INFO_POS = {
    "slotId": [16, 200],  # topleft
    "typeId": [230, 200],  # topright
    "durability": [205, 360],  # center
    "sellValue": [100, 360],  # center
    "name": ["customWidth", 100],  # center
    "stats": ["customWidth", 200 + 17 + 35 * 2],  # center
    "classRestriction": ["customWidth", 200 + 17 + 35 * 3],  # center
}


# Quests

# If the some task's name are about the player's stat, the value to obtain in addition of the current's player stat is defined here
# The absolute amount to obtain will be update according to the player's stat in the NPC class !

NPC_QUESTS = [
    {
        "name": "Skeleton's Invasion",
        "tasks": {
            "Item1": {"Skeleton skull": 1},
            "Money": 50,
        },
        "reward": {
            "Money": 50,
            "Item1": random.randint(1, 100),
            "Item2": random.randint(1, 100),
        },  # ids of the items
        "desc": "The skeletons invaded our village ! We, the villagers, do not feel in security. Please Hero, can you get rid of them ?",
        "textReward": "We will be forever grateful to you for securing the Village ! Please, accept these rewards !",
    },
    {
        "name": "Skeleton's Invasion",
        "tasks": {
            "Item1": {"Skeleton skull": 2},
            "Money": 50,
        },
        "reward": {
            "Money": 50,
            "Item1": random.randint(1, 100),
            "Item2": random.randint(1, 100),
        },  # ids of the items
        "desc": "The skeletons invaded our village ! We, the villagers, do not feel in security. Please Hero, can you get rid of them ?",
        "textReward": "We will be forever grateful to you for securing the Village ! Please, accept these rewards !",
    },
]