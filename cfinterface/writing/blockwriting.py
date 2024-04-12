from typing import Union, IO
from cfinterface.data.blockdata import BlockData
from cfinterface.adapters.writing.repository import (
    Repository,
    factory,
)


class BlockWriting:
    """
    Class for writing custom files based on a BlockData structure.
    """

    __slots__ = [
        "__data",
        "__storage",
        "__repository",
    ]

    def __init__(self, data: BlockData, storage: str = "") -> None:
        self.__data = data
        self.__storage = storage
        self.__repository: Repository = None  # type: ignore

    def __write_file(self, *args, **kwargs):
        """
        Writes all the blocks from the given BlockData structure
        to the specified file.

        """
        for b in self.__data:
            b.write(self.__repository.file, *args, **kwargs)

    def write(self, to: Union[str, IO], encoding: str, *args, **kwargs):
        """
        Writes a file with a given name in a given directory with
        the data from the BlockData structure.

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
    def data(self) -> BlockData:
        return self.__data
