from .exceptions import CorruptedFileError
from .base import IAudioDescriber, Content
from dataclasses import dataclass
from .format import Description
from typing import Union
from pathlib import Path
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


def update_first_header_idx(func) -> callable:
    def wrapper(obj, *args, **kwargs):
        if obj._first_header_idx is None:
            result = obj._find_next_header_idx(start_idx=0)
            if result is None:
                raise CorruptedFileError(obj.file_path)
            obj._first_header_idx = result
        return func(obj, *args, **kwargs)
    return wrapper


class BaseDescriber(IAudioDescriber):

    def __init__(
            self,
            file_path: Union[str, Path],
            header_range: Range
            ) -> None:
        super().__init__()
        self.file_path = file_path
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
        result = (self.get_file_size() - self.__header.end)
        result /= self.get_sampling_rate()
        result /= self.get_channels_count()
        result /= (self.get_sample_width() / 8)
        return result


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

    def get_bit_rate(self) -> None:
        return None

    def get_byte_rate(self) -> None:
        return None

    def get_channels_count(self) -> int:
        buffer = self._get_buffer(FlacDescriber.__channels)
        result = mask_bytes(buffer, FlacDescriber.__channels_mask)
        return result + 1

    def get_sample_width(self) -> int:
        buffer = self._get_buffer(FlacDescriber.__sample_width)
        result = mask_bytes(buffer, FlacDescriber.__sample_width_mask)
        result = bits_shift_right(result, 4)
        return result + 1


class MP3Describer(BaseDescriber):
    """Used to describe an MP3 file, we assume that the sample rate for the
    first frame is the same for all frames

    Args:
        BaseDescriber (Union[str, Path]): the path of the mp3 file to be
        described
    """
    __header_length = 4
    __frame_sync_head = 0xff
    __frame_sync_tail = 0xe0
    __sampling_rate_shifts = 10
    __sampling_rate_mask = 3
    __mpeg_version_shifts = 19
    __mpeg_version_mask = 3
    __layer_shifts = 17
    __layer_mask = 3
    __bit_rate_shifts = 12
    __bit_rate_mask = 15
    __num_channels_shifts = 6
    __num_channels_mask = 3
    __mpeg_mapper = {
        0: 2.5,  # MPEG-2.5
        2: 2,    # MPEG-2
        3: 1     # MPEG-1
    }
    __sample_rate_mapper = [
        [11025, 12000, 8000, None],     # MPEG-2.5
        [None] * 4,                     # Reserved
        [22050, 24000, 16000, None],    # MPEG-2
        [44100, 48000, 32000, None],    # MPEG-1
        ]
    __bit_rate_mapper = [[
        [0, 32, 48, 56,  64,  80,  96, 112, 128, 144, 160, 176, 192, 224, 256, None],
        [0, 8, 16, 24,  32,  40,  48,  56,  64,  80,  96, 112, 128, 144, 160, None],
        [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None]],
        [[0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, None],
        [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, None],
        [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None]]]

    def __init__(self, file_path: Union[str, Path]) -> None:
        super().__init__(file_path, Range(0, -1))
        self.last_header_idx = 0
        self._first_header_idx = None

    def __get_first_buffer(self) -> bytes:
        return self._get_buffer(Range(self._first_header_idx,
                                self._first_header_idx + self.__header_length))

    def __get_pos_buffer(self, b_range: Union[Range, None] = None) -> bytes:
        if b_range is None:
            return self.__get_first_buffer()
        return self._get_buffer(b_range)

    def __shift_and_mask(
            self,
            buffer: bytes,
            mask: Union[hex, int],
            n_shifts: int
            ) -> int:
        return bits_shift_right(buffer, n_shifts) & mask

    def __process_first_header(
            self,
            mask: Union[hex, int],
            num_shifts: int
            ) -> int:
        buffer = self.__get_first_buffer()
        return self.__shift_and_mask(buffer, mask, num_shifts)

    def __get_sr_for_buffer(self, buffer: bytes) -> Union[int, None]:
        sr_idx = self.__shift_and_mask(
            buffer,
            self.__sampling_rate_mask,
            self.__sampling_rate_shifts
            )
        mpeg_version = self.__get_mpeg_for_buffer(buffer, with_map=False)
        return self.__sample_rate_mapper[mpeg_version][sr_idx]

    @update_first_header_idx
    def get_sampling_rate(
            self,
            b_range: Union[Range, None] = None
            ) -> Union[int, None]:
        buffer = self.__get_pos_buffer(b_range)
        return self.__get_sr_for_buffer(buffer)

    def __get_mpeg_for_buffer(
            self,
            buffer,
            with_map=False
            ) -> Union[int, None]:
        result = self.__shift_and_mask(
            buffer,
            self.__mpeg_version_mask,
            self.__mpeg_version_shifts
            )
        return self.__mpeg_mapper.get(result, None) if with_map else result

    @update_first_header_idx
    def get_mpeg_version(
            self,
            b_range: Union[Range, None] = None,
            with_map=True
            ) -> Union[float, int, None]:
        buffer = self.__get_pos_buffer(b_range)
        return self.__get_mpeg_for_buffer(buffer, with_map)

    def __get_layer_for_buffer(self, buffer: bytes) -> Union[float, int, None]:
        result = self.__shift_and_mask(
            buffer,
            self.__layer_mask,
            self.__layer_shifts
            )
        return 4 - result if result > 0 else None

    @update_first_header_idx
    def get_layer(
            self,
            b_range: Union[Range, None] = None
            ) -> Union[float, int]:
        buffer = self.__get_pos_buffer(b_range)
        return self.__get_layer_for_buffer(buffer)

    @update_first_header_idx
    def get_num_samples(self) -> None:
        return None

    @update_first_header_idx
    def get_duration(self) -> None:
        return None

    def __get_br_for_buffer(self, buffer: bytes) -> Union[int, None]:
        br_idx = self.__shift_and_mask(
            buffer,
            self.__bit_rate_mask,
            self.__bit_rate_shifts,
            )
        mpeg_version = self.__get_mpeg_for_buffer(buffer, with_map=False)
        layer = self.__get_layer_for_buffer(buffer)
        if layer is None:
            return
        return self.__bit_rate_mapper[mpeg_version & 1][layer - 1][br_idx]

    @update_first_header_idx
    def get_bit_rate(
            self,
            b_range: Union[Range, None] = None
            ) -> Union[int, None]:
        buffer = self.__get_pos_buffer(b_range)
        return self.__get_br_for_buffer(buffer)

    @update_first_header_idx
    def get_byte_rate(self) -> Union[int, None]:
        result = self.get_bit_rate()
        return None if result is None else result // 8

    @update_first_header_idx
    def get_channels_count(self):
        result = self.__process_first_header(
            self.__num_channels_mask,
            self.__num_channels_shifts
            )
        return 1 if result == 3 else 2

    @update_first_header_idx
    def get_sample_width(self):
        return None

    def _find_next_header_idx(self, start_idx=0) -> Union[int, None]:
        """Used to find the next header based on the given idx by searching for
        the synchronization bits
        Args:
            start_idx (int, optional): the starting indexof the header.
            Defaults to 0.
        """
        offset = self._content.find(self.__frame_sync_head, start_idx)
        if offset is None:
            return
        masked_tail = self._content[offset + 1] & self.__frame_sync_tail
        if masked_tail == self.__frame_sync_tail:
            return offset
        return self._find_next_header_idx(start_idx=offset)
