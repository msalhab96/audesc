from base import AudioDescriber, Content
from dataclasses import dataclass
from utils import bytes_to_int, bytes_to_short


@dataclass
class Range:
    start: int
    end: int


class WaveDescriber(AudioDescriber):
    header = Range(0, 44)
    file_size = Range(4, 8)
    channels = Range(22, 24)
    sampling_rate = Range(24, 28)
    byte_rate = Range(28, 32)
    sample_width = Range(34, 36)
    num_samples = Range(40, 44)

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.content = Content(
            file_path,
            start=WaveDescriber.header.start,
            end=WaveDescriber.header.end
            )

    def _get_buffer(self, slice_range: Range) -> bytes:
        return self.content[slice_range.start: slice_range.end]

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
        )) // 8

    def get_num_samples(self) -> int:
        return int(bytes_to_int(
            self._get_buffer(WaveDescriber.num_samples),
            little_endian=True
        ) / (self.get_channels_count() * self.get_sample_width()))

    def get_duration(self) -> float:
        return self.get_num_samples() / self.get_sampling_rate()
