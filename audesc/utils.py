import os
import struct
from constants import (
                        INT_LITTLE_ENDIAN,
                        INT_BIG_ENDIAN,
                        SHORT_LITTLE_ENDIAN,
                        SHORT_BIG_ENDIAN
                        )


def get_file_extension(file_name: str) -> str:
    """Used to extract the file's extension from
    file_name

    Args:
        file_name (str): the file name of the

    Returns:
        str: the extension of the file
    """
    extension = os.path.splitext(file_name)[1]
    extension = extension.replace('.', '')
    extension = extension.strip()
    return extension


def bytes_to_int(buffer:  bytes, little_endian=True) -> int:
    if little_endian:
        int_struct = struct.Struct(INT_LITTLE_ENDIAN)
    else:
        int_struct = struct.Struct(INT_BIG_ENDIAN)
    return int_struct.unpack(buffer)[0]


def bytes_to_short(buffer:  bytes, little_endian=True) -> int:
    if little_endian:
        int_struct = struct.Struct(SHORT_LITTLE_ENDIAN)
    else:
        int_struct = struct.Struct(SHORT_BIG_ENDIAN)
    return int_struct.unpack(buffer)[0]


def bits_shift_right(buffer_data: bytes, n_shifts: int) -> int:
    """Shifts the bits of the buffer n_shifts to the left
    0xf0 becomes 0x0f if n_shifts is 4, in binary 11110000
    becomes 00001111

    Args:
        buffer_data (bytes or int): the bytes to be shifted
        n_shifts (int): number of bits to be shifted

    Returns:
        int: [description]
    """
    if isinstance(buffer_data, bytes):
        hex_buffer = buffer_data.hex()
        return int(hex_buffer, base=16) >> n_shifts
    elif isinstance(buffer_data, int):
        return buffer_data >> n_shifts
    else:
        raise ValueError()


def bits_shift_left(buffer_data, n_shifts: int) -> int:
    """Shifts the bits of the buffer n_shifts to the left
    0xf0 becomes 0xf00 if n_shifts is 4, in binary 11110000
    becomes 111100000000

    Args:
        buffer_data (bytes or int): the bytes to be shifted
        n_shifts (int): number of bits to be shifted

    Returns:
        int: [description]
    """
    if isinstance(buffer_data, bytes):
        hex_buffer = buffer_data.hex()
        return int(hex_buffer, base=16) << n_shifts
    elif isinstance(buffer_data, int):
        return buffer_data << n_shifts
    else:
        raise ValueError()


def mask_bytes(buffer: bytes, mask: hex) -> int:
    """masks the buffer's bytes by the mask

    Args:
        buffer (bytes): the bytes to be masked by the mask
        mask (hex): the mask in hex to mask the buffers' bytes

    Returns:
        int: [description]
    """
    hex_buffer = buffer.hex()
    return int(hex_buffer, base=16) & mask
