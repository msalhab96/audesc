from .exceptions import CorruptedFileError
from .base import AudioDescriber, Content
from dataclasses import dataclass
from .utils import (
    bytes_to_int,
    bytes_to_short,
    mask_bytes,
    bits_shift_right
    )


@dataclass
class Range:
    start: int
    end: int


class BaseDescriber(AudioDescriber):
    header = Range(None, None)

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path
        self.content = Content(
            file_path,
            start=self.header.start,
            end=self.header.end
            )

    def _get_buffer(self, slice_range: Range) -> bytes:
        return self.content[slice_range.start: slice_range.end]


class WaveDescriber(BaseDescriber):
    header = Range(0, 44)
    file_size = Range(4, 8)
    channels = Range(22, 24)
    sampling_rate = Range(24, 28)
    byte_rate = Range(28, 32)
    sample_width = Range(34, 36)
    num_samples = Range(40, 44)

    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)

    def get_file_size(self) -> int:
        return bytes_to_int(
            self._get_buffer(WaveDescriber.file_size),
            little_endian=True
        ) + 8  # 8 for the size of (RIFF + size field)

    def get_channels_count(self) -> int:
        return int(bytes_to_short(
            self._get_buffer(WaveDescriber.channels),
            little_endian=True
        ))

    def get_sampling_rate(self) -> int:
        return int(bytes_to_int(
            self._get_buffer(WaveDescriber.sampling_rate),
            little_endian=True
        ))

    def get_byte_rate(self) -> int:
        return bytes_to_int(
            self._get_buffer(WaveDescriber.byte_rate),
            little_endian=True
        )

    def get_bit_rate(self) -> int:
        return self.get_byte_rate() * 8

    def get_sample_width(self) -> int:
        return int(bytes_to_short(
            self._get_buffer(WaveDescriber.sample_width),
            little_endian=True
        ))

    def get_num_samples(self) -> int:
        return int(bytes_to_int(
            self._get_buffer(WaveDescriber.num_samples),
            little_endian=True
        ) / (self.get_channels_count() * self.get_sample_width()))

    def get_duration(self) -> float:
        return self.get_num_samples() / self.get_sampling_rate()


class FlacDescriber(BaseDescriber):
    header = Range(0, 26)
    sampling_rate = Range(18, 21)
    max_sampling_rate = 655350
    channels = Range(20, 21)
    channels_mask = 0xc
    sample_width = Range(20, 22)
    sample_width_mask = 0x1f0
    num_samples = Range(22, None)
    num_samples_mask = 0xfffffffff

    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)

    def get_sampling_rate(self) -> int:
        buffer = self._get_buffer(FlacDescriber.sampling_rate)
        result = bits_shift_right(buffer, 4)
        if result > FlacDescriber.max_sampling_rate:
            raise CorruptedFileError(self.file_path)
        return result

    def get_num_samples(self) -> int:
        buffer = self._get_buffer(FlacDescriber.num_samples)
        result = mask_bytes(buffer, FlacDescriber.num_samples_mask)
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
        buffer = self._get_buffer(FlacDescriber.channels)
        result = mask_bytes(buffer, FlacDescriber.channels_mask)
        return result + 1

    def get_sample_width(self):
        buffer = self._get_buffer(FlacDescriber.sample_width)
        result = mask_bytes(buffer, FlacDescriber.sample_width_mask)
        result = bits_shift_right(result, 4)
        return result + 1
