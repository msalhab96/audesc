from .exceptions import CorruptedFileError
from .base import IAudioDescriber, Content
from dataclasses import dataclass
from typing import Union
from pathlib import Path
from .utils import (
    bytes_to_int,
    bytes_to_short,
    mask_bytes,
    bits_shift_right
    )
from .format import Description


@dataclass
class Range:
    start: int
    end: int


class BaseDescriber(IAudioDescriber):

    def __init__(self, file_path: Union[str, Path], header_range: Range) -> None:
        super().__init__()
        self.file_path = file_path
        print(header_range.start)
        self._content = Content(
            file_path,
            start=header_range.start,
            end=header_range.end
            )

    def _get_buffer(self, slice_range: Range) -> bytes:
        return self._content[slice_range.start: slice_range.end]

    def describe(self) -> Description:
        return Description(
            self.get_duration(),
            self.get_bit_rate(),
            self.get_sampling_rate(),
            self.get_channels_count(),
            self.get_num_samples()
        )

class WaveDescriber(BaseDescriber):
    """A describer used to describe a wav file

    Args:
        file_path (Union[str, Path]): the file path to get its information
    """
    __header = Range(0, 44)
    __file_size = Range(4, 8)
    __channels = Range(22, 24)
    __sampling_rate = Range(24, 28)
    __byte_rate = Range(28, 32)
    __sample_width = Range(34, 36)
    __num_samples = Range(40, 44)

    def __init__(self, file_path: Union[str, Path]) -> None:
        super().__init__(file_path, self.__header)

    def get_file_size(self) -> int:
        return bytes_to_int(
            self._get_buffer(WaveDescriber.__file_size),
            little_endian=True
        ) + 8  # 8 for the size of (RIFF + size field)

    def get_channels_count(self) -> int:
        return int(bytes_to_short(
            self._get_buffer(WaveDescriber.__channels),
            little_endian=True
        ))

    def get_sampling_rate(self) -> int:
        return int(bytes_to_int(
            self._get_buffer(WaveDescriber.__sampling_rate),
            little_endian=True
        ))

    def get_byte_rate(self) -> int:
        return bytes_to_int(
            self._get_buffer(WaveDescriber.__byte_rate),
            little_endian=True
        )

    def get_bit_rate(self) -> int:
        return self.get_byte_rate() * 8

    def get_sample_width(self) -> int:
        return int(bytes_to_short(
            self._get_buffer(WaveDescriber.__sample_width),
            little_endian=True
        ))

    def get_num_samples(self) -> int:
        return int(bytes_to_int(
            self._get_buffer(WaveDescriber.__num_samples),
            little_endian=True
        ) / (self.get_channels_count() * self.get_sample_width()))

    def get_duration(self) -> float:
        return self.get_num_samples() / self.get_sampling_rate()


class FlacDescriber(BaseDescriber):
    __header = Range(0, 26)
    __sampling_rate = Range(18, 21)
    __max_sampling_rate = 655350
    __channels = Range(20, 21)
    __channels_mask = 0xc
    __sample_width = Range(20, 22)
    __sample_width_mask = 0x1f0
    __num_samples = Range(22, None)
    __num_samples_mask = 0xfffffffff

    def __init__(self, file_path: Union[str, Path]) -> None:
        super().__init__(file_path, self.__header)

    def get_sampling_rate(self) -> int:
        buffer = self._get_buffer(FlacDescriber.__sampling_rate)
        result = bits_shift_right(buffer, 4)
        if result > FlacDescriber.__max_sampling_rate:
            raise CorruptedFileError(self.file_path)
        return result

    def get_num_samples(self) -> int:
        buffer = self._get_buffer(FlacDescriber.__num_samples)
        result = mask_bytes(buffer, FlacDescriber.__num_samples_mask)
        return None if result == 0 else result

    def get_duration(self) -> float:
        num_samples = self.get_num_samples()
        sampling_rate = self.get_sampling_rate()
        if num_samples is None:
            return
        return num_samples / sampling_rate

    def get_bit_rate(self):
        return None

    def get_byte_rate(self):
        return None

    def get_channels_count(self):
        buffer = self._get_buffer(FlacDescriber.__channels)
        result = mask_bytes(buffer, FlacDescriber.__channels_mask)
        return result + 1

    def get_sample_width(self):
        buffer = self._get_buffer(FlacDescriber.__sample_width)
        result = mask_bytes(buffer, FlacDescriber.__sample_width_mask)
        result = bits_shift_right(result, 4)
        return result + 1

