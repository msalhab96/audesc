from .utils import get_file_extension


class FileNotFoundError(Exception):
    def __init__(self, file_path: str) -> None:
        msg = f'{file_path} is not found!'
        super().__init__(msg)


class NotImplemented(Exception):
    def __init__(self) -> None:
        msg = 'This feature is not implemented yet!'
        super().__init__(msg)


class CorruptedFileError(Exception):
    def __init__(self, file_path: str) -> None:
        extension = get_file_extension(file_path)
        msg = f'{file_path} is corrupted or does \
            not follow {extension} file structire'
        super().__init__(msg)
