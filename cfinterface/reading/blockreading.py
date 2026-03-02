from os.path import isfile
from typing import Any

from cfinterface.adapters.reading.repository import Repository, factory
from cfinterface.components.block import Block
from cfinterface.components.defaultblock import DefaultBlock
from cfinterface.data.blockdata import BlockData
from cfinterface.storage import StorageType


class BlockReading:
    """
    Class for reading custom files based on a BlockData structure.
    """

    __slots__ = [
        "__allowed_blocks",
        "__data",
        "__last_position_filepointer",
        "__storage",
        "__linesize",
        "__repository",
    ]

    def __init__(
        self,
        allowed_blocks: list[type[Block]],
        storage: str | StorageType = "",
        linesize: int = 1,
    ) -> None:
        self.__allowed_blocks = allowed_blocks
        self.__data = BlockData(DefaultBlock(data=""))
        self.__last_position_filepointer = 0
        self.__storage = storage
        self.__repository: Repository = None  # type: ignore
        self.__linesize = linesize

    def __read_line_with_backup(self) -> str | bytes:
        self.__last_position_filepointer = self.__repository.file.tell()
        return self.__repository.read(self.__linesize)

    def __restore_previous_line(self) -> None:
        self.__repository.file.seek(self.__last_position_filepointer)

    def __find_starting_block(
        self, blockdata: str | bytes
    ) -> "type[Block]":
        for b in self.__allowed_blocks:
            if b.begins(blockdata):
                return b
        return DefaultBlock

    def __read_file(self, *args: Any, **kwargs: Any) -> BlockData:
        while True:
            line = self.__read_line_with_backup()
            if len(line) == 0:
                break
            self.__restore_previous_line()
            blocktype = self.__find_starting_block(line)
            block = blocktype()
            block.read(self.__repository.file, *args, **kwargs)
            self.__data.append(block)
        return self.__data

    def read(
        self,
        content: str | bytes,
        encoding: str,
        *args: Any,
        **kwargs: Any,
    ) -> BlockData:
        """
        Reads a file in a given path and
        extracts the data from the specified blocks.

        :param content: The file name in disk or the file contents
        :type content: str | bytes
        :param encoding: The encoding for reading the file
        :type encoding: str
        :return: The data from the blocks found in the file
        :rtype: BlockData
        """
        self.__repository = factory(self.__storage)(
            content, not isfile(content), encoding
        )
        with self.__repository:
            return self.__read_file(*args, **kwargs)

    @property
    def data(self) -> BlockData:
        return self.__data

    @property
    def empty(self) -> bool:
        return len(self.__data) == 1
