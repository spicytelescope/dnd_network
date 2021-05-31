import struct
import os
import json
from config.netConf import *
import errno
from subprocess import call


def encode_msg_size(size: int) -> bytes:
    return struct.pack("<I", size)


def decode_msg_size(size_bytes: bytes) -> int:
    return struct.unpack("<I", size_bytes)[0]


def create_msg(content: bytes) -> bytes:
    size = len(content)
    return encode_msg_size(size) + content


def get_raw_data_to_str(fifo: int) -> str:
    """Get a message from the named pipe."""

    #  Handling non-blocking mode
    try:
        msg_size_bytes = os.read(fifo, 4)
    except OSError as err:
        if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
            msg_size_bytes = b""
        else:
            raise  # something else has happened -- better reraise

    if msg_size_bytes == b"":
        return ""
    else:
        msg_size = decode_msg_size(msg_size_bytes)
        msg_content = os.read(fifo, msg_size)#.decode("utf8")
        return msg_content


def write_to_pipe(fifo_path: str, packet: dict) -> None:

    fifo = os.open(fifo_path, os.O_WRONLY)
    user_encode_data = json.dumps(packet, indent=2).encode("utf-8")
    os.write(fifo, create_msg(user_encode_data))
    os.close(fifo)

def run_C_client(c_client_name: str) -> None:
    call