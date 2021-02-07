from os import listdir
from typing import Tuple
from math import *
import random


#  ------------------ DUNGEON ------------------- #


# Safe range to spawn nothing on the player
SAFE_PLAYER_RANGE = 1
#  BUILDINGS CORRIDORS
CORRIOR_PADDING = 10  # Pixels
DUNGEON_FOG = 5  # In tiles

# ---------------  ZONE SETTINGS ----------------- #


def createChunkCoorListFromRadius(center: Tuple[int, int], radius: int):
    """Return a list of chunkCoors within a circle determined by a center and a radius"""

    return [
        (i, j)
        for i in range(center[0] - radius, center[0] + (radius + 1))
        for j in range(center[1] - radius, center[1] + (radius + 1))
        if sqrt((i - center[0]) ** 2 + (j - center[1]) ** 2) <= radius
    ]


#  Loading biome template

BIOME_LANDSCAPE_NAME = ["tree", "rock", "random_wood", "flower"]
BIOME_NAMES = ["snow", "plains", "sand", "mountain"]

# World Color settings (biomes)
WATER = (65, 105, 225)
GREEN = (34, 139, 34)
BEACH = (238, 214, 175)
SNOW = (255, 250, 250)
MOUNTAIN = (139, 137, 137)

BIOME_COLORS = {"snow": SNOW, "plains": GREEN,
                "mountain": MOUNTAIN, "sand": BEACH}

# ------------------ RANDOM GENERATION ------------------- #
# Link probability to spawn at each rendering

BUILDING_NAMES_RANDOM_GEN = {"Building": {"Temple": 0.25, "Shop_Caravan": 0.1}}
STRUCTS_NAMES_RANDOM_GEN = {"Village": 0.5}

# ----------------- DETERMINISTIC GENERATION ----------------- #

# Defines the number of structures to generate in some zones
#  The numbers here need

DEPART_ZONE = {
    "elements": {
        # "NPC": {"Seller": 1},
        # "Building": {"PNJHouse": 2},
        # "GameObject": {"Chest": 1},
    },
    "structures": {"Village": 1},
    "chunkCoorList": createChunkCoorListFromRadius((0, 0), 1),
}


DANGER_ZONE = {
    "elements": {
        # "NPC": {"Seller": 1},
        "Ennemy": {
            "Skeleton": 0
        }
        # "Building": {"PNJHouse": 2},
        # "GameObject": {"Chest": 1},
    },
    "structures": {},
    "chunkCoorList": createChunkCoorListFromRadius((0, -1), 1),
}

ZONE_1 = {
    "elements": {
        # "NPC": {"Seller": 1},
        # "Building": {"PNJHouse": 2},
        # "GameObject": {"Chest": 1},
    },
    "structures": {"Village": 1},
    "chunkCoorList": createChunkCoorListFromRadius((0, -3), 2),
}

ZONE_2 = {
    "elements": {
        # "NPC": {"Seller": 1},
        # "Building": {"PNJHouse": 2},
        # "GameObject": {"Chest": 1},
    },
    "structures": {"Village": 1},
    "chunkCoorList": createChunkCoorListFromRadius((2, 2), 1),
}
