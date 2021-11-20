from dataclasses import dataclass


@dataclass
class Description:
    duration: float
    bit_rate: int
    sampling_rate: int

    @property
    def number_of_samples(self) -> int:
        return int(self.sampling_rate * self.duration)

    def __str__(self):
        return '''sr: {} sample/sec, duration: {} sec, br: {} kb/sec'''.format(
            self.sampling_rate,
            self.duration,
            self.bit_rate
            )

    def __repr__(self):
        return '''Description({}, {}, {})'''.format(
            self.duration,
            self.bit_rate,
            self.sampling_rate
            )
