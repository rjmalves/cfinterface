from typing import IO, List, Type
from os.path import join

from cfinterface.components.block import Block
from cfinterface.components.defaultblock import DefaultBlock
from cfinterface.data.blockdata import BlockData


class BlockReading:
    """
    Class for reading custom files based on a BlockData structure.
    """

    def __init__(self, allowed_blocks: List[Type[Block]]) -> None:
        self.__allowed_blocks = allowed_blocks
        self.__data = BlockData(DefaultBlock(data=""))
        self.__last_position_filepointer = 0

    def __read_line_with_backup(self, file: IO) -> str:
        """
        Reads a line of the file, saving the filepointer position
        in case one desired to return to the previous line.

        :param file: THe filepoiner for the reading file
        :type file: IO
        :return: The read line
        :rtype: str
        """
        self.__last_position_filepointer = file.tell()
        return file.readline()

    def __restore_previous_line(self, file: IO):
        """
        Restores the filepointer to the beginning of the previously
        read line.

        :param file: The filepointer
        :type file: IO
        """
        file.seek(self.__last_position_filepointer)

    def __find_starting_block(self, line: str) -> Type[Block]:
        """
        Searches among the given blocks for the block that begins in
        a line of the reading file.

        :param line: A line of the reading file
        :type line: str
        :return: The block type that begins on the given line
        :rtype: Type[Block]
        """
        for b in self.__allowed_blocks:
            if b.begins(line):
                return b
        return DefaultBlock

    def __read_file(self, file: IO) -> BlockData:
        """
        Reads all the blocks from the given blocks in a file and
        returns the BlockData structure.

        :param file: The filepointer
        :type file: IO
        :return: The block data from the file
        :rtype: BlockData
        """
        while True:
            line = self.__read_line_with_backup(file)
            if len(line) == 0:
                break
            self.__restore_previous_line(file)
            blocktype = self.__find_starting_block(line)
            block = blocktype()
            block.read(file)
            self.__data.append(block)
        return self.__data

    def read(self, filename: str, directory: str) -> BlockData:
        """
        Reads a file with a given name in a given directory and
        extracts the data from the specified blocks.

        :param filename: The name of the file
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        :return: The data from the blocks found in the file
        :rtype: BlockData
        """
        filepath = join(directory, filename)
        with open(filepath, "r") as fp:
            return self.__read_file(fp)

    @property
    def data(self) -> BlockData:
        return self.__data

    @property
    def empty(self) -> bool:
        return len(self.__data) == 1
