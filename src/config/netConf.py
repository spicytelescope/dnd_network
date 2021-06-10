import string
from config.defaultConf import *

# ------------- GENERAL NETWORK SETTINGS ----------#

DEFAULT_ADDR = "127.0.0.1"
DEFAULT_PORT = 3000
ONLINE_DIALOG_COLOR = (75, 181, 67)
PLAYER_DECONNECTION_TIMEOUT = 10  # min

# ------------ C CLIENTS --------------- #

C_CLIENT_PATH = "./network/bin/client"

# --------------- GENERAL SYSTEM SETTINGS -------------- #

POLLIN_TIMEOUT = 2  # seconds

IPC_FIFO_OUTPUT = "/tmp/info_output"
IPC_FIFO_INPUT = "/tmp/info_input"

# 2 Clients way (localhost only)

IPC_FIFO_INPUT_CREA = "/tmp/info_input_creator"
IPC_FIFO_OUTPUT_CREA = "/tmp/info_output_creator"

IPC_FIFO_INPUT_JOINER = "/tmp/info_input_joiner"
IPC_FIFO_OUTPUT_JOINER = "/tmp/info_output_joiner"

FIFO_PATH_CREA_TO_JOINER = "/tmp/crea_to_joiner"
FIFO_PATH_JOINER_TO_CREA = "/tmp/joiner_to_crea"

OPEN_CONNEXION_BYTE = b"\xfa"
DECONNECTION_TIMEOUT_BYTES = b"\xfb"
DECONNECTION_MANUAL_BYTES = b"\xfc"
# Client double pipes ways nomenclature : (in | out)put_fifo_{id}

# ------------------ CHAT ----------------- #

ACCEPTED = string.ascii_letters + string.digits + string.punctuation + " " + "éè"
KEY_REPEAT_SETTING = (200, 70)

CHAT_WINDOW_DIM = (int(WINDOW_SIZE[0] * 0.6), WINDOW_SIZE[1] // 4)
CHAT_TEXTBOX_DIM = (CHAT_WINDOW_DIM[0], CHAT_WINDOW_DIM[1] // 6)
BLINK_TIME_OUT = 500  # ms
CHAT_FONT_SIZE = 20
CHAR_LIMIT_DEFAULT = 40  # Set accordingly to the CHAT_FONT_SIZE

SCROLL_VALUE = 15  # pixels
VERTICAL_SPACING = 30  # pixels

CHAT_COLORS = {
    "CONNEXION": (0, 255, 00),
    "DECONNEXION": (255, 0, 0),
    "DEFAULT": (255, 255, 255),
}
WELCOME_MESSAGE = (
    "",
    "Welcome in the chat ! Type '/help' to get the command's list",
    CHAT_COLORS["CONNEXION"],
    True,
)
