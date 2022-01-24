from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Union
from pathlib import Path
from .exceptions import FileNotFoundError
import os


class IAudioDescriber(ABC):
    @abstractmethod
    def get_duration():
        """Get the duration for the given file

        Returns:
                returns the duration of the file as float number or None
                incase the file is corrupted
        """
        pass

    @abstractmethod
    def get_sampling_rate():
        """Get the sampling rate for the given file

        Returns:
                returns the sampling rate of the file as an integer or None
                incase the file is corrupted
        """
        pass

    @abstractmethod
    def get_bit_rate():
        """Get the bit rate for the given file

        Returns:
                returns the bit rate of the file as an integer or None
                incase the file is corrupted
        """
        pass

    @abstractmethod
    def get_byte_rate():
        """Get the byte rate for the given file which is the bit_rate / 8

        Returns:
                returns the bit rate of the file as an integer or None
                incase the file is corrupted
        """
        pass

    @abstractmethod
    def get_channels_count():
        """Get the number of channels for the given file

        Returns:
                returns the number of channels of the file as an
                integer or None incase the file is corrupted
        """
        pass

    @abstractmethod
    def get_num_samples():
        """Get the total number of samples for the given file

        Returns:
                returns the total number of samples of the file as an
                integer or None incase the file is corrupted
        """
        pass

    @abstractmethod
    def describe():
        """Get a describtion about the given file
        """
        pass


class Content(Sequence):
    def __init__(
            self,
            file_path:
            Union[str, Path],
            start: int,
            end: int
            ) -> None:
        self.data = self._load(file_path, start, end)

    def _load(self, file_path: str, start: int, end: int) -> bytes:
        """This function is used to load the bytes data from the
        given target file

        Args:
            file_path (str): the target file to read the data from
            start (int): where to start reading from
            end (int): where to stop the reading
        """
        if os.path.exists(file_path) is False:
            raise FileNotFoundError(file_path)
        with open(file=file_path, mode='rb+') as f:
            _ = f.seek(start)
            data = f.read(end)
        return data

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> bytes:
        return self.data[idx]

    def find(self, match: Union[hex, str, bytes], start_idx=0) -> Union[None, int]:
        """sed to find a match in the file's content if found it returns the 
        starting idx if not returns None

        Args:
            match (Union[hex, str, bytes]): the exact subvalue to be found in 
            the file's bytes contents
            start_idx (int, optional): the starting index to start looking from.
            Defaults to 0.
        """
        result = self.data.find(match, start_idx)
        return None if result == -1 else result