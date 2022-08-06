from typing import Type
from os.path import join

from cfinterface.data.blockdata import BlockData
from cfinterface.adapters.writing.repository import Repository
from cfinterface.adapters.writing.textualrepository import TextualRepository


class BlockWriting:
    """
    Class for writing custom files based on a BlockData structure.
    """

    def __init__(
        self,
        data: BlockData,
        repository: Type[Repository] = TextualRepository,
    ) -> None:
        self.__data = data
        self.__repository = repository
        self.__interface: Repository = None  # type: ignore

    def __write_file(self):
        """
        Writes all the blocks from the given BlockData structure
        to the specified file.

        """
        for b in self.__data:
            b.write(self.__interface.file)

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
        self.__interface = self.__repository(filepath, encoding)
        with self.__interface:
            return self.__write_file()

    @property
    def data(self) -> BlockData:
        return self.__data
