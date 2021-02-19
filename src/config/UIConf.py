import pygame
from pygame import Color

from utils.utils import logger

logger.info("Loading UI Conf")

DUNGEON_FONT = "./assets/fonts/DUNGRG__.ttf"
TITLE_FONT_SIZE = 180

# ------------ BUTTON SETTINGS ---------------- #

BUTTON_FONT_SIZE = 35
BUTTON_PADDING = [75, 20]
BUTTON_FONT_NAME = "dejavusansmono"

BUTTON_SURFS = [
    pygame.image.load(f"./assets/UI/buttons/{name}.png")
    for name in ["Button_default", "Button_hovered"]
]

# -------------- SELECT BUTTONS SETTINGS --------- #

# 0 and 2 = left ; 1 and 3 = right
SELECT_BUTTONS = [
    pygame.image.load(f"./assets/UI/buttons/select_{direction}.png")
    for direction in ["left", "right"]
] + [
    pygame.image.load(f"./assets/UI/buttons/select_{direction}_clicked.png")
    for direction in ["left", "right"]
]

# --------- UP BUTTONS SETTINGS ---------- #

UP_BUTTONS = [
    pygame.image.load(f"./assets/UI/buttons/button_{direction}.png")
    for direction in ["down", "up"]
] + [
    pygame.image.load(f"./assets/UI/buttons/button_{direction}_clicked.png")
    for direction in ["down", "up"]
]


# ------------ TEXT BOX SETTINGS ------------- #

TEXT_FONT_SIZE = 40
TEXTBOX_LAYOUT = pygame.image.load("./assets/UI/textBox/TextBoxLayout.png")
NEXT_BUTTON = pygame.image.load("./assets/UI/textBox/nextButton.png")
NEXT_BUTTON_HOVERED = pygame.image.load("./assets/UI/textBox/nextButtonHovered.png")

DEFAULT_CHAR_LIMIT = 60

# ---------------- INFO TIP ----------------- #

INFOTIP_WIDTH = 60
INFOTIP_DESC_FONT_SIZE = 30


def infoTipLines(mousePos, direction, textLen):
    factor = 1 if direction == "left" else -1
    return [
        mousePos,
        (mousePos[0] + INFOTIP_WIDTH * factor, mousePos[1] - 50),
        (mousePos[0] + (INFOTIP_WIDTH + textLen) * factor, mousePos[1] - 50),
    ]


# ------------------- WORLD TRANSITION ------------------- #

WORLD_TRANS_TIME = 1.5
WORLD_TRANS_ALPHA_SEC = 255 // WORLD_TRANS_TIME

# CURSORS

CURSORS_SURF = {
    "main": pygame.image.load("./assets/cursors/main.png"),
    "interact": pygame.image.load("./assets/cursors/interact.png"),
}

# TRADING UI

TRADING_SURF = pygame.image.load("./assets/UI/TradeUI/TradeUI.png")

NAME_SLOT_1 = [85, 60]
NAME_SLOT_2 = [85, 180]

LOCK_BUTTON_POS = [85, 120]

TARGET_INIT_POINT = [177, 65]
PLAYER_INIT_POINT = [177, 185]

# CONTEXTUAL MENU

TRADE_LOCK_BTN = pygame.image.load("./assets/UI/TradeUI/lock_btn.png")
TRADE_LOCK_BTN_CLICKED = pygame.image.load("./assets/UI/TradeUI/lock_btn_clicked.png")

POP_UP_ACTIONS = (
    "Character Options",
    "Inventory",
    "Spellbook",
    "Trade",
    "Fight",
    # (
    #     'Things',
    #     'Item 0',
    #     'Item 1',
    #     'Item 2',
    #     (
    #         'More Things',
    #         'Item 0',
    #         'Item 1',
    #     ),
    # ),
)


bg_color = Color("grey")
hi_color = Color(155, 155, 155)
text_color = Color("black")
glint_color = Color(220, 220, 220)
shadow_color = Color(105, 105, 105)

margin = 15