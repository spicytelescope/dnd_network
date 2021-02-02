import pygame

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
    return (
        [
            mousePos,
            (mousePos[0] + INFOTIP_WIDTH*factor, mousePos[1] - 50),
            (mousePos[0] + (INFOTIP_WIDTH+textLen)*factor, mousePos[1] - 50),
        ]
    )


# ------------------- WORLD TRANSITION ------------------- #

WORLD_TRANS_TIME = 1.5
WORLD_TRANS_ALPHA_SEC = 255//WORLD_TRANS_TIME

# CURSORS

CURSORS_SURF = {
    "main": pygame.image.load("./assets/cursors/main.png"),
    "interact": pygame.image.load("./assets/cursors/interact.png")
}