# TODO - implement basic funcions for opening, reading,
# seeking data, etc. in files, being them binary or textual.

# Will need a blocksize parameter for the binary case
# The textual case is trivial, reads line by line

from typing import IO, Union, Optional
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
    def read(self, n: int) -> Union[str, bytes]:
        """
        Reads a line for extracting information following
        the given fields.

        :param n: The number of bytes to be read
        :type n: int
        :return: The extracted data
        :rtype: str | bytes
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def file(self) -> IO:
        raise NotImplementedError
