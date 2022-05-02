from typing import IO
from os.path import join

from cfinterface.data.sectiondata import SectionData


class SectionWriting:
    """
    Class for writing custom files based on a SectionData structure.
    """

    def __init__(self, data: SectionData) -> None:
        self.__data = data

    def __write_file(self, file: IO):
        """
        Writes all the registers from the given SectionData structure
        to the specified file.

        :param file: The filepointer
        :type file: IO
        """
        for s in self.__data:
            s.write(file)

    def write(self, filename: str, directory: str):
        """
        Writes a file with a given name in a given directory with
        the data from the SectionData structure.

        :param filename: The name of the file
        :type filename: str
        :param directory: The directory where the file will be
        :type directory: str
        """
        filepath = join(directory, filename)
        with open(filepath, "w") as fp:
            return self.__write_file(fp)

    @property
    def data(self) -> SectionData:
        return self.__data
