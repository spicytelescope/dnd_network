# ------------- GENERAL NETWORK SETTINGS ----------#

DEFAULT_ADDR = "127.0.0.1"
DEFAULT_PORT = 3000
ONLINE_DIALOG_COLOR = (75, 181, 67)

# ------------ C CLIENTS --------------- #

CLIENT_BIN_DIR = "./network/bin"

# --------------- GENERAL SYSTEM SETTINGS -------------- #

POLLIN_TIMEOUT = 2 # seconds

# 2 Clients way (localhost only)

IPC_FIFO_INPUT_CREA = "/tmp/info_input_creator"
IPC_FIFO_OUTPUT_CREA = "/tmp/info_output_creator"

IPC_FIFO_INPUT_JOINER = "/tmp/info_input_joiner"
IPC_FIFO_OUTPUT_JOINER = "/tmp/info_output_joiner"

FIFO_PATH_CREA_TO_JOINER = "/tmp/crea_to_joiner"
FIFO_PATH_JOINER_TO_CREA = "/tmp/joiner_to_crea"

# Client double pipes ways nomenclature : (in | out)put_fifo_{id}