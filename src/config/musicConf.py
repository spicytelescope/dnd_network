from utils.utils import logger
logger.info("Loading musicConf")

FADE_IN_OUT_TIME = 2000  # ms
SOUNDS_PATH = {
    "dungeon": "./assets/musics/8bit Dungeon Level.wav",
    "fight": "./assets/musics/fight.wav",
    "openWorld": "./assets/musics/biome_plaine.wav",
    "building": "./assets/musics/building.wav",
    "menu": "./assets/musics/menu.wav"
}
EFFECTS_PATH = {
    "bonk": "./assets/musics/BONK.wav",
}

global SOUNDS_BANK