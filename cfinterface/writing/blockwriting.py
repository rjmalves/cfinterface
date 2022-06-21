from typing import IO
from os.path import join

from cfinterface.data.blockdata import BlockData


class BlockWriting:
    """
    Class for writing custom files based on a BlockData structure.
    """

    def __init__(self, data: BlockData) -> None:
        self.__data = data

    def __write_file(self, file: IO):
        """
        Writes all the blocks from the given BlockData structure
        to the specified file.

        :param file: The filepointer
        :type file: IO
        """
        for b in self.__data:
            b.write(file)

    def write(self, filename: str, directory: str, encoding: str):
        """
        Writes a file with a given name in a given directory with
        the data from the BlockData structure.

        :param filename: The name of the file
        :type filename: str
        :param directory: The directory where the file will be
        :type directory: str
        :param encoding: The encoding for reading the file
        :type encoding: str
        """
        filepath = join(directory, filename)
        with open(filepath, "w", encoding=encoding) as fp:
            return self.__write_file(fp)

    @property
    def data(self) -> BlockData:
        return self.__data
