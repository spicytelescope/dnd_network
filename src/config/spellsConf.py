from utils.Anim import *

from utils.utils import logger

logger.info("Loading spellConf")

# SPELL BOOK

OPEN_ANIM_TIME = 1  # s
CLOSE_ANIM_TIME = 1  # s
NEXT_ANIM_TIME = 0.750  # s
BACK_ANIM_TIME = 0.750  # s

global SPELLBOOK_BUTTONS

global SPELLBOOK_MAIN_SURF

ANIM_PATHS = {
    nameDir: f"./assets/UI/spellBook/{nameDir}"
    for nameDir in ["openAnimation", "closeAnimation", "nextAnimation", "backAnimation"]
}

global OPEN_ANIM_FRAMES

global CLOSE_ANIM_FRAMES

global NEXT_ANIM_FRAMES

global BACK_ANIM_FRAMES


# BOOK CONTENT

SPELL_INFO_SURF_DIM = [325, 110]
TITLE_CENTER_POINT_LEFT = [305, 330]
TITLE_CENTER_POINT_RIGHT = [725, 330]
SPELL_INFO_INIT_POINT = [130, 360]

SPELL_LEVEL_NAME_CENTER = [195, 18]
SPELL_INFO_DMG_ICON_POINT = [85, 60]
SPELL_INFO_DMGRANGE_ICON_POINT = [205, 60]
SPELL_INFO_ICON_DIM = [40, 40]

SPELL_NAME_FONT_SIZE = 50
SPELL_DESC_FONT_SIZE = 50

global DMG_ICON
global DMGRANGE_ICON

SPELL_ANIMATION_CENTER = [721, 483]
SPELL_ANIMATION_DIM = [235, 235]

SPELL_DESC_CENTER = [721, 650]
SPELL_DESC_SURF_DIM = [170*2, 30*2]
SPELL_DESC_SLOT_POINTS = [
    (721 - 170, 620),
    (721 + 170, 650 - 30),
    (721 + 170, 650 + 30),
    (721 - 170, 650 + 30),
]

# SPELLS

global SPELL_DB
