from dataclasses import dataclass
from typing import Union


@dataclass
class Description:
    duration: Union[float, None]
    bit_rate: Union[int, None]
    sampling_rate: Union[int, None]
    channels_count: Union[int, None]
    num_samples: Union[int, None]

    @property
    def number_of_samples(self) -> int:
        return int(self.sampling_rate * self.duration)

    def __str__(self):
        return """sr: {} sample/sec, duration: {} sec, br: {} b/sec, ch: {} channels, n_s: {} samples""".format(
            self.sampling_rate,
            self.duration,
            self.bit_rate,
            self.channels_count,
            self.num_samples
            )

    def __repr__(self):
        return '''Description({}, {}, {}, {}, {})'''.format(
            self.duration,
            self.bit_rate,
            self.sampling_rate,
            self.channels_count,
            self.num_samples
            )
