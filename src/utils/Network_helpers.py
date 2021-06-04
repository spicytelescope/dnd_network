from datetime import datetime
import struct
import os
import json
from config.netConf import *
import errno
from subprocess import call


def encode_msg_size(size: int) -> bytes:
    return struct.pack("<I", size)


def decode_msg_size(size_bytes: bytes) -> int:
    # return struct.unpack("<I", size_bytes)[0]
    # FIFO's output are in little endian
    return int.from_bytes(size_bytes, byteorder="little")


def create_msg(content: bytes) -> bytes:
    size = len(content)
    return encode_msg_size(size) + content


def get_raw_data_to_str(isCreator: bool) -> str:
    """Get a message from a named pipe.

    ---
    ## Args
        - isCreator (boolean): Wether the user joins or creates a game
    """
    #  Handling non-blocking mode
    # try:
    fifo = os.open(
        IPC_FIFO_INPUT,
        os.O_RDONLY,
    )
    msg_size_bytes = os.read(fifo, 4)
    os.close(fifo)
    msg_size = decode_msg_size(msg_size_bytes)

    # except OSError as err:
    #     if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
    #         return ""
    #     else:
    #         print("Unknown error :/")
    #         raise  # something else has happened -- better reraise

    # try:
    fifo = os.open(
        IPC_FIFO_OUTPUT,
        os.O_RDONLY,
    )
    msg_content = os.read(fifo, msg_size).decode("latin-1")
    os.close(fifo)
    return msg_content

    # except OSError as err:
    #     if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
    #         return ""
    #     else:
    #         print("Unknown error :/")
    #         raise  # something else has happened -- better reraise


def write_to_pipe(fifo_path: str, packet: dict) -> None:

    fifo = os.open(fifo_path, os.O_WRONLY)
    user_encode_data = json.dumps(packet, indent=2).encode("latin-1")
    os.write(fifo, create_msg(user_encode_data))
    os.close(fifo)


def run_C_client(ip_addr: str = "") -> None:
    call(C_CLIENT_PATH) if ip_addr != "" else call([C_CLIENT_PATH, ip_addr])


def dump_network_logs(packet_loss: float) -> None:

    header = f'NETWORK SESSION - {datetime.today().strftime("%Y-%m-%d-%H:%M:%S")}'
    packet_loss_segment = f"\n packet_loss : {100*packet_loss:.2f}%"
    with open("session.log", "w") as f:
        f.write(header + packet_loss_segment)