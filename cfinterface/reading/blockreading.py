from typing import List, Type, Union
from os.path import join

from cfinterface.components.block import Block
from cfinterface.components.defaultblock import DefaultBlock
from cfinterface.data.blockdata import BlockData

from cfinterface.adapters.reading.repository import Repository, factory


class BlockReading:
    """
    Class for reading custom files based on a BlockData structure.
    """

    def __init__(
        self,
        allowed_blocks: List[Type[Block]],
        storage: str = "",
        linesize: int = 1,
    ) -> None:
        self.__allowed_blocks = allowed_blocks
        self.__data = BlockData(DefaultBlock(data=""))
        self.__last_position_filepointer = 0
        self.__storage = storage
        self.__repository: Repository = None  # type: ignore
        self.__linesize = linesize

    def __read_line_with_backup(self) -> Union[str, bytes]:
        """
        Reads a line of information from a file,
        saving the filepointer position in case one desired to return
        to the previous line.

        :return: The read line
        :rtype: str | bytes
        """
        self.__last_position_filepointer = self.__repository.file.tell()
        return self.__repository.read(self.__linesize)

    def __restore_previous_line(self):
        """
        Restores the filepointer to the beginning of the previously
        read line.
        """
        self.__repository.file.seek(self.__last_position_filepointer)

    def __find_starting_block(
        self, blockdata: Union[str, bytes]
    ) -> Type[Block]:
        """
        Searches among the given blocks for the block that begins in
        a certain position of the reading file.

        :param blockdata: A portion of data in the reading file
        :type blockdata: str | bytes
        :return: The block type that begins on the given blockdata
        :rtype: Type[Block]
        """
        for b in self.__allowed_blocks:
            if b.begins(blockdata):
                return b
        return DefaultBlock

    def __read_file(self) -> BlockData:
        """
        Reads all the blocks from the given blocks in a file and
        returns the BlockData structure.

        :return: The block data from the file
        :rtype: BlockData
        """
        while True:
            line = self.__read_line_with_backup()
            if len(line) == 0:
                break
            self.__restore_previous_line()
            blocktype = self.__find_starting_block(line)
            block = blocktype()
            block.read(self.__repository.file)
            self.__data.append(block)
        return self.__data

    def read(self, filename: str, directory: str, encoding: str) -> BlockData:
        """
        Reads a file with a given name in a given directory and
        extracts the data from the specified blocks.

        :param filename: The name of the file
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        :param encoding: The encoding for reading the file
        :type encoding: str
        :return: The data from the blocks found in the file
        :rtype: BlockData
        """
        filepath = join(directory, filename)
        self.__repository = factory(self.__storage)(filepath, encoding)
        with self.__repository:
            return self.__read_file()

    @property
    def data(self) -> BlockData:
        return self.__data

    @property
    def empty(self) -> bool:
        return len(self.__data) == 1
