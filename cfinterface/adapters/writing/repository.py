# TODO - implement basic funcions for opening, reading,
# seeking data, etc. in files, being them binary or textual.

# Will need a blocksize parameter for the binary case
# The textual case is trivial, reads line by line

from typing import IO, BinaryIO, TextIO, Union, Optional, Dict, Type
from abc import ABC, abstractmethod


class Repository(ABC):
    def __init__(self, path: str, encoding: Optional[str]) -> None:
        self._path = path
        self._encoding = encoding

    def __enter__(self) -> "Repository":
        return self

    def __exit__(self, *args):
        pass

    @abstractmethod
    def write(self, data: Union[str, bytes]):
        """
        Writes an amount of information to a file.

        :param data: The number of bytes to be read
        :type data: str | bytes
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def file(self) -> IO:
        raise NotImplementedError


class BinaryRepository(Repository):
    def __init__(self, path: str) -> None:
        super().__init__(path, None)
        self._filepointer: BinaryIO = None  # type: ignore

    def __enter__(self):
        self._filepointer = open(self._path, "wb")
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._filepointer.close()

    def write(self, data: Union[str, bytes]):
        """
        Writes an amount of information to a file.

        :param data: The bytes to be written
        :type data: str | bytes
        """
        if isinstance(data, bytes):
            self._filepointer.write(data)

    @property
    def file(self) -> BinaryIO:
        return self._filepointer


class TextualRepository(Repository):
    def __init__(self, path: str, encoding: str) -> None:
        super().__init__(path, encoding)
        self._filepointer: TextIO = None  # type: ignore

    def __enter__(self):
        self._filepointer = open(self._path, "w", encoding=self._encoding)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._filepointer.close()

    def write(self, data: Union[str, bytes]):
        """
        Writes an amount of information to a file.

        :param data: The data to be written
        :type data: str | bytes
        """
        if isinstance(data, str):
            self._filepointer.write(data)

    @property
    def file(self) -> TextIO:
        return self._filepointer


def factory(kind: str) -> Type[Repository]:
    mappings: Dict[str, Type[Repository]] = {
        "TEXT": TextualRepository,
        "BINARY": BinaryRepository,
    }
    return mappings.get(kind, TextualRepository)
