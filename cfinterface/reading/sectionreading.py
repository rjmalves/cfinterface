from typing import IO, List, Type
from os.path import join

from cfinterface.components.section import Section
from cfinterface.components.defaultsection import DefaultSection
from cfinterface.data.sectiondata import SectionData


class SectionReading:
    """
    Class for reading custom files based on a SectionData structure.
    """

    def __init__(self, sections: List[Type[Section]]) -> None:
        self.__sections = sections
        self.__data = SectionData(DefaultSection(data=""))
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

    def __read_file(self, file: IO) -> SectionData:
        """
        Reads all the sections from a file and
        returns the SectionData structure.

        :param file: The filepointer
        :type file: IO
        :return: The section data from the file
        :rtype: SectionData
        """
        for sectiontype in self.__sections:
            section = sectiontype()
            section.read(file)
            self.__data.append(section)
        while True:
            line = self.__read_line_with_backup(file)
            if len(line) == 0:
                break
            self.__restore_previous_line(file)
            section = DefaultSection()
            section.read(file)
            self.__data.append(section)
        return self.__data

    def read(self, filename: str, directory: str) -> SectionData:
        """
        Reads a file with a given name in a given directory and
        extracts the data from the specified sections.

        :param filename: The name of the file
        :type filename: str
        :param directory: The directory where the file is
        :type directory: str
        :return: The data from the sections found in the file
        :rtype: SectionData
        """
        filepath = join(directory, filename)
        with open(filepath, "r") as fp:
            return self.__read_file(fp)

    @property
    def data(self) -> SectionData:
        return self.__data

    @property
    def empty(self) -> bool:
        return len(self.__data) == 1
