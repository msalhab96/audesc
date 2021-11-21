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
