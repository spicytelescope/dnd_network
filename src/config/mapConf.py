from config.eventConf import ANIMATE_WATER_EVENT_ID
from utils.utils import logger
logger.info("Loading mapConf")

ZOOM_FACTOR = 2  # up it = zoom in

# Some limits value for the zoom (one is obviously 0 for the zoom out)
MAX_ZOOM_IN_VALUE = 4000
MAX_ZOOM_OUT_VALUE = 0

# Perlin Noise Settings
OCTAVES_DEFAULT = 6
PERSISTENCE_DEFAULT = 0.5
LACUNARITY_DEFAULT = 3.0

# OFFSET VALUES

MAX_RENDER_DISTANCE = 4
MAX_BIOMES = 8
MIN_BIOMES = 2
MAX_STEP_GENERATION = 64  # pixels
MIN_CHUNK_SUBDIVISON = 1024 // MAX_STEP_GENERATION

# Map Configuration Settings

WORLD_MAP_CONFIG = {
    "id": 0,
    "DEFAULT_VIEW_SCALE": 250,
    "LOD": 0,
    "CIRCULAR_MAP": False,
    "STEP_GENERATION": 1,
    "ANIMATE_WATER": {
        "enabled": True,
    },
}

PLAYER_CONFIG = {
    "id": 1,
    "DEFAULT_VIEW_SCALE": 3650,
    "LOD": 6,  # Random LOD for the beggining, cuz' this one is relative to a max level of details defined from CHUNK_SIZE
    "STEP_GENERATION": 64,
    "CIRCULAR_MAP": False,
    "ANIMATE_WATER": {
        "enabled": False,
        "eventId": ANIMATE_WATER_EVENT_ID,
        "animation_delay": 1000,  # ms
    },
}

# ELements' Generation Settings
# These values are layer, 1 layer = 3x3 square check

# Determine the scope (in term of square of X by X) to spawn a tree,
SCOPE_SQUARE_TREE_DEFAULT = 8
# Determine the scope (in term of square of X by X) to spawn a rock
SCOPE_SQUARE_ROCK_DEFAULT = 4

# Determine the minimium amount of grass in the square checked to generate a tree
TREE_GEN_TRESHOLD_DEFAULT = 4
# Determine the minimium amount of sand in the square checked to generate a rock
ROCK_GEN_TRESHOLD_DEFAULT = 4


# MINIMAP SETTINGS

MINIMAP_ZOOM_RATIO = 0.65  # Ratio between the chunk size and the actuel player vision
assert MINIMAP_ZOOM_RATIO < (2 / 3), f"<ERROR> : MINIMAP_ZOOM_RATIO too high"

global EXTENDED_MINIMAP_BG
global EXTENDED_MAP_LAYOUT
global BAR_MAP_LAYOUT_LOCAL_AREA
global BAR_MAP_LAYOUT_WORLD_AREA

# TILED MAP

# Dict to convert_alpha tile ID from "Tiled" tilesets to elements of the game
TILED_FRAMEWORK_CONVERT = {
    "Chest": [29, 13, 53],
}

TILED_GROUND_ID = [48, 49, 65, 68, 96, 83, 84, 99, 100, 119, 120, 102, 116, 62]

BUILDING_MAP_SIZE = 32

BUILDING_TRANSITION_TIME = 0.75  # Seconds
