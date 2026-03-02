from typing import IO, Any

from cfinterface.adapters.writing.repository import (
    Repository,
    factory,
)
from cfinterface.data.sectiondata import SectionData
from cfinterface.storage import StorageType


class SectionWriting:
    """
    Class for writing custom files based on a SectionData structure.
    """

    __slots__ = [
        "__data",
        "__storage",
        "__repository",
    ]

    def __init__(
        self, data: SectionData, storage: str | StorageType = ""
    ) -> None:
        self.__data = data
        self.__storage = storage
        self.__repository: Repository = None  # type: ignore

    def __write_file(self, *args: Any, **kwargs: Any) -> None:
        for s in self.__data:
            s.write(self.__repository.file, *args, **kwargs)

    def write(
        self,
        to: str | IO[Any],
        encoding: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Writes to a file with a given name in a given directory or
        to a buffer with the data from the SectionData structure.

        :param to: The writing destination, being a string for writing
            to a file or the IO buffer
        :type to: str | IO
        :param encoding: The encoding for reading the file
        :type encoding: str
        """
        self.__repository = factory(self.__storage)(to, encoding)
        with self.__repository:
            return self.__write_file(*args, **kwargs)

    @property
    def data(self) -> SectionData:
        return self.__data
