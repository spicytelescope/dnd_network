import random
from os import *

# ENNEMY OUT COMBAT STATE

ENNEMY_STATES = ["Walk", "Idle"]
ENNEMY_ANIM_TIME = 1.5  # s
ENNEMY_BUBBLE_ANIM_TIME = 1  # s


# IDLE RANDOM CLICKING

CLICK_TIME_RANGE = [1.5, 3.5]  # seconds
ENNEMY_DETECTION_RANGE = 2  # in term of case

# DUNGEON

ENNEMY_DUNGEON_PROB = 0.3  # in %
ENNEMY_SPAWN_RANGE = [
    3,
    2,
    1,
    1,
]  # Is linked with the game difficulty, easy mode = difficultyId 0 = scopegrid range to 3

# STATS

ENNEMIES_STAT = {
    ennemyName: {
        "STR": 8,
        "DEX": 14,
        "CON": 10,
        "INT": 10,
        "WIS": 8,
        "CHA": 8,
        "HP": 10,
        "HP_max": 10,
        "Mana": 15,
        "Mana_max": 15,
        "DEF": random.choice(range(1, 5)),
        "ATK": random.choice(range(1, 5)),
    }
    for ennemyName in listdir("./assets/world_textures/ennemy")
}
for ennemyName in ENNEMIES_STAT:
    if ennemyName == "Gobelin":
        ENNEMIES_STAT[ennemyName]["HP"] = ENNEMIES_STAT[ennemyName]["CON"] + 2
        ENNEMIES_STAT[ennemyName]["Mana"] = ENNEMIES_STAT[ennemyName]["WIS"]

    ENNEMIES_STAT[ennemyName]["HP_max"] = ENNEMIES_STAT[ennemyName]["HP"]
    ENNEMIES_STAT[ennemyName]["Mana_max"] = ENNEMIES_STAT[ennemyName]["Mana"]

ENNEMY_DEFAULT_GOLD_VALUE = {"Goblin": 2, "Flying_eye": 1, "Mushroom": 3, "Skeleton": 4}
